from flask import Flask
from flask_cors import CORS
from routes.backtest import backtest_bp
from routes.symbols import symbols_bp

from routes.market import market_bp
from database.db import init_db
from routes.simulations import simulations_bp
from routes.chart import chart_bp

app = Flask(__name__)
CORS(app)
init_db()

app.register_blueprint(market_bp)
app.register_blueprint(backtest_bp)
app.register_blueprint(simulations_bp)
app.register_blueprint(chart_bp)
app.register_blueprint(symbols_bp)

@app.route("/")
def home():
    return {
        "message": "Crypto Trading Simulator API radi uspješno"
    }

if __name__ == "__main__":
    app.run(debug=True)