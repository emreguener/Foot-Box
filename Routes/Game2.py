from flask import Blueprint, render_template, request, session, redirect, url_for
import pandas as pd
import random

# Blueprint tanımı
game2_bp = Blueprint('game2_bp', __name__)

# Örnek veri
# Burada kendi verinizi kullandığınızda aşağıdaki satırı kaldırabilirsiniz
new_df2 = pd.read_csv("C:\\Users\\batur\\OneDrive\\Masaüstü\\Personal Development\\Codes\\FootBox\\CSV Files\\TümOyuncular.csv")

# Oyun başladığında oturum değişkenlerini ayarla
@game2_bp.route('/game2')
def index():
    skor = session.get('skor', 0)

    # Rastgele 5 oyuncu seç
    oyuncular = new_df2.sample(5).reset_index(drop=True)

    # Kullanıcıya kriter seçimi sun
    return render_template(
        'game2.html',
        oyuncular=oyuncular.to_dict(orient='records'),  # HTML'de kullanılmak üzere oyuncuları dönüştür
        skor=skor
    )

# Kullanıcının sıralama yapması
@game2_bp.route('/game2/submit', methods=['POST'])
def submit_sort_by():
    try:
        # Veriler
        kriter = request.form.get('kriter')
        kullanici_sirasi = list(map(int, request.form.get('siralama').split(',')))

        if kriter not in ["1", "2"]:
            raise ValueError("Geçersiz kriter!")

        # Kriterlere göre sıralama yap
        kriter_adi = "Piyasa Değeri (Sayısal)" if kriter == "1" else "Yaş"

        # Rastgele seçilen oyuncuları listele
        oyuncular = new_df2.sample(5).reset_index(drop=True)

        # Kullanıcının sıralamasını yap
        # Kullanıcı sıralama için girdiği indekslerin geçerli olup olmadığını kontrol et
        if not all(0 <= i < len(oyuncular) for i in kullanici_sirasi):
            raise ValueError("Geçersiz sıralama! Girdiğiniz indeksler geçerli değil.")

        kullanici_siralamasi = oyuncular.iloc[kullanici_sirasi]

        # Doğru sıralama
        dogru_siralama = oyuncular.sort_values(by=kriter_adi, ascending=(kriter == "2")).reset_index(drop=True)

        # Skor kontrolü
        if kullanici_siralamasi.equals(dogru_siralama):
            skor = session.get('skor', 0) + 1
            session['skor'] = skor  # Skoru güncelle
            return render_template(
                'game2.html', 
                oyuncular=oyuncular.to_dict(orient='records'), 
                skor=skor,
                message="Tebrikler! Doğru sıralama yaptınız."
            )
        else:
            return render_template(
                'game2.html', 
                oyuncular=oyuncular.to_dict(orient='records'), 
                skor=session.get('skor', 0),
                message="Yanlış sıralama! Lütfen tekrar deneyin."
            )
    except ValueError as e:
        return render_template(
            'game2.html',
            message=f"Bir hata oluştu: {str(e)}"
        )