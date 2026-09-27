import json
import unittest

import pandas as pd

from backtesting.backtester import run_backtest
from utils.validation import ValidationError


def market(prices, positions):
    return pd.DataFrame({
        "close": [float(price) for price in prices],
        "position": positions,
        "open_time": [1704067200000 + i * 3600000 for i in range(len(prices))],
        "close_time": [1704070799999 + i * 3600000 for i in range(len(prices))],
    })


class ExecutionModelTests(unittest.TestCase):
    def test_trades_use_close_price_of_signal_row(self):
        """Izvršenje: kupnja i prodaja izvršavaju se po cijeni zatvaranja retka na kojem je signal."""
        result = run_backtest(market([100, 110, 120, 130], [1, 0, -1, 0]))
        self.assertEqual([(t["type"], t["price"]) for t in result["trades"]], [("BUY", 100.0), ("SELL", 120.0)])

    def test_whole_balance_is_invested_and_returned(self):
        """Izvršenje: pri kupnji se ulaže cijeli kapital, a prodaja zatvara cijelu poziciju."""
        result = run_backtest(market([100, 120], [1, -1]), initial_balance=5000)
        self.assertEqual(result["final_balance"], 6000)
        self.assertEqual(result["return_pct"], 20)

    def test_repeated_buy_or_sell_signals_are_ignored(self):
        """Izvršenje: samo long pozicija; ponovljena kupnja ili prodaja bez pozicije se ignorira."""
        result = run_backtest(market([100, 90, 80, 120, 110], [-1, 1, 1, -1, -1]))
        self.assertEqual([(t["type"], t["price"]) for t in result["trades"]], [("BUY", 90.0), ("SELL", 120.0)])

    def test_open_position_is_force_closed_at_last_close(self):
        """Kraj razdoblja: otvorena pozicija zatvara se po posljednjoj cijeni i označava se."""
        result = run_backtest(market([100, 90, 95], [1, 0, 0]))
        final = result["trades"][-1]
        self.assertEqual((final["type"], final["price"], final["is_final_close"]), ("SELL", 95.0, True))
        self.assertTrue(result["had_open_position_at_end"])
        self.assertEqual(result["number_of_trades"], 1)
        self.assertEqual(result["return_pct"], -5)

    def test_position_closed_by_signal_is_not_marked_as_open_at_end(self):
        """Kraj razdoblja: pozicija zatvorena signalom nije označena kao otvorena na kraju."""
        result = run_backtest(market([100, 110, 105], [1, -1, 0]))
        self.assertFalse(result["had_open_position_at_end"])
        self.assertFalse(any(t["is_final_close"] for t in result["trades"]))

    def test_trade_times_match_market_rows(self):
        """Izvršenje: vrijeme i redak svake transakcije odgovaraju OHLCV zapisu, i kod završnog zatvaranja."""
        df = market([0.00123456, 0.00234567, 0.00156789, 0.00256789], [1, -1, 1, 0])
        result = run_backtest(df)
        self.assertEqual([t["candle_index"] for t in result["trades"]], [0, 1, 2, 3])
        for trade in result["trades"]:
            row = df.iloc[trade["candle_index"]]
            self.assertEqual(trade["timestamp"], int(row["close_time"]))
            self.assertEqual(trade["price"], row["close"])
        self.assertTrue(result["trades"][-1]["is_final_close"])
        json.dumps(result, allow_nan=False)


class MetricsTests(unittest.TestCase):
    def test_return_is_relative_to_initial_balance(self):
        """Metrike: povrat je postotna promjena u odnosu na početni kapital."""
        result = run_backtest(market([200, 150], [1, -1]), initial_balance=10000)
        self.assertEqual((result["final_balance"], result["return_pct"]), (7500, -25))

    def test_max_drawdown_is_largest_drop_from_previous_peak(self):
        """Metrike: najveći pad je najveći postotni pad vrijednosti portfelja od prethodnog vrha."""
        result = run_backtest(market([100, 120, 90, 130], [1, 0, 0, -1]))
        self.assertEqual(result["max_drawdown_pct"], 25)

    def test_win_rate_counts_winning_and_losing_trades(self):
        """Metrike: stopa dobitnih transakcija broji i gubitne transakcije."""
        result = run_backtest(market([100, 110, 100, 90], [1, -1, 1, -1]))
        self.assertEqual([t["profit_pct"] for t in result["trades"] if t["type"] == "SELL"], [10, -10])
        self.assertEqual(result["win_rate_pct"], 50)
        self.assertEqual(result["number_of_trades"], 2)

    def test_forced_final_close_counts_as_trade_in_metrics(self):
        """Metrike: prisilno zatvaranje na kraju ulazi u broj transakcija i stopu dobitnih."""
        result = run_backtest(market([100, 110, 100, 105], [1, -1, 1, 0]))
        self.assertEqual(result["number_of_trades"], 2)
        self.assertEqual(result["win_rate_pct"], 100)

    def test_without_trades_metrics_are_zero(self):
        """Metrike: bez transakcija povrat, pad i stopa dobitnih iznose 0."""
        result = run_backtest(market([100, 50, 150], [0, 0, 0]))
        self.assertEqual(
            (result["return_pct"], result["max_drawdown_pct"], result["win_rate_pct"], result["number_of_trades"]),
            (0, 0, 0, 0),
        )


class InputTests(unittest.TestCase):
    def test_rejects_zero_capital_and_empty_data(self):
        """Ulazi: backtester odbija početni kapital 0 i prazne tržišne podatke."""
        with self.assertRaises(ValidationError):
            run_backtest(market([100], [0]), initial_balance=0)
        with self.assertRaises(ValidationError):
            run_backtest(pd.DataFrame(), initial_balance=10000)


if __name__ == "__main__":
    unittest.main()
