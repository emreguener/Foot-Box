from flask import Blueprint, render_template, request, session, redirect, url_for
import pandas as pd
import os

# Blueprint tanımı
game2_bp = Blueprint('game2_bp', __name__)

# CSV dosya yolu
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Foot-Box klasörüne çıkar
CSV_PATH = os.path.join(BASE_DIR, "CSV Files", "TümOyuncular1.csv")

if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(f"CSV dosyası bulunamadı: {CSV_PATH}")

# CSV dosyasını oku
new_df2 = pd.read_csv(CSV_PATH, encoding='utf-8')

def normalize_market_value(value):
    if isinstance(value, str):
        if 'mil.' in value:
            return float(value.replace(' mil. €', ''))
        elif 'bin' in value:
            return float(value.replace(' bin €', '')) / 1000
    return 0.0

new_df2['Piyasa Değeri'] = new_df2['Piyasa Değeri'].apply(normalize_market_value)

@game2_bp.route('/game2')
def index():
    if 'tur' not in session:
        session['skor'] = 0
        session['tur'] = 1
        session['oyuncular'] = new_df2.sample(5).reset_index(drop=True).to_dict(orient='records')
        session['tur_ozet'] = []  # Her turun sonucunu tutacak liste

    return render_template(
        'game2.html',
        oyuncular=session['oyuncular'],
        skor=session['skor'],
        tur=session['tur']
    )

@game2_bp.route('/game2/submit', methods=['POST'])
def submit_sort_by():
    if 'tur' not in session or session['tur'] > 10:
        return redirect(url_for('game2_bp.sonuclar'))  # Eğer 10 tur bittiyse sonuçları göster

    # Eğer 'tur_ozet' session içinde tanımlı değilse, onu oluştur
    if 'tur_ozet' not in session:
        session['tur_ozet'] = []

    siralama = request.form.get('siralama')
    if not siralama:
        return render_template(
            'game2.html',
            oyuncular=session['oyuncular'],
            skor=session['skor'],
            tur=session['tur'],
            message="<div class='error-box'>⚠️ Lütfen bir sıralama girin!</div>"
        )

    try:
        kullanici_sirasi = [int(i) - 1 for i in siralama.split(',')]
        oyuncular_df = pd.DataFrame(session['oyuncular'])
        dogru_siralama = oyuncular_df.sort_values(by="Piyasa Değeri", ascending=False).reset_index(drop=True)
        kullanici_siralamasi = oyuncular_df.iloc[kullanici_sirasi].reset_index(drop=True)

        if kullanici_siralamasi.equals(dogru_siralama):
            session['skor'] += 1
            sonuc = "✅ Doğru"
        else:
            session['skor'] -= 1
            sonuc = "❌ Yanlış"

        # Tur özetini kaydet
        session['tur_ozet'].append({
            "tur": session['tur'],
            "oyuncular": [f"{o['Oyuncu İsmi']} ({o['Piyasa Değeri']} Mil. €)" for o in session['oyuncular']],
            "dogru_siralama": [f"{o} ({p} Mil. €)" for o, p in zip(dogru_siralama["Oyuncu İsmi"], dogru_siralama["Piyasa Değeri"])],
            "kullanici_siralama": [f"{o} ({p} Mil. €)" for o, p in zip(kullanici_siralamasi["Oyuncu İsmi"], kullanici_siralamasi["Piyasa Değeri"])],
            "sonuc": sonuc
        })

        # Tur sayısı 10'u geçtiyse sonuçları göster
        if session['tur'] >= 10:
            return redirect(url_for('game2_bp.sonuclar'))

        # Yeni tur
        session['tur'] += 1
        session['oyuncular'] = new_df2.sample(5).reset_index(drop=True).to_dict(orient='records')

        return render_template(
            'game2.html',
            oyuncular=session['oyuncular'],
            skor=session['skor'],
            tur=session['tur'],
            message=f"""
                <div class='{"success-box" if "✅" in sonuc else "error-box"}'>
                    <p><strong>{sonuc}</strong></p>
                    <p><strong>Senin Sıralaman:</strong> {", ".join(session['tur_ozet'][-1]['kullanici_siralama'])}</p>
                    <p><strong>Doğru Sıralama:</strong> {", ".join(session['tur_ozet'][-1]['dogru_siralama'])}</p>
                </div>
            """
        )

    except ValueError as e:
        return render_template(
            'game2.html',
            oyuncular=session['oyuncular'],
            skor=session['skor'],
            tur=session['tur'],
            message=f"<div class='error-box'>Hata: {str(e)}</div>"
        )

@game2_bp.route('/game2/sonuclar')
def sonuclar():
    if 'tur_ozet' not in session:
        return redirect(url_for('game2_bp.index'))  # Eğer özet yoksa yeni oyun başlat

    # Sonuçları al, çünkü session'ı sıfırlayacağız
    tur_ozet = session['tur_ozet']
    skor = session['skor']

    # Oyun tamamen bittiği için session'ı sıfırla
    session.clear()

    return render_template(
        'game2_sonuclar.html',
        tur_ozet=tur_ozet,
        skor=skor
    )


@game2_bp.route('/game2/yeni_oyun')
def yeni_oyun():
    # Yeni bir oyun başlat, tüm session değişkenlerini sıfırla
    session.clear()
    session['skor'] = 0
    session['tur'] = 1
    session['oyuncular'] = new_df2.sample(5).reset_index(drop=True).to_dict(orient='records')
    session['tur_ozet'] = []  # Yeni oyun için sıfırdan başlat

    return redirect(url_for('game2_bp.index'))
