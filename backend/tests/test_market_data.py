import os
import tempfile
import time
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

import requests
from flask import Flask

from routes.backtest import backtest_bp
from routes.market import market_bp
from routes.symbols import symbols_bp
from services import binance_service, symbols_service
from services.binance_service import (
    CACHE_TTL_SECONDS, REQUEST_TIMEOUT, date_to_milliseconds, get_cache_file_path, get_market_data,
)


DAY = 86_400_000


def ms(date_value):
    return date_to_milliseconds(date_value)


def kline(open_time, close_time, close=100.0):
    return [open_time, str(close), str(close), str(close), str(close), "1", close_time]


def daily(date_value, close=100.0):
    return kline(ms(date_value), ms(date_value) + DAY - 1, close)


def binance_returning(payload, status_code=200):
    response = Mock(status_code=status_code)
    response.json.return_value = payload
    return patch("services.binance_service.requests.get", return_value=response)


class BinanceTestCase(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.data_dir = directory.name
        data_patch = patch.object(binance_service, "DATA_DIR", self.data_dir)
        data_patch.start()
        self.addCleanup(data_patch.stop)
        symbols_service._symbols_cache.update(fetched_at=None, symbols=[])

        app = Flask(__name__)
        app.config["TESTING"] = True
        for blueprint in (backtest_bp, market_bp, symbols_bp):
            app.register_blueprint(blueprint)
        self.client = app.test_client()

    def set_saved_at(self, path, timestamp_ms):
        os.utime(path, (timestamp_ms / 1000, timestamp_ms / 1000))


class NetworkErrorTests(BinanceTestCase):
    ENDPOINTS = ("/api/backtests", "/api/backtests/compare", "/api/market-data", "/api/symbols/search?query=BTC")

    def assert_error_on_all_endpoints(self, status_code, text, **mock_options):
        with patch("services.binance_service.requests.get", **mock_options), \
             patch("routes.backtest.save_simulation", return_value=1) as save:
            for endpoint in self.ENDPOINTS:
                with self.subTest(endpoint=endpoint):
                    if endpoint == "/api/backtests":
                        response = self.client.post(endpoint, json={"strategy": "rsi"})
                    else:
                        response = self.client.get(endpoint)
                    self.assertEqual(response.status_code, status_code, response.get_data(as_text=True))
                    self.assertEqual(response.json["status"], "error")
                    self.assertIn(text, response.json["message"])
            save.assert_not_called()

    def test_every_binance_request_has_a_timeout(self):
        """Mreža: svaki poziv prema Binanceu ima vremensko ograničenje (timeout)."""
        with binance_returning([daily("2025-01-01")]) as get:
            get_market_data()
            self.assertEqual(get.call_args.kwargs["timeout"], REQUEST_TIMEOUT)
        with binance_returning({"symbols": []}) as get:
            symbols_service.search_symbols("BTC")
            self.assertEqual(get.call_args.kwargs["timeout"], REQUEST_TIMEOUT)

    def test_timeout_becomes_504(self):
        """Mreža: Binance koji ne odgovori na vrijeme daje HTTP 504 s porukom, bez spremanja."""
        self.assert_error_on_all_endpoints(504, "nije odgovorio na vrijeme", side_effect=requests.Timeout())

    def test_connection_error_becomes_502(self):
        """Mreža: nedostupan Binance daje HTTP 502 s porukom, bez spremanja."""
        self.assert_error_on_all_endpoints(502, "ne može pristupiti", side_effect=requests.ConnectionError())

    def test_binance_server_error_becomes_502(self):
        """Mreža: pogreška poslužitelja Binancea daje HTTP 502."""
        self.assert_error_on_all_endpoints(502, "HTTP 500", return_value=Mock(status_code=500))

    def test_rate_limit_becomes_502_with_explanation(self):
        """Mreža: ograničenje broja zahtjeva (HTTP 429) daje HTTP 502 s objašnjenjem."""
        self.assert_error_on_all_endpoints(502, "ograničio broj zahtjeva", return_value=Mock(status_code=429))

    def test_invalid_json_becomes_502(self):
        """Mreža: neispravan odgovor Binancea daje HTTP 502."""
        response = Mock(status_code=200)
        response.json.side_effect = ValueError
        self.assert_error_on_all_endpoints(502, "neispravan odgovor", return_value=response)


class PeriodBoundaryTests(BinanceTestCase):
    def test_weekly_row_crossing_end_date_is_dropped(self):
        """Granice: tjedni zapis koji završava nakon završnog datuma ne ulazi u analizu."""
        rows = [
            kline(ms("2025-05-12"), ms("2025-05-19") - 1),
            kline(ms("2025-05-19"), ms("2025-05-26") - 1),
            kline(ms("2025-05-26"), ms("2025-06-02") - 1),
            kline(ms("2025-06-02"), ms("2025-06-09") - 1),
        ]
        with binance_returning(rows):
            data = get_market_data("BTCUSDT", "1w", 200, True, "2025-05-18", "2025-06-03")
        self.assertEqual([row["open_time"] for row in data], [ms("2025-05-19"), ms("2025-05-26")])

    def test_monthly_row_crossing_end_date_is_dropped(self):
        """Granice: mjesečni zapis koji završava nakon završnog datuma ne ulazi u analizu."""
        rows = [
            kline(ms("2025-02-01"), ms("2025-03-01") - 1),
            kline(ms("2025-06-01"), ms("2025-07-01") - 1),
        ]
        with binance_returning(rows):
            data = get_market_data("BTCUSDT", "1M", 200, True, "2025-01-15", "2025-06-10")
        self.assertEqual([row["open_time"] for row in data], [ms("2025-02-01")])

    def test_daily_row_of_end_date_is_kept(self):
        """Granice: dnevni zapis završnog datuma ostaje u analizi."""
        with binance_returning([daily("2025-03-30"), daily("2025-03-31")]):
            data = get_market_data("BTCUSDT", "1d", 200, True, "2025-03-30", "2025-03-31")
        self.assertEqual(len(data), 2)
        self.assertEqual(data[-1]["close_time"], date_to_milliseconds("2025-03-31", end_of_day=True))

    def test_latest_query_drops_forming_row_and_keeps_limit(self):
        """Granice: upit za zadnjih N zapisa izostavlja nedovršeni tekući zapis."""
        today = datetime.now(timezone.utc).date()
        days = [(today - timedelta(days=n)).isoformat() for n in (4, 3, 2, 1, 0)]
        with binance_returning([daily(day) for day in days]) as get:
            data = get_market_data("BTCUSDT", "1d", 3)
        self.assertEqual(get.call_args.kwargs["params"]["limit"], 4)
        self.assertEqual([row["open_time"] for row in data], [ms(day) for day in days[1:4]])

    def test_old_cache_with_crossing_row_is_corrected_without_download(self):
        """Granice: stari cache s prelaznim zapisom ispravlja se bez ponovnog dohvata."""
        path = get_cache_file_path("BTCUSDT", "1w", 200, "2025-05-18", "2025-06-03")
        binance_service.write_cache(path, [
            binance_service.format_kline(kline(ms("2025-05-19"), ms("2025-05-26") - 1)),
            binance_service.format_kline(kline(ms("2025-06-02"), ms("2025-06-09") - 1)),
        ])
        with patch("services.binance_service.requests.get") as get:
            data = get_market_data("BTCUSDT", "1w", 200, True, "2025-05-18", "2025-06-03")
            get.assert_not_called()
        self.assertEqual([row["open_time"] for row in data], [ms("2025-05-19")])

    def test_backtest_does_not_trade_after_end_date(self):
        """Granice: simulacija ne koristi nijedan zapis nakon završnog datuma."""
        rows = [kline(ms("2024-01-01") + n * 7 * DAY, ms("2024-01-08") + n * 7 * DAY - 1, 100 + n)
                for n in range(30)]
        with binance_returning(rows), patch("routes.backtest.save_simulation", return_value=1):
            response = self.client.post("/api/backtests", json={
                "strategy": "bollinger", "symbol": "BTCUSDT", "interval": "1w",
                "start_date": "2024-01-01", "end_date": "2024-07-10",
            })
        self.assertEqual(response.status_code, 201)
        period_end = date_to_milliseconds("2024-07-10", end_of_day=True)
        self.assertTrue(all(t <= period_end for t in response.json["result"]["chart_data"]["timestamps"]))


class CacheExpiryTests(BinanceTestCase):
    def test_finished_period_is_cached_permanently(self):
        """Cache: razdoblje koje je završilo prije spremanja trajno se čita iz cachea."""
        with binance_returning([daily("2025-01-01")]) as get:
            get_market_data("BTCUSDT", "1d", 200, True, "2025-01-01", "2025-01-01")
            path = get_cache_file_path("BTCUSDT", "1d", 200, "2025-01-01", "2025-01-01")
            self.set_saved_at(path, date_to_milliseconds("2025-01-02"))
            get_market_data("BTCUSDT", "1d", 200, True, "2025-01-01", "2025-01-01")
            self.assertEqual(get.call_count, 1)

    def test_cache_saved_before_period_ended_is_downloaded_again(self):
        """Cache: cache spremljen prije kraja razdoblja ponovno se dohvaća."""
        path = get_cache_file_path("BTCUSDT", "1d", 200, "2025-01-01", "2025-01-10")
        binance_service.write_cache(path, [binance_service.format_kline(daily("2025-01-01"))])
        self.set_saved_at(path, date_to_milliseconds("2025-01-05"))
        with binance_returning([daily("2025-01-01"), daily("2025-01-10")]) as get:
            data = get_market_data("BTCUSDT", "1d", 200, True, "2025-01-01", "2025-01-10")
            get.assert_called_once()
        self.assertEqual(len(data), 2)

    def test_period_reaching_today_uses_cache_only_within_ttl(self):
        """Cache: razdoblje koje uključuje danas koristi cache samo 5 minuta."""
        today = datetime.now(timezone.utc).date()
        start, yesterday = (today - timedelta(days=3)).isoformat(), (today - timedelta(days=1)).isoformat()
        with binance_returning([daily(yesterday)]) as get:
            get_market_data("BTCUSDT", "1d", 200, True, start, today.isoformat())
            get_market_data("BTCUSDT", "1d", 200, True, start, today.isoformat())
            self.assertEqual(get.call_count, 1)
            path = get_cache_file_path("BTCUSDT", "1d", 200, start, today.isoformat())
            self.set_saved_at(path, (time.time() - CACHE_TTL_SECONDS - 1) * 1000)
            get_market_data("BTCUSDT", "1d", 200, True, start, today.isoformat())
            self.assertEqual(get.call_count, 2)

    def test_latest_query_cache_expires(self):
        """Cache: upit za zadnjih N zapisa koristi cache samo 5 minuta."""
        yesterday = (datetime.now(timezone.utc).date() - timedelta(days=1)).isoformat()
        with binance_returning([daily(yesterday)]) as get:
            get_market_data("BTCUSDT", "1d", 50)
            get_market_data("BTCUSDT", "1d", 50)
            self.assertEqual(get.call_count, 1)
            self.set_saved_at(get_cache_file_path("BTCUSDT", "1d", 50), (time.time() - CACHE_TTL_SECONDS - 1) * 1000)
            get_market_data("BTCUSDT", "1d", 50)
            self.assertEqual(get.call_count, 2)

    def test_symbol_list_is_downloaded_once_per_hour(self):
        """Cache: popis simbola dohvaća se najviše jednom na sat."""
        exchange_info = {"symbols": [
            {"symbol": "BTCUSDT", "baseAsset": "BTC", "quoteAsset": "USDT", "status": "TRADING"},
            {"symbol": "ETHBTC", "baseAsset": "ETH", "quoteAsset": "BTC", "status": "TRADING"},
            {"symbol": "OLDUSDT", "baseAsset": "OLD", "quoteAsset": "USDT", "status": "BREAK"},
        ]}
        with binance_returning(exchange_info) as get:
            self.assertEqual([item["symbol"] for item in symbols_service.search_symbols("b")], ["BTCUSDT"])
            self.assertEqual(symbols_service.search_symbols("eth"), [])
            self.assertEqual(get.call_count, 1)
            symbols_service._symbols_cache["fetched_at"] -= symbols_service.SYMBOLS_CACHE_TTL_SECONDS + 1
            symbols_service.search_symbols("BTC")
            self.assertEqual(get.call_count, 2)


class BrokenCacheTests(BinanceTestCase):
    def test_repeated_empty_response_does_not_create_broken_cache(self):
        """Cache: prazan odgovor Binancea ne stvara praznu cache datoteku i ne sprema simulaciju."""
        with binance_returning([]), patch("routes.backtest.save_simulation", return_value=1) as save:
            for dates in ({}, {"start_date": "2025-01-01", "end_date": "2025-02-01"}):
                for _ in range(2):
                    response = self.client.post("/api/backtests", json={"strategy": "rsi", **dates})
                    self.assertEqual(response.status_code, 400)
            self.assertEqual(os.listdir(self.data_dir), [])
            save.assert_not_called()

    def test_existing_blank_cache_is_downloaded_again(self):
        """Cache: prazna ili oštećena cache datoteka ponovno se dohvaća s Binancea."""
        path = get_cache_file_path("BTCUSDT", "1d", 100)
        with open(path, "w") as stream:
            stream.write("\n")
        with binance_returning([daily("2025-01-01")]) as get:
            data = get_market_data()
            get.assert_called_once()
        self.assertEqual(data[0]["close"], 100)
        self.assertEqual(len(binance_service.pd.read_csv(path)), 1)


if __name__ == "__main__":
    unittest.main()
