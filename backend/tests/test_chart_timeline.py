import json
import os
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

from backtesting.backtester import run_backtest
from database import db
from services.backtest_service import run_moving_average, run_rsi, run_bollinger
from services.chart_data import build_chart_data


class ChartTimelineTests(unittest.TestCase):
    def market_data(self):
        prices = [100.0] * 20 + [50.0, 60.0] + [100.0] * 20 + [150.0, 100.0]
        return pd.DataFrame({
            'close': prices,
            'open_time': [1704067200000 + i * 3600000 for i in range(len(prices))],
            'close_time': [1704070799999 + i * 3600000 for i in range(len(prices))],
        })

    def test_trade_times_match_candles_including_final_close(self):
        df = self.market_data().iloc[:4].copy()
        df['close'] = [0.00123456, 0.00234567, 0.00156789, 0.00256789]
        df['position'] = [1, -1, 1, 0]
        result = run_backtest(df)
        self.assertEqual([t['candle_index'] for t in result['trades']], [0, 1, 2, 3])
        for trade in result['trades']:
            row = df.iloc[trade['candle_index']]
            self.assertEqual(trade['timestamp'], int(row['close_time']))
            self.assertEqual(trade['price'], row['close'])
        self.assertTrue(result['trades'][-1]['is_final_close'])
        json.dumps(result, allow_nan=False)

    def test_all_strategies_keep_serializable_chart_snapshot(self):
        cases = [
            (run_moving_average, [3, 5], 'ma_long'),
            (run_rsi, [14, 30, 70], 'rsi'),
            (run_bollinger, [20, 2], 'upper_band'),
        ]
        for strategy, params, indicator in cases:
            with self.subTest(strategy=strategy.__name__):
                df = self.market_data()
                with patch('services.backtest_service.get_dataframe', return_value=df):
                    result = strategy('TESTUSDT', '1h', 200, 10000, *params)
                snapshot = result['chart_data']
                self.assertEqual(snapshot['timestamps'], df['close_time'].tolist())
                self.assertEqual(snapshot['prices'], df['close'].tolist())
                self.assertIsNone(snapshot[indicator][0])
                self.assertEqual(len(snapshot[indicator]), len(df))
                for trade in result['trades']:
                    self.assertEqual(trade['timestamp'], snapshot['timestamps'][trade['candle_index']])
                json.dumps(result, allow_nan=False)

    def test_snapshot_survives_database_roundtrip_without_bloating_history(self):
        df = self.market_data()
        with patch('services.backtest_service.get_dataframe', return_value=df):
            result = run_bollinger('TESTUSDT', '1h', 200, 10000, 20, 2)
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(db, 'DB_PATH', os.path.join(directory, 'test.db')):
                db.init_db()
                db.save_simulation('Bollinger Bands', 'TESTUSDT', '1h', result)
                history = db.get_all_simulations()
                self.assertNotIn('result_json', history[0])
                saved = db.get_simulation_by_id(history[0]['id'])['result']
                self.assertEqual(saved['chart_data'], result['chart_data'])
                self.assertEqual(saved['trades'], result['trades'])

    def test_unavailable_indicator_values_are_gaps_not_zeroes(self):
        df = self.market_data()
        df['RSI'] = float('nan')
        snapshot = build_chart_data(df)
        self.assertTrue(all(value is None for value in snapshot['rsi']))
        json.dumps(snapshot, allow_nan=False)


if __name__ == '__main__':
    unittest.main()
