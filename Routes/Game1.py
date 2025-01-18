from flask import Blueprint, Flask, request, render_template, session, redirect, url_for
import random
import pandas as pd
import os
game1_bp = Blueprint('game1_bp', __name__)


# BASE_DIR, "Routes" klasöründen bir üst dizine çıkmalı
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Foot-Box klasörüne çıkar

# CSV dosyasının tam yolu
CSV_PATH = os.path.join(BASE_DIR, "CSV Files", "TümOyuncular1.csv")

# Dosyanın gerçekten var olup olmadığını kontrol et
if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(f"CSV dosyası bulunamadı: {CSV_PATH}")

# CSV dosyasını oku
raw_data = pd.read_csv(CSV_PATH, encoding='utf-8')

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

@game1_bp.route('/game1')
def index():
    # Yeni oyun başlat
    if 'current_round' not in session or 'excluded_players' not in session:
        session['results'] = []  # Sonuçları sıfırla
        session['attempts_left'] = 3  # Her oyuncu için kalan tahmin hakkı
        session['excluded_players'] = []  # Çıkan oyuncular listesi
        session['current_player'] = select_random_player(session['excluded_players']).to_dict()
        session['current_round'] = 1  # İlk roundu başlat
    return render_template(
        'game1.html', 
        player_name=session['current_player']['Oyuncu İsmi'], 
        player_value=session['current_player']['Piyasa Değeri'], 
        attempts_left=session['attempts_left'], 
        feedback="", 
        round_number=session['current_round']
    )

@game1_bp.route('/game1/guess', methods=['POST'])
def guess():
    # Giriş kontrolü
    guessed_value = request.form.get('guessed_value')
    if not guessed_value:
        feedback = "Lütfen bir tahmin değeri girin!"
        return render_template(
            'game1.html', 
            player_name=session['current_player']['Oyuncu İsmi'], 
            feedback=feedback, 
            attempts_left=session['attempts_left'], 
            round_number=session['current_round']
        )

    try:
        guessed_value = float(guessed_value)
    except ValueError:
        feedback = "Geçerli bir sayı girin!"
        return render_template(
            'game1.html', 
            player_name=session['current_player']['Oyuncu İsmi'], 
            feedback=feedback, 
            attempts_left=session['attempts_left'], 
            round_number=session['current_round']
        )
    
    # Session kontrolü
    if 'current_player' not in session or 'current_round' not in session:
        return redirect(url_for('game1_bp.index'))

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
        session['results'].append({
            'Oyuncu İsmi': session['current_player']['Oyuncu İsmi'],
            'Gerçek Değer': true_value,
            'Son Tahmin': guessed_value,
            'Fark': abs(true_value - guessed_value)
        })
        session['excluded_players'].append(session['current_player']['Oyuncu İsmi'])

        if session['current_round'] == 10:
            return redirect(url_for('game1_bp.summary'))

        session['temp_feedback'] = f"Sizin tahmininiz: {guessed_value} milyon Euro. Gerçek değer: {true_value} milyon Euro. Fark: {abs(true_value - guessed_value):.2f} milyon Euro."
        return redirect(url_for('game1_bp.temp_result'))

    return render_template(
        'game1.html', 
        player_name=session['current_player']['Oyuncu İsmi'], 
        feedback=feedback, 
        attempts_left=session['attempts_left'], 
        round_number=session['current_round']
    )
@game1_bp.route('/game1/temp_result')
def temp_result():
    # Geçici sonuç gösteriminden sonra yeni rounda geç
    feedback = session.pop('temp_feedback', "")
    session['current_round'] += 1
    session['current_player'] = select_random_player(session['excluded_players']).to_dict()
    session['attempts_left'] = 3
    return render_template('temp_result.html', feedback=feedback, round_number=session['current_round'])

@game1_bp.route('/game1/summary')
def summary():
    return render_template('summary.html', results=session['results'])

