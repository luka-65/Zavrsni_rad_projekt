import sqlite3
from datetime import datetime
from collections import Counter
import json

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
            result_json TEXT,
            start_date TEXT,
            end_date TEXT,
            created_at TEXT NOT NULL
        )
    """)

    try:
        cursor.execute("""
            ALTER TABLE simulations
            ADD COLUMN result_json TEXT
        """)
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("""
            ALTER TABLE simulations
            ADD COLUMN start_date TEXT
        """)
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("""
            ALTER TABLE simulations
            ADD COLUMN end_date TEXT
        """)
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()

    


def save_simulation(strategy, symbol, interval, result, start_date=None, end_date=None):
    conn = get_connection()
    cursor = conn.cursor()

    result["start_date"] = start_date
    result["end_date"] = end_date

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
            result_json,
            start_date,
            end_date,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        json.dumps(result),
        start_date,
        end_date,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def get_all_simulations():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, strategy, symbol, interval, initial_balance, final_balance,
               return_pct, max_drawdown_pct, win_rate_pct, number_of_trades,
               start_date, end_date, created_at
        FROM simulations
        ORDER BY created_at DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]

def get_dashboard_stats():
    data = get_all_simulations()

    if not data:
        return {
            "total_simulations": 0,
            "best_roi": 0,
            "most_used_strategy": "-",
            "most_traded_symbol": "-"
        }

    total_simulations = len(data)

    best_roi = max(item["return_pct"] for item in data)

    strategy_counter = Counter(
        item["strategy"] for item in data
    )

    most_used_strategy = strategy_counter.most_common(1)[0][0]

    symbol_counter = Counter(
        item["symbol"] for item in data
    )

    most_traded_symbol = symbol_counter.most_common(1)[0][0]

    return {
        "total_simulations": total_simulations,
        "best_roi": round(best_roi, 2),
        "most_used_strategy": most_used_strategy,
        "most_traded_symbol": most_traded_symbol
    }

def get_best_backtest():

    data = get_all_simulations()

    if not data:
        return None

    best = max(
        data,
        key=lambda x: x["return_pct"]
    )

    return best

def get_simulation_by_id(simulation_id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM simulations
        WHERE id = ?
    """, (simulation_id,))

    row = cursor.fetchone()

    conn.close()

    if row is None:
        return None

    simulation = dict(row)

    if simulation.get("result_json"):
        simulation["result"] = json.loads(
            simulation["result_json"]
        )

    return simulation

def delete_simulation(simulation_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM simulations
        WHERE id = ?
    """, (simulation_id,))

    deleted_count = cursor.rowcount

    conn.commit()
    conn.close()

    return deleted_count > 0
