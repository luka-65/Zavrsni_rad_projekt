import unittest

import pandas as pd

from backtesting.backtester import run_backtest
from strategies.bollinger import bollinger_bands_strategy
from strategies.rsi import rsi_strategy


class StrategyExitTests(unittest.TestCase):
    def test_default_strategies_sell_before_end_of_period(self):
        cases = [
            (rsi_strategy, list(range(120, 99, -1)) + list(range(101, 132)), 110),
            (bollinger_bands_strategy, [100.0] * 20 + [50.0] + [100.0] * 20 + [150.0, 100.0], 150),
        ]
        for strategy, prices, sell_price in cases:
            with self.subTest(strategy=strategy.__name__):
                df = strategy(pd.DataFrame({'close': prices}))
                result = run_backtest(df)
                self.assertEqual([trade['type'] for trade in result['trades']], ['BUY', 'SELL'])
                self.assertEqual(result['trades'][-1]['price'], sell_price)
                self.assertFalse(result['trades'][-1]['is_final_close'])
                self.assertEqual(result['number_of_trades'], 1)

    def test_neutral_rows_preserve_state_and_allow_reentry(self):
        cases = [
            (rsi_strategy, {'period': 3},
             [100, 99, 98, 97, 98, 99, 100, 101, 100, 99, 98, 97, 98, 99, 100],
             [2, 10], [6, 14], [4, 5, 12, 13], [8, 9], 100 / 98),
            (bollinger_bands_strategy, {'window': 3, 'num_std': 1},
             [100, 100, 90, 91, 110, 100, 100, 90, 91, 110, 100],
             [2, 7], [4, 9], [3, 8], [5, 6, 10], 110 / 90),
        ]
        for strategy, params, prices, buys, sells, held, flat, growth in cases:
            with self.subTest(strategy=strategy.__name__):
                df = strategy(pd.DataFrame({'close': prices}), **params)
                self.assertEqual(df.index[df['position'] == 1].tolist(), buys)
                self.assertEqual(df.index[df['position'] == -1].tolist(), sells)
                self.assertTrue((df.loc[held, 'signal'] == 1).all())
                self.assertTrue((df.loc[flat, 'signal'] == 0).all())
                result = run_backtest(df)
                self.assertEqual([trade['type'] for trade in result['trades']], ['BUY', 'SELL', 'BUY', 'SELL'])
                self.assertFalse(any(trade['is_final_close'] for trade in result['trades']))
                self.assertEqual(result['number_of_trades'], 2)
                self.assertEqual(result['win_rate_pct'], 100)
                self.assertEqual(result['final_balance'], round(10000 * growth ** 2, 2))

    def test_no_trades_without_entry_signal(self):
        for strategy in (rsi_strategy, bollinger_bands_strategy):
            for prices in ([100.0] * 40, [100.0] * 2):
                with self.subTest(strategy=strategy.__name__, candles=len(prices)):
                    result = run_backtest(strategy(pd.DataFrame({'close': prices})))
                    self.assertEqual(result['trades'], [])
                    self.assertEqual(result['final_balance'], 10000)
                    self.assertEqual(result['number_of_trades'], 0)

    def test_final_close_remains_when_no_sell_signal_occurs(self):
        cases = [
            (rsi_strategy, list(range(120, 99, -1))),
            (bollinger_bands_strategy, [100.0] * 20 + [50.0, 60.0]),
        ]
        for strategy, prices in cases:
            with self.subTest(strategy=strategy.__name__):
                result = run_backtest(strategy(pd.DataFrame({'close': prices})))
                self.assertEqual([trade['type'] for trade in result['trades']], ['BUY', 'SELL'])
                self.assertTrue(result['trades'][-1]['is_final_close'])
                self.assertEqual(result['trades'][-1]['price'], prices[-1])


if __name__ == '__main__':
    unittest.main()
