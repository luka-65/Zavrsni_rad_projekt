import sqlite3
from datetime import datetime

DB_PATH = "database/simulations.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS simulations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            strategy TEXT NOT NULL,
            symbol TEXT NOT NULL,
            interval TEXT NOT NULL,
            initial_balance REAL NOT NULL,
            final_balance REAL NOT NULL,
            return_pct REAL NOT NULL,
            max_drawdown_pct REAL NOT NULL,
            win_rate_pct REAL NOT NULL,
            number_of_trades INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def save_simulation(strategy, symbol, interval, result):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO simulations (
            strategy,
            symbol,
            interval,
            initial_balance,
            final_balance,
            return_pct,
            max_drawdown_pct,
            win_rate_pct,
            number_of_trades,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        strategy,
        symbol,
        interval,
        result["initial_balance"],
        result["final_balance"],
        result["return_pct"],
        result["max_drawdown_pct"],
        result["win_rate_pct"],
        result["number_of_trades"],
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def get_all_simulations():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM simulations
        ORDER BY created_at DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]