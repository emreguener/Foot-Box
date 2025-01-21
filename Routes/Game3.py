from flask import Blueprint, render_template, request, session,redirect, url_for
import pandas as pd
import os

# Blueprint tanımı
game3_bp = Blueprint('game3_bp', __name__)

# BASE_DIR, "Routes" klasöründen bir üst dizine çıkmalı
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Foot-Box klasörüne çıkar

# CSV dosyasının tam yolu
CSV_PATH = os.path.join(BASE_DIR, "CSV Files", "TümOyuncular1.csv")

# Dosyanın gerçekten var olup olmadığını kontrol et
if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(f"CSV dosyası bulunamadı: {CSV_PATH}")

# CSV dosyasını oku
new_df = pd.read_csv(CSV_PATH, encoding='utf-8')

# Oyun başladığında oturum değişkenlerini ayarla
@game3_bp.route('/game3', methods=['GET', 'POST'])
def game3():
    # Skor bilgisini session'dan al
    skor = session.get('skor', 0)

    if request.method == 'POST':
        # Kullanıcının tahminini al
        tahmin = request.form.get('tahmin')

        # İki rastgele oyuncuyu session'dan al
        oyuncu1 = session.get('oyuncu1')
        oyuncu2 = session.get('oyuncu2')

        if not oyuncu1 or not oyuncu2:
            return redirect(url_for('game3_bp.game3'))  # Session'da oyuncular yoksa yeniden yükle

        oyuncu1_degeri = float(oyuncu1["Piyasa Değeri (Sayısal)"])
        oyuncu2_degeri = float(oyuncu2["Piyasa Değeri (Sayısal)"])

        # Doğru cevabı hesapla
        dogru_cevap = 1 if oyuncu1_degeri > oyuncu2_degeri else 2

        if int(tahmin) == dogru_cevap:
            # Doğru tahmin: Skoru artır
            skor += 1
            session['skor'] = skor
            message = "Doğru tahmin! Skorunuz: " + str(skor)
        else:
            # Yanlış tahmin: Skoru sıfırla
            old_skor = skor
            skor = 0
            session['skor'] = skor
            message = "Yanlış tahmin! Oyun bitti. Son skorunuz: " + str(old_skor)

        # Yeni oyuncular seç ve sayfayı yenile
        oyuncular = new_df.sample(2).reset_index(drop=True)
        oyuncu1 = oyuncular.iloc[0].to_dict()
        oyuncu2 = oyuncular.iloc[1].to_dict()

        session['oyuncu1'] = oyuncu1
        session['oyuncu2'] = oyuncu2

        return render_template(
            'game3.html',
            oyuncu1=oyuncu1,
            oyuncu2=oyuncu2,
            skor=skor,
            message=message
        )

    # İlk GET isteğinde iki rastgele oyuncu seçilir
    oyuncular = new_df.sample(2).reset_index(drop=True)
    oyuncu1 = oyuncular.iloc[0].to_dict()
    oyuncu2 = oyuncular.iloc[1].to_dict()

    # Oyuncuları session'a kaydet
    session['oyuncu1'] = oyuncu1
    session['oyuncu2'] = oyuncu2

    return render_template(
        'game3.html',
        oyuncu1=oyuncu1,
        oyuncu2=oyuncu2,
        skor=skor,
        message=None
    )