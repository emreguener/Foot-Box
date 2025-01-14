from flask import Flask, request, render_template, session, redirect, url_for
import random
import pandas as pd

app = Flask(__name__)
app.secret_key = 'secret_key'

# Veri setini yükle ve piyasa değerlerini normalize et
raw_data = pd.read_csv("fenerbahçe_oyuncular.csv")
def normalize_market_value(value):
    if 'mil.' in value:
        return float(value.replace(' mil. €', ''))
    elif 'bin' in value:
        return float(value.replace(' bin €', '')) / 1000
    else:
        return 0.0

data = raw_data.copy()
data['Piyasa Değeri'] = data['Piyasa Değeri'].apply(normalize_market_value)

def select_random_player(excluded_players):
    # Oyuncu seçimi için filtre uygula
    available_players = data[~data['Oyuncu İsmi'].isin(excluded_players)]
    return available_players.sample(1).iloc[0]

@app.route('/')
def index():
    # Yeni oyun başlat
    if 'current_round' not in session or 'excluded_players' not in session:
        session['results'] = []  # Sonuçları sıfırla
        session['attempts_left'] = 3  # Her oyuncu için kalan tahmin hakkı
        session['excluded_players'] = []  # Çıkan oyuncular listesi
        session['current_player'] = select_random_player(session['excluded_players']).to_dict()
        session['current_round'] = 1  # İlk roundu başlat
    return render_template(
        'index.html', 
        player_name=session['current_player']['Oyuncu İsmi'], 
        player_value=session['current_player']['Piyasa Değeri'], 
        attempts_left=session['attempts_left'], 
        feedback="", 
        round_number=session['current_round']
    )

@app.route('/guess', methods=['POST'])
def guess():
    guessed_value = float(request.form['guessed_value'])
    true_value = session['current_player']['Piyasa Değeri']
    attempts_left = session['attempts_left'] - 1
    session['attempts_left'] = attempts_left
    feedback = ""

    if guessed_value == true_value:
        feedback = "Doğru bildiniz!"
        attempts_left = 0
    elif guessed_value < true_value:
        feedback = "Daha yüksek bir değer girin."
    else:
        feedback = "Daha düşük bir değer girin."

    if attempts_left == 0:
        # Sonuçları kaydet
        session['results'].append({
            'Oyuncu İsmi': session['current_player']['Oyuncu İsmi'],
            'Gerçek Değer': true_value,
            'Son Tahmin': guessed_value,
            'Fark': abs(true_value - guessed_value)
        })

        # Oyuncuyu çıkarılanlar listesine ekle
        session['excluded_players'].append(session['current_player']['Oyuncu İsmi'])

        # Eğer 10 oyuncu tamamlandıysa, sonucu göster
        if session['current_round'] == 10:
            return redirect(url_for('summary'))

        # Geçici sonuç gösterimi
        session['temp_feedback'] = f"Sizin tahmininiz: {guessed_value} milyon Euro. Gerçek değer: {true_value} milyon Euro. Fark: {abs(true_value - guessed_value):.2f} milyon Euro."
        return redirect(url_for('temp_result'))

    return render_template(
        'index.html', 
        player_name=session['current_player']['Oyuncu İsmi'], 
        player_value=session['current_player']['Piyasa Değeri'], 
        feedback=feedback, 
        attempts_left=session['attempts_left'], 
        round_number=session['current_round']
    )

@app.route('/temp_result')
def temp_result():
    # Geçici sonuç gösteriminden sonra yeni rounda geç
    feedback = session.pop('temp_feedback', "")
    session['current_round'] += 1
    session['current_player'] = select_random_player(session['excluded_players']).to_dict()
    session['attempts_left'] = 3
    return render_template('temp_result.html', feedback=feedback, round_number=session['current_round'])

@app.route('/summary')
def summary():
    return render_template('summary.html', results=session['results'])

if __name__ == '__main__':
    app.run(debug=True)
