from flask import Blueprint, render_template, request, session
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
def index():

    # Skor bilgisini session'dan al
    skor = session.get('skor', 0)
    old_skor = 0
    # Sabit oyuncu rastgele seçilir
    sabit_oyuncu = new_df.sample(1).iloc[0]  

    if request.method == 'POST':
        # Rakip oyuncu rastgele seçilir
        rakip_oyuncu = new_df.sample(1).iloc[0]
        while rakip_oyuncu["Oyuncu İsmi"] == sabit_oyuncu["Oyuncu İsmi"]:
            sabit_oyuncu = new_df.sample(1).iloc[0]

        # Kullanıcının tahminini al
        tahmin = request.form.get('tahmin')

        if tahmin not in ['1', '2']:
            return render_template('game3.html', sabit_oyuncu=sabit_oyuncu, rakip_oyuncu=rakip_oyuncu, skor=skor, message="Geçersiz seçim! Lütfen 1 veya 2 yazın.")

        dogru_cevap = 1 if sabit_oyuncu["Piyasa Değeri (Sayısal)"] > rakip_oyuncu["Piyasa Değeri (Sayısal)"] else 2

        if int(tahmin) == dogru_cevap:
            skor += 1
            session['skor'] = skor
            
            return render_template('game3.html', sabit_oyuncu=sabit_oyuncu, rakip_oyuncu=rakip_oyuncu, skor=skor, message="Doğru tahmin! Skorunuz: " + str(skor))
        else:
            old_skor = skor
            skor = 0
            session['skor'] = skor
            return render_template('game3.html', sabit_oyuncu=sabit_oyuncu, rakip_oyuncu=rakip_oyuncu, skor=skor, message="Yanlış tahmin! Oyun bitti. Son skorunuz: " + str(old_skor))

    # İlk oyun başlangıcında rakip oyuncuyu seç
    rakip_oyuncu = new_df.sample(1).iloc[0]
    while rakip_oyuncu["Oyuncu İsmi"] == sabit_oyuncu["Oyuncu İsmi"]:
        rakip_oyuncu = new_df.sample(1).iloc[0]

    return render_template('game3.html', sabit_oyuncu=sabit_oyuncu, rakip_oyuncu=rakip_oyuncu, skor=skor)
