import json
import tempfile
import unittest
from unittest.mock import Mock, patch

import pandas as pd
from flask import Flask

from routes.backtest import backtest_bp
from routes.chart import chart_bp
from routes.market import market_bp
from utils.validation import STRATEGY_PARAMETERS


STRATEGIES = ("moving-average", "rsi", "bollinger")


class ApiValidationTests(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        app.config["TESTING"] = True
        app.register_blueprint(backtest_bp)
        app.register_blueprint(chart_bp)
        app.register_blueprint(market_bp)
        self.client = app.test_client()
        self.rows = pd.DataFrame({
            "close": [100.0 + i % 12 for i in range(100)],
            "open_time": [1704067200000 + i * 3600000 for i in range(100)],
            "close_time": [1704070799999 + i * 3600000 for i in range(100)],
        })

    def backtest(self, strategy, fields=None):
        fields = dict(fields or {})
        if strategy == "compare":
            return self.client.get("/api/backtests/compare", query_string=fields)
        parameters = {key: fields.pop(key) for key in list(fields) if key in STRATEGY_PARAMETERS[strategy]}
        return self.client.post("/api/backtests", json={"strategy": strategy, **fields, "parameters": parameters})

    def send(self, prefix, strategy, fields=None):
        if prefix == "chart":
            return self.client.get(f"/api/chart/{strategy}", query_string=fields)
        return self.backtest(strategy, fields)

    def assert_invalid_before_fetch(self, send_request):
        with patch("services.backtest_service.get_dataframe") as backtest_fetch, \
             patch("services.chart_service.get_dataframe") as chart_fetch, \
             patch("routes.market.get_market_data") as market_fetch, \
             patch("routes.backtest.save_simulation", return_value=1) as save:
            response = send_request()
            self.assertEqual(response.status_code, 400, response.get_data(as_text=True))
            self.assertEqual(response.json["status"], "error")
            self.assertTrue(response.json["message"])
            json.dumps(response.json, allow_nan=False)
            for mock in (backtest_fetch, chart_fetch, market_fetch, save):
                mock.assert_not_called()

    def test_invalid_capital_on_all_backtest_endpoints(self):
        """Validacija: početni kapital mora biti konačan broj veći od 0 (HTTP 400)."""
        values = ("0", "-1", "abc", "", "NaN", "Infinity", "-inf", "1e999")
        json_values = (0, -1, True, None, [], float("nan"), float("inf"))
        for strategy in (*STRATEGIES, "compare"):
            for value in values + (json_values if strategy != "compare" else ()):
                with self.subTest(strategy=strategy, value=value):
                    self.assert_invalid_before_fetch(lambda: self.backtest(strategy, {"initial_balance": value}))

    def test_invalid_moving_average_windows(self):
        """Validacija: MA prozori moraju biti pozitivni cijeli brojevi i kratki manji od dugog."""
        cases = [dict(short_window=0), dict(long_window=-1), dict(short_window="2.5"),
                 dict(long_window="abc"), dict(short_window=50, long_window=50),
                 dict(short_window=60, long_window=50), dict(long_window="NaN")]
        for prefix in ("backtest", "chart"):
            for query in cases:
                with self.subTest(prefix=prefix, query=query):
                    self.assert_invalid_before_fetch(lambda: self.send(prefix, "moving-average", query))

    def test_invalid_rsi_period_and_thresholds(self):
        """Validacija: RSI period mora biti pozitivan, a vrijediti 0 <= oversold < overbought <= 100."""
        cases = [dict(period=0), dict(period="1.5"), dict(period="abc"),
                 dict(oversold=-1), dict(overbought=101), dict(oversold=70, overbought=30),
                 dict(oversold=50, overbought=50), dict(overbought="NaN"),
                 dict(oversold="Infinity")]
        for prefix in ("backtest", "chart"):
            for query in cases:
                with self.subTest(prefix=prefix, query=query):
                    self.assert_invalid_before_fetch(lambda: self.send(prefix, "rsi", query))

    def test_invalid_bollinger_parameters(self):
        """Validacija: Bollinger prozor mora biti barem 2, a broj devijacija veći od 0."""
        cases = [dict(window=1), dict(window=0), dict(window="2.5"),
                 dict(window="abc"), dict(num_std=0), dict(num_std=-1),
                 dict(num_std="NaN"), dict(num_std="Infinity"), dict(num_std="abc")]
        for prefix in ("backtest", "chart"):
            for query in cases:
                with self.subTest(prefix=prefix, query=query):
                    self.assert_invalid_before_fetch(lambda: self.send(prefix, "bollinger", query))

    def test_json_integers_must_be_whole_numbers(self):
        """Validacija: cijeli brojevi u JSON-u ne smiju biti decimalni ni logičke vrijednosti."""
        for strategy, parameters in (("moving-average", {"short_window": 2.5}), ("rsi", {"period": 14.0}),
                                     ("bollinger", {"window": True})):
            with self.subTest(strategy=strategy):
                self.assert_invalid_before_fetch(lambda: self.backtest(strategy, parameters))

    def test_invalid_market_inputs(self):
        """Validacija: neispravan simbol, interval ili limit odbija se na svim rutama."""
        senders = [lambda q, s=s: self.backtest(s, q) for s in (*STRATEGIES, "compare")]
        senders += [lambda q, s=s: self.send("chart", s, q) for s in STRATEGIES]
        senders += [lambda q: self.client.get("/api/market-data", query_string=q)]
        cases = [dict(symbol=""), dict(symbol="../BTCUSDT"), dict(symbol="BTC/USDT"),
                 dict(interval="2d"), dict(interval=""), dict(limit=0),
                 dict(limit=1001), dict(limit="4.2"), dict(limit="abc")]
        for index, sender in enumerate(senders):
            for query in cases:
                with self.subTest(endpoint=index, query=query):
                    self.assert_invalid_before_fetch(lambda: sender(query))

    def test_invalid_dates(self):
        """Validacija: datumi moraju biti oba navedena, stvarni, u formatu YYYY-MM-DD i ne u budućnosti."""
        cases = [dict(start_date="2025-01-01"), dict(end_date="2025-01-01"),
                 dict(start_date="", end_date=""),
                 dict(start_date="2025-02-30", end_date="2025-03-01"),
                 dict(start_date="2025-2-01", end_date="2025-03-01"),
                 dict(start_date="2025-03-02", end_date="2025-03-01"),
                 dict(start_date="2099-01-01", end_date="2099-01-02")]
        for prefix in ("backtest", "chart"):
            for query in cases:
                with self.subTest(prefix=prefix, query=query):
                    self.assert_invalid_before_fetch(lambda: self.send(prefix, "rsi", query))

    def test_excessive_date_range(self):
        """Validacija: predugo razdoblje za odabrani interval odbija se."""
        self.assert_invalid_before_fetch(lambda: self.backtest("compare", dict(
            interval="1h", start_date="2025-01-01", end_date="2025-05-01"
        )))

    def test_duplicate_query_parameter(self):
        """Validacija: parametar naveden dvaput u URL-u odbija se."""
        self.assert_invalid_before_fetch(lambda: self.client.get("/api/backtests/compare", query_string=[
            ("initial_balance", "10000"), ("initial_balance", "0")
        ]))

    def test_invalid_request_body(self):
        """Validacija: tijelo POST zahtjeva mora biti JSON objekt s poznatom strategijom i njezinim parametrima."""
        bodies = [
            dict(data="not json", content_type="application/json"),
            dict(data="symbol=BTCUSDT", content_type="application/x-www-form-urlencoded"),
            dict(json=["rsi"]),
            dict(json={}),
            dict(json={"strategy": "macd"}),
            dict(json={"strategy": "rsi", "parameters": [14, 30, 70]}),
            dict(json={"strategy": "rsi", "parameters": {"short_window": 20}}),
            dict(json={"strategy": "rsi", "initial_capital": 10000}),
        ]
        for body in bodies:
            with self.subTest(body=body):
                self.assert_invalid_before_fetch(lambda: self.client.post("/api/backtests", **body))

    def test_wrong_json_types_are_400_not_500(self):
        """Validacija: lista, objekt ili logička vrijednost umjesto teksta ili broja vraća 400, a ne 500."""
        wrong_values = ([], {}, True)
        bodies = [{"strategy": value} for value in wrong_values]
        for field in ("symbol", "interval", "limit", "initial_balance", "start_date", "end_date"):
            bodies += [{"strategy": "rsi", field: value} for value in wrong_values]
        for name in STRATEGY_PARAMETERS["rsi"]:
            bodies += [{"strategy": "rsi", "parameters": {name: value}} for value in wrong_values]
        bodies += [{"strategy": "rsi", "parameters": value} for value in ([], True, "14")]
        for body in bodies:
            with self.subTest(body=body):
                self.assert_invalid_before_fetch(lambda: self.client.post("/api/backtests", json=body))

    def test_running_a_backtest_requires_post(self):
        """REST: simulacija se pokreće samo POST zahtjevom; GET je ne pokreće ni ne sprema."""
        with patch("routes.backtest.save_simulation", return_value=1) as save:
            self.assertEqual(self.client.get("/api/backtests").status_code, 405)
            self.assertEqual(self.client.get("/api/backtest/rsi").status_code, 404)
            save.assert_not_called()

    def test_empty_market_data_is_400_without_database_write(self):
        """Podaci: prazan skup tržišnih podataka vraća 400 i ništa se ne sprema."""
        for strategy in (*STRATEGIES, "compare"):
            with self.subTest(strategy=strategy), \
                 patch("services.backtest_service.get_dataframe", return_value=pd.DataFrame()), \
                 patch("routes.backtest.save_simulation", return_value=1) as save:
                response = self.backtest(strategy)
                self.assertEqual(response.status_code, 400)
                self.assertIn("nema tržišnih podataka", response.json["message"])
                save.assert_not_called()

    def test_insufficient_market_data_is_400(self):
        """Podaci: premalo OHLCV zapisa za odabrani prozor vraća 400."""
        for strategy, count in (("moving-average", 49), ("rsi", 14), ("bollinger", 19)):
            for prefix in ("backtest", "chart"):
                with self.subTest(strategy=strategy, prefix=prefix), \
                     patch(f"services.{prefix}_service.get_dataframe", return_value=self.rows.iloc[:count]), \
                     patch("routes.backtest.save_simulation", return_value=1) as save:
                    response = self.send(prefix, strategy)
                    self.assertEqual(response.status_code, 400)
                    self.assertIn("Nedovoljno", response.json["message"])
                    save.assert_not_called()

    def test_minimum_sufficient_market_data_is_accepted(self):
        """Podaci: točno minimalan broj OHLCV zapisa je prihvaćen."""
        for strategy, count in (("moving-average", 50), ("rsi", 15), ("bollinger", 20)):
            with self.subTest(strategy=strategy), \
                 patch("services.backtest_service.get_dataframe", return_value=self.rows.iloc[:count]), \
                 patch("routes.backtest.save_simulation", return_value=1) as save:
                response = self.backtest(strategy)
                self.assertEqual(response.status_code, 201, response.get_data(as_text=True))
                save.assert_called_once()
                json.dumps(response.json, allow_nan=False)

    def test_valid_requests_keep_response_shape_and_save_once(self):
        """REST: ispravna simulacija vraća 201, ID i adresu spremljene simulacije te se sprema jednom."""
        for strategy in STRATEGIES:
            with self.subTest(strategy=strategy), \
                 patch("services.backtest_service.get_dataframe", return_value=self.rows.copy()), \
                 patch("routes.backtest.save_simulation", return_value=42) as save:
                response = self.backtest(strategy, {"initial_balance": 12500.50})
                self.assertEqual(response.status_code, 201)
                self.assertEqual(response.headers["Location"], "/api/simulations/42")
                self.assertEqual(response.json["id"], 42)
                self.assertEqual(response.json["result"]["initial_balance"], 12500.5)
                self.assertEqual(response.json["status"], "success")
                self.assertIn("chart_data", response.json["result"])
                save.assert_called_once()
                json.dumps(response.json, allow_nan=False)

    def test_valid_compare_returns_fixed_configurations_without_save(self):
        """Usporedba: uvijek koristi fiksne referentne parametre i ništa ne sprema."""
        with patch("services.backtest_service.get_dataframe", return_value=self.rows), \
             patch("routes.backtest.save_simulation", return_value=1) as save:
            response = self.client.get("/api/backtests/compare", query_string={"short_window": 5})
            self.assertEqual(response.status_code, 200)
            self.assertEqual([item["parameters"] for item in response.json["results"]], [
                {"short_window": 20, "long_window": 50},
                {"period": 14, "oversold": 30, "overbought": 70},
                {"window": 20, "num_std": 2},
            ])
            save.assert_not_called()

    def test_valid_chart_endpoints(self):
        """Graf: rute za podatke grafa rade za sve tri strategije."""
        for strategy in STRATEGIES:
            with self.subTest(strategy=strategy), \
                 patch("services.chart_service.get_dataframe", return_value=self.rows.copy()):
                response = self.client.get(f"/api/chart/{strategy}")
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.json["prices"]), 100)
                json.dumps(response.json, allow_nan=False)

    def test_legal_rsi_boundary_parameters(self):
        """Validacija: rubne dopuštene RSI vrijednosti (period 1, granice 0 i 100) su prihvaćene."""
        with patch("services.backtest_service.get_dataframe", return_value=self.rows), \
             patch("routes.backtest.save_simulation", return_value=1):
            response = self.backtest("rsi", {"period": 1, "oversold": 0, "overbought": 100})
            self.assertEqual(response.status_code, 201)

    def test_valid_calendar_dates_pass_to_data_service(self):
        """Validacija: ispravni kalendarski datumi (i 29. veljače) prosljeđuju se dohvatu podataka."""
        with patch("services.backtest_service.get_dataframe", return_value=self.rows) as fetch, \
             patch("routes.backtest.save_simulation", return_value=1):
            response = self.backtest("rsi", {"start_date": "2024-02-29", "end_date": "2024-03-31"})
            self.assertEqual(response.status_code, 201)
            self.assertEqual(fetch.call_args.args[-2:], ("2024-02-29", "2024-03-31"))

    def test_nonexistent_binance_symbol_becomes_400(self):
        """Podaci: simbol koji ne postoji na Binanceu vraća 400 s jasnom porukom."""
        upstream = Mock(status_code=400)
        upstream.json.return_value = {"code": -1121, "msg": "Invalid symbol."}
        with tempfile.TemporaryDirectory() as directory, \
             patch("services.binance_service.DATA_DIR", directory), \
             patch("services.binance_service.requests.get", return_value=upstream), \
             patch("routes.backtest.save_simulation", return_value=1) as save:
            for strategy in (*STRATEGIES, "compare"):
                with self.subTest(strategy=strategy):
                    response = self.backtest(strategy, {"symbol": "NOTAREALPAIR"})
                    self.assertEqual(response.status_code, 400)
                    self.assertIn("ne postoji", response.json["message"])
            save.assert_not_called()


if __name__ == "__main__":
    unittest.main()
