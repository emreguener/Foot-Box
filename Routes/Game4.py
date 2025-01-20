from flask import Blueprint, Flask, request, render_template, session, redirect, url_for
import random
import pandas as pd
import os

# Blueprint tanımlaması
memory_game_bp = Blueprint('memory_game_bp', __name__)

# BASE_DIR, "Routes" klasöründen bir üst dizine çıkmalı
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# CSV dosyasının tam yolu
CSV_PATH = os.path.join(BASE_DIR, "CSV Files", "TümOyuncular1.csv")

# Dosyanın mevcutluğunu kontrol et
if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(f"CSV dosyası bulunamadı: {CSV_PATH}")

# CSV dosyasını oku
raw_data = pd.read_csv(CSV_PATH, encoding='utf-8')

# Oyuncuların isimlerini çıkart
player_names = raw_data['Oyuncu İsmi'].tolist()

def create_memory_board(card_number):
    # Oyunculardan rastgele bir kart seti seç
    if card_number > len(player_names):
        raise ValueError("Card number is greater than available player names")

    selected_players = random.sample(player_names, card_number)
    cards = selected_players + selected_players  # Çift kartlar
    random.shuffle(cards)  # Kartları karıştır

    # Kart matrisini oluştur
    board_size = int(len(cards) ** 0.5)  # Kare matris boyutunu hesapla
    board = [cards[i:i + board_size] for i in range(0, len(cards), board_size)]

    return board

@memory_game_bp.route('/memory_game', methods=['GET', 'POST'])
def memory_game():
    if request.method == 'POST':
        try:
            card_number = int(request.form.get('card_number'))
            if card_number % 2 != 0:
                return render_template('memory_game.html', feedback="Lütfen çift sayı girin!")

            board = create_memory_board(card_number)

            # Gizli kartlar boardı
            hidden_board = [['*' for _ in row] for row in board]

            session['board'] = board
            session['hidden_board'] = hidden_board
            session['matched_cards'] = 0
            session['moves'] = []  # Hamle kaydı
        except ValueError:
            return render_template('memory_game.html', feedback="Geçerli bir sayı girin!")

    return render_template('memory_game.html', hidden_board=session.get('hidden_board', []))

@memory_game_bp.route('/memory_game/init', methods=['POST'])
def init_game():
    try:
        card_number = int(request.form.get('card_number'))
        if card_number % 2 != 0:
            return render_template('memory_game.html', 
                                feedback="Lütfen çift sayı girin!")
        
        # Her bir çift için bir sayı alıyoruz, bu yüzden input'u ikiye bölüyoruz
        board = create_memory_board(card_number)
        hidden_board = [['*' for _ in row] for row in board]
        
        session['board'] = board
        session['hidden_board'] = hidden_board
        session['matched_cards'] = 0
        session['moves'] = []
        session['last_revealed'] = None
        session['feedback'] = "Oyun başladı! Kartları eşleştirmeye başlayın."
        
        return redirect(url_for('memory_game_bp.memory_game'))
        
    except ValueError:
        return render_template('memory_game.html', 
                             feedback="Geçerli bir sayı girin!")

@memory_game_bp.route('/memory_game/guess', methods=['POST'])
def make_guess():
    try:
        row1 = int(request.form.get('row1'))
        col1 = int(request.form.get('col1'))
        row2 = int(request.form.get('row2'))
        col2 = int(request.form.get('col2'))

        board = session['board']
        hidden_board = session['hidden_board']

        # Aynı kart kontrolü
        if (row1 == row2) and (col1 == col2):
            return render_template('memory_game.html', hidden_board=hidden_board, feedback="Aynı kartı iki kez seçemezsiniz!", revealed_board=board)

        # Kartları aç
        card1 = board[row1][col1]
        card2 = board[row2][col2]

        hidden_board[row1][col1] = card1
        hidden_board[row2][col2] = card2

        session['hidden_board'] = hidden_board

        if card1 == card2:
            session['matched_cards'] += 1
            feedback = "Eşleşme bulundu!"
        else:
            hidden_board[row1][col1] = '*'
            hidden_board[row2][col2] = '*'
            feedback = f"Eşleşme yok! Açılan kartlar: Card-1|{row1}-{col1} {card1} \n ve Card-2|{row2}-{col2}: {card2}"

        session.modified = True
        return render_template('memory_game.html', hidden_board=hidden_board, feedback=feedback, revealed_board=board)

    except (ValueError, IndexError):
        return render_template('memory_game.html', hidden_board=session['hidden_board'], feedback="Geçersiz girdi.", revealed_board=session['board'])
