import json
import os
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd
from flask import Flask

from database import db
from routes.backtest import backtest_bp
from routes.simulations import simulations_bp
from services.backtest_service import run_bollinger, run_moving_average, run_rsi
from services.chart_data import build_chart_data


CASES = (
    ("moving-average", {"short_window": 5, "long_window": 30}),
    ("rsi", {"period": 10, "oversold": 20.0, "overbought": 80.0}),
    ("bollinger", {"window": 15, "num_std": 2.5}),
)


def market_rows(count=100):
    return pd.DataFrame({
        "close": [100.0 + i % 12 for i in range(count)],
        "open_time": [1704067200000 + i * 3600000 for i in range(count)],
        "close_time": [1704070799999 + i * 3600000 for i in range(count)],
    })


class PersistenceTestCase(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        app.config["TESTING"] = True
        app.register_blueprint(backtest_bp)
        app.register_blueprint(simulations_bp)
        self.client = app.test_client()
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.db_path = os.path.join(directory.name, "test.db")
        db_patch = patch.object(db, "DB_PATH", self.db_path)
        db_patch.start()
        self.addCleanup(db_patch.stop)

    def run_strategy(self, strategy, parameters=None, **fields):
        with patch("services.backtest_service.get_dataframe", return_value=market_rows()):
            return self.client.post("/api/backtests", json={
                "strategy": strategy, "parameters": parameters or {}, **fields,
            })


class SavedSimulationTests(PersistenceTestCase):
    def test_saved_result_is_identical_after_loading(self):
        """Spremanje: rezultat učitan iz baze jednak je rezultatu koji je API vratio."""
        db.init_db()
        response = self.run_strategy("bollinger")
        self.assertEqual(response.status_code, 201)
        history = db.get_all_simulations()
        self.assertEqual([item["id"] for item in history], [response.json["id"]])
        self.assertEqual(db.get_simulation_by_id(response.json["id"])["result"], response.json["result"])

    def test_custom_parameters_are_saved_and_returned_by_history_and_details(self):
        """Parametri: spremljeni parametri svake strategije vraćaju se u povijesti i detaljima."""
        db.init_db()
        for strategy, parameters in CASES:
            with self.subTest(strategy=strategy):
                response = self.run_strategy(strategy, parameters)
                self.assertEqual(response.status_code, 201, response.get_data(as_text=True))
                self.assertEqual(response.json["parameters"], parameters)

                history = self.client.get("/api/simulations").json["data"]
                self.assertEqual(history[0]["parameters"], parameters)
                self.assertNotIn("parameters_json", history[0])

                details = self.client.get(f"/api/simulations/{history[0]['id']}").json["data"]
                self.assertEqual(details["parameters"], parameters)

    def test_default_parameters_are_saved_when_request_omits_them(self):
        """Parametri: kad zahtjev ne navede parametre, spremaju se zadane vrijednosti."""
        db.init_db()
        self.assertEqual(self.run_strategy("rsi").status_code, 201)
        saved = db.get_all_simulations()[0]["parameters"]
        self.assertEqual(saved, {"period": 14, "oversold": 30.0, "overbought": 70.0})

    def test_two_rsi_runs_with_different_thresholds_are_distinguishable(self):
        """Parametri: dvije RSI simulacije s granicama 30/70 i 20/80 razlikuju se u povijesti."""
        db.init_db()
        self.run_strategy("rsi", {"oversold": 30, "overbought": 70})
        self.run_strategy("rsi", {"oversold": 20, "overbought": 80})
        thresholds = {
            (item["parameters"]["oversold"], item["parameters"]["overbought"])
            for item in db.get_all_simulations()
        }
        self.assertEqual(thresholds, {(30.0, 70.0), (20.0, 80.0)})

    def test_existing_database_without_parameters_column_is_migrated(self):
        """Migracija: postojeća baza bez stupca za parametre nadograđuje se bez gubitka podataka."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE simulations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy TEXT NOT NULL, symbol TEXT NOT NULL, interval TEXT NOT NULL,
                initial_balance REAL NOT NULL, final_balance REAL NOT NULL,
                return_pct REAL NOT NULL, max_drawdown_pct REAL NOT NULL,
                win_rate_pct REAL NOT NULL, number_of_trades INTEGER NOT NULL,
                result_json TEXT, start_date TEXT, end_date TEXT, created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            INSERT INTO simulations (strategy, symbol, interval, initial_balance, final_balance,
                return_pct, max_drawdown_pct, win_rate_pct, number_of_trades, created_at)
            VALUES ('Bollinger Bands', 'BTCUSDT', '1d', 10000, 11000, 10, 5, 50, 2, '2026-01-01 10:00:00')
        """)
        conn.commit()
        conn.close()

        db.init_db()
        old = db.get_all_simulations()[0]
        self.assertIsNone(old["parameters"])
        self.assertIsNone(db.get_simulation_by_id(old["id"])["parameters"])

        self.run_strategy("bollinger", {"window": 15, "num_std": 2.5})
        newest = db.get_all_simulations()[0]
        self.assertEqual(newest["parameters"], {"window": 15, "num_std": 2.5})


class HistoryRouteTests(PersistenceTestCase):
    def test_details_and_delete_of_missing_simulation_return_404(self):
        """Povijest: detalji i brisanje nepostojeće simulacije vraćaju 404."""
        db.init_db()
        self.assertEqual(self.client.get("/api/simulations/999").status_code, 404)
        self.assertEqual(self.client.delete("/api/simulations/999").status_code, 404)

    def test_delete_removes_only_the_selected_simulation(self):
        """Povijest: brisanje uklanja samo odabranu simulaciju."""
        db.init_db()
        first = self.run_strategy("rsi").json["id"]
        second = self.run_strategy("bollinger").json["id"]
        self.assertEqual(self.client.delete(f"/api/simulations/{first}").status_code, 200)
        self.assertEqual([item["id"] for item in db.get_all_simulations()], [second])
        self.assertEqual(self.client.get(f"/api/simulations/{first}").status_code, 404)

    def test_dashboard_summarises_saved_simulations(self):
        """Nadzorna ploča: sažetak broji spremljene simulacije i pronalazi najveći zabilježeni povrat."""
        db.init_db()
        empty = self.client.get("/api/dashboard-stats").json["data"]
        self.assertEqual(empty["total_simulations"], 0)
        self.assertIsNone(self.client.get("/api/best-backtest").json["data"])

        for strategy, parameters in CASES:
            self.run_strategy(strategy, parameters)
        history = db.get_all_simulations()
        stats = self.client.get("/api/dashboard-stats").json["data"]
        best = self.client.get("/api/best-backtest").json["data"]
        self.assertEqual(stats["total_simulations"], 3)
        self.assertEqual(stats["best_roi"], round(max(item["return_pct"] for item in history), 2))
        self.assertEqual(best["return_pct"], max(item["return_pct"] for item in history))
        self.assertIn("parameters", best)


class ChartSnapshotTests(unittest.TestCase):
    def market_data(self):
        prices = [100.0] * 20 + [50.0, 60.0] + [100.0] * 20 + [150.0, 100.0]
        return pd.DataFrame({
            "close": prices,
            "open_time": [1704067200000 + i * 3600000 for i in range(len(prices))],
            "close_time": [1704070799999 + i * 3600000 for i in range(len(prices))],
        })

    def test_all_strategies_keep_serializable_chart_snapshot(self):
        """Snimka grafa: svaka strategija sprema vremensku os, cijene i indikatore korištene u simulaciji."""
        cases = [
            (run_moving_average, [3, 5], "ma_long"),
            (run_rsi, [14, 30, 70], "rsi"),
            (run_bollinger, [20, 2], "upper_band"),
        ]
        for strategy, params, indicator in cases:
            with self.subTest(strategy=strategy.__name__):
                df = self.market_data()
                with patch("services.backtest_service.get_dataframe", return_value=df):
                    result = strategy("TESTUSDT", "1h", 200, 10000, *params)
                snapshot = result["chart_data"]
                self.assertEqual(snapshot["timestamps"], df["close_time"].tolist())
                self.assertEqual(snapshot["prices"], df["close"].tolist())
                self.assertIsNone(snapshot[indicator][0])
                self.assertEqual(len(snapshot[indicator]), len(df))
                for trade in result["trades"]:
                    self.assertEqual(trade["timestamp"], snapshot["timestamps"][trade["candle_index"]])
                json.dumps(result, allow_nan=False)

    def test_snapshot_survives_database_roundtrip_without_bloating_history(self):
        """Snimka grafa: nakon spremanja i učitavanja ostaje ista, a popis povijesti je ne učitava."""
        df = self.market_data()
        with patch("services.backtest_service.get_dataframe", return_value=df):
            result = run_bollinger("TESTUSDT", "1h", 200, 10000, 20, 2)
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(db, "DB_PATH", os.path.join(directory, "test.db")):
                db.init_db()
                db.save_simulation("Bollinger Bands", "TESTUSDT", "1h", result)
                history = db.get_all_simulations()
                self.assertNotIn("result_json", history[0])
                saved = db.get_simulation_by_id(history[0]["id"])["result"]
                self.assertEqual(saved["chart_data"], result["chart_data"])
                self.assertEqual(saved["trades"], result["trades"])

    def test_unavailable_indicator_values_are_gaps_not_zeroes(self):
        """Snimka grafa: nedostupne vrijednosti indikatora spremaju se kao praznine, ne kao nule."""
        df = self.market_data()
        df["RSI"] = float("nan")
        snapshot = build_chart_data(df)
        self.assertTrue(all(value is None for value in snapshot["rsi"]))
        json.dumps(snapshot, allow_nan=False)


if __name__ == "__main__":
    unittest.main()
