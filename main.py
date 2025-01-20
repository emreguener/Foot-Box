from flask import Flask, render_template
from Routes.Game1 import game1_bp
from Routes.Game2 import game2_bp
from Routes.Game3 import game3_bp
from Routes.Game4 import memory_game_bp

app = Flask(__name__)

# Flask uygulamanıza secret key ekleyin
app.secret_key = 'secret_key'  # Bunu, güvenli bir anahtar değeri ile değiştirdiğinizden emin olun!

# Blueprint'leri kaydediyoruz
app.register_blueprint(game1_bp)
app.register_blueprint(game2_bp)
app.register_blueprint(game3_bp)
app.register_blueprint(memory_game_bp)


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)