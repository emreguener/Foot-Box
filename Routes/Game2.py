from flask import Blueprint, render_template, request, session, redirect, url_for
import pandas as pd
import random

# Blueprint tanımı
game2_bp = Blueprint('game2_bp', __name__)

# Örnek veri
# Burada kendi verinizi kullandığınızda aşağıdaki satırı kaldırabilirsiniz
new_df2 = pd.read_csv("C:\\Users\\batur\\OneDrive\\Masaüstü\\Personal Development\\Codes\\FootBox\\CSV Files\\TümOyuncular1.csv")

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
        siralama = request.form.get('siralama')

        if not kriter or kriter not in ["1", "2"]:
            raise ValueError("Geçersiz kriter!")

        if not siralama:
            raise ValueError("Sıralama bilgisi gönderilmedi!")

        try:
            # Kullanıcı girdisini sıfır tabanlı indekslere çevirin
            kullanici_sirasi = [int(i) - 1 for i in siralama.split(',')]
            if len(kullanici_sirasi) != len(set(kullanici_sirasi)):
                raise ValueError("Sıralamada tekrar eden indeksler var!")
        except ValueError:
            raise ValueError("Sıralama bilgisi yalnızca benzersiz sayılardan oluşmalıdır!")

        # Rastgele seçilen oyuncuları listele
        oyuncular = new_df2.sample(5).reset_index(drop=True)

        if oyuncular.empty:
            raise ValueError("Oyuncu listesi boş!")

        # Kullanıcı tarafından verilen indekslerin doğruluğunu kontrol edin
        if not all(0 <= i < len(oyuncular) for i in kullanici_sirasi):
            raise ValueError(f"Geçersiz sıralama! İndeksler 1 ile {len(oyuncular)} arasında olmalı.")

        # Kullanıcı sıralamasını uygulayın
        kullanici_siralamasi = oyuncular.iloc[kullanici_sirasi]

        # Doğru sıralama kriterine göre sıralayın
        kriter_adi = "Piyasa Değeri (Sayısal)" if kriter == "1" else "Yaş"
        dogru_siralama = oyuncular.sort_values(by=kriter_adi, ascending=(kriter == "2")).reset_index(drop=True)

        # Sıralamaları karşılaştırın
        if kullanici_siralamasi.equals(dogru_siralama):
            skor = session.get('skor', 0) + 1
            session['skor'] = skor
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