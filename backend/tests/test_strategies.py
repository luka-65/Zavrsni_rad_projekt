import math
import unittest

import pandas as pd

from backtesting.backtester import run_backtest
from strategies.bollinger import bollinger_bands_strategy
from strategies.moving_average import moving_average_strategy
from strategies.rsi import rsi_strategy


def run(strategy, prices, **params):
    return strategy(pd.DataFrame({"close": prices}), **params)


def buys(df):
    return df.index[df["position"] == 1].tolist()


def sells(df):
    return df.index[df["position"] == -1].tolist()


CROSSING_PRICES = [10, 9, 8, 7, 8, 10, 12, 11, 9, 7, 6]


class MovingAverageTests(unittest.TestCase):
    def test_buy_when_short_average_crosses_above_long(self):
        """MA: kupnja nastaje kad kratki prosjek prijeđe iznad dugog."""
        df = run(moving_average_strategy, CROSSING_PRICES, short_window=2, long_window=4)
        self.assertEqual(buys(df), [5])
        self.assertAlmostEqual(df["MA_SHORT"].iloc[5], 9.0)
        self.assertAlmostEqual(df["MA_LONG"].iloc[5], 8.25)

    def test_sell_when_short_average_crosses_below_long(self):
        """MA: prodaja nastaje kad kratki prosjek padne ispod dugog."""
        df = run(moving_average_strategy, CROSSING_PRICES, short_window=2, long_window=4)
        self.assertEqual(sells(df), [8])
        result = run_backtest(df)
        self.assertEqual([(t["type"], t["price"]) for t in result["trades"]], [("BUY", 10.0), ("SELL", 9.0)])
        self.assertFalse(result["trades"][-1]["is_final_close"])

    def test_no_signal_before_long_average_exists(self):
        """MA: nema signala dok dugi prosjek nema dovoljno podataka."""
        df = run(moving_average_strategy, CROSSING_PRICES, short_window=2, long_window=4)
        self.assertTrue(df["MA_LONG"].iloc[:3].isna().all())
        self.assertTrue((df["signal"].iloc[:3] == 0).all())

    def test_enters_immediately_when_short_average_is_already_above(self):
        """MA: ako je kratki prosjek već iznad dugog kad oba postoje, kupnja nastaje odmah."""
        df = run(moving_average_strategy, list(range(1, 11)), short_window=2, long_window=4)
        self.assertEqual(buys(df), [3])
        self.assertEqual(sells(df), [])

    def test_equal_averages_do_not_signal(self):
        """MA: jednaki prosjeci (ravne cijene) ne daju signal kupnje."""
        df = run(moving_average_strategy, [5.0] * 10, short_window=2, long_window=4)
        self.assertEqual(buys(df), [])
        self.assertEqual(run_backtest(df)["trades"], [])

    def test_repeated_crossings_open_and_close_positions_again(self):
        """MA: nakon prodaje novo križanje ponovno otvara poziciju."""
        prices = CROSSING_PRICES + [5, 4, 5, 7, 9, 8, 6, 4]
        df = run(moving_average_strategy, prices, short_window=2, long_window=4)
        self.assertEqual(buys(df), [5, 14])
        self.assertEqual(sells(df), [8, 17])
        result = run_backtest(df)
        self.assertEqual([t["type"] for t in result["trades"]], ["BUY", "SELL", "BUY", "SELL"])
        self.assertEqual(result["number_of_trades"], 2)
        self.assertFalse(result["had_open_position_at_end"])


class RsiTests(unittest.TestCase):
    def test_first_value_uses_exactly_period_price_changes(self):
        """RSI: prva vrijednost koristi točno `period` stvarnih promjena cijene."""
        df = run(rsi_strategy, [10, 11, 10, 12, 11, 13], period=3)
        self.assertTrue(df["RSI"].iloc[:3].isna().all())
        self.assertAlmostEqual(df["RSI"].iloc[3], 75.0)
        self.assertFalse(df["RSI"].iloc[3:].isna().any())

    def test_monotonic_rise_gives_rsi_100_without_nan(self):
        """RSI: cijena koja samo raste daje RSI 100 bez NaN vrijednosti."""
        df = run(rsi_strategy, list(range(100, 130)), period=14)
        self.assertTrue((df["RSI"].iloc[14:] == 100).all())
        self.assertTrue(df["RSI"].iloc[:14].isna().all())
        self.assertTrue((df["position"].fillna(0) == 0).all())

    def test_flat_prices_give_neutral_rsi_50_without_nan(self):
        """RSI: potpuno ravne cijene daju neutralni RSI 50 bez NaN vrijednosti."""
        df = run(rsi_strategy, [100.0] * 30, period=14)
        self.assertTrue((df["RSI"].iloc[14:] == 50).all())
        self.assertTrue((df["signal"] == 0).all())

    def test_flat_rsi_50_is_compared_like_any_other_value(self):
        """RSI: vrijednost 50 uspoređuje se s granicama kao i svaka druga."""
        df = run(rsi_strategy, [100.0] * 20, period=14, oversold=60, overbought=80)
        self.assertEqual(buys(df), [14])

    def test_monotonic_fall_gives_rsi_0_and_buy_signal(self):
        """RSI: cijena koja samo pada daje RSI 0 i signal kupnje."""
        df = run(rsi_strategy, list(range(130, 100, -1)), period=14)
        self.assertTrue((df["RSI"].iloc[14:] == 0).all())
        self.assertEqual(buys(df), [14])

    def test_rsi_stays_within_0_and_100(self):
        """RSI: vrijednost je uvijek između 0 i 100."""
        prices = [100, 100, 101, 101, 99, 99, 99, 103, 98, 98, 98, 98, 105, 90, 90]
        values = run(rsi_strategy, prices, period=3)["RSI"].iloc[3:]
        self.assertTrue(all(0 <= value <= 100 and not math.isnan(value) for value in values))

    def test_neutral_rows_preserve_state_and_allow_reentry(self):
        """RSI: vrijednosti između granica zadržavaju stanje, a nova preprodanost ponovno otvara poziciju."""
        prices = [100, 99, 98, 97, 98, 99, 100, 101, 100, 99, 98, 97, 98, 99, 100]
        df = run(rsi_strategy, prices, period=3)
        self.assertEqual(buys(df), [3, 10])
        self.assertEqual(sells(df), [6, 14])
        self.assertTrue((df.loc[[4, 5, 12, 13], "signal"] == 1).all())
        self.assertTrue((df.loc[[8, 9], "signal"] == 0).all())
        result = run_backtest(df)
        self.assertEqual(result["win_rate_pct"], 100)
        self.assertEqual(result["final_balance"], round(10000 * (100 / 97) * (100 / 98), 2))


class BollingerTests(unittest.TestCase):
    def test_bands_use_moving_average_and_sample_standard_deviation(self):
        """Bollinger: srednja ovojnica je pomični prosjek, a širina koristi uzoračku standardnu devijaciju."""
        df = run(bollinger_bands_strategy, [1.0, 2.0, 3.0], window=3, num_std=2)
        self.assertAlmostEqual(df["MA"].iloc[2], 2.0)
        self.assertAlmostEqual(df["STD"].iloc[2], 1.0)
        self.assertAlmostEqual(df["UPPER_BAND"].iloc[2], 4.0)
        self.assertAlmostEqual(df["LOWER_BAND"].iloc[2], 0.0)

    def test_buy_below_lower_band_and_sell_above_upper_band(self):
        """Bollinger: kupnja ispod donje ovojnice, prodaja iznad gornje."""
        prices = [100.0] * 20 + [50.0] + [100.0] * 20 + [150.0, 100.0]
        df = run(bollinger_bands_strategy, prices)
        self.assertEqual(buys(df), [20])
        self.assertEqual(sells(df), [41])
        self.assertLess(df["close"].iloc[20], df["LOWER_BAND"].iloc[20])
        self.assertGreater(df["close"].iloc[41], df["UPPER_BAND"].iloc[41])

    def test_neutral_rows_preserve_state_and_allow_reentry(self):
        """Bollinger: cijena unutar ovojnica zadržava stanje, a novi pad ispod donje ponovno otvara poziciju."""
        prices = [100, 100, 90, 91, 110, 100, 100, 90, 91, 110, 100]
        df = run(bollinger_bands_strategy, prices, window=3, num_std=1)
        self.assertEqual(buys(df), [2, 7])
        self.assertEqual(sells(df), [4, 9])
        self.assertTrue((df.loc[[3, 8], "signal"] == 1).all())
        self.assertTrue((df.loc[[5, 6, 10], "signal"] == 0).all())
        result = run_backtest(df)
        self.assertEqual(result["win_rate_pct"], 100)
        self.assertEqual(result["final_balance"], round(10000 * (110 / 90) ** 2, 2))

    def test_flat_prices_collapse_bands_without_signal(self):
        """Bollinger: ravne cijene daju ovojnice jednake cijeni i nijedan signal."""
        df = run(bollinger_bands_strategy, [100.0] * 25)
        self.assertTrue((df["STD"].iloc[19:] == 0).all())
        self.assertEqual(buys(df), [])


class SharedStrategyTests(unittest.TestCase):
    def test_signals_close_positions_before_end_of_period(self):
        """Sve strategije: signal prodaje zatvara poziciju prije kraja razdoblja."""
        cases = [
            (moving_average_strategy, CROSSING_PRICES, {"short_window": 2, "long_window": 4}, 9),
            (rsi_strategy, list(range(120, 99, -1)) + list(range(101, 132)), {}, 110),
            (bollinger_bands_strategy, [100.0] * 20 + [50.0] + [100.0] * 20 + [150.0, 100.0], {}, 150),
        ]
        for strategy, prices, params, sell_price in cases:
            with self.subTest(strategy=strategy.__name__):
                result = run_backtest(run(strategy, prices, **params))
                self.assertEqual([t["type"] for t in result["trades"]], ["BUY", "SELL"])
                self.assertEqual(result["trades"][-1]["price"], sell_price)
                self.assertFalse(result["trades"][-1]["is_final_close"])
                self.assertFalse(result["had_open_position_at_end"])
                self.assertEqual(result["number_of_trades"], 1)

    def test_no_trades_without_entry_signal(self):
        """Sve strategije: bez signala kupnje nema transakcija i kapital ostaje isti."""
        for strategy in (moving_average_strategy, rsi_strategy, bollinger_bands_strategy):
            for prices in ([100.0] * 60, [100.0] * 2):
                with self.subTest(strategy=strategy.__name__, rows=len(prices)):
                    result = run_backtest(run(strategy, prices))
                    self.assertEqual(result["trades"], [])
                    self.assertEqual(result["final_balance"], 10000)
                    self.assertEqual(result["number_of_trades"], 0)

    def test_open_position_is_closed_at_last_price_when_no_sell_signal(self):
        """Sve strategije: bez signala prodaje pozicija se zatvara po posljednjoj cijeni."""
        cases = [
            (moving_average_strategy, list(range(1, 11)), {"short_window": 2, "long_window": 4}),
            (rsi_strategy, list(range(120, 99, -1)), {}),
            (bollinger_bands_strategy, [100.0] * 20 + [50.0, 60.0], {}),
        ]
        for strategy, prices, params in cases:
            with self.subTest(strategy=strategy.__name__):
                result = run_backtest(run(strategy, prices, **params))
                self.assertEqual([t["type"] for t in result["trades"]], ["BUY", "SELL"])
                self.assertTrue(result["trades"][-1]["is_final_close"])
                self.assertEqual(result["trades"][-1]["price"], prices[-1])
                self.assertTrue(result["had_open_position_at_end"])

    def test_strategies_do_not_change_input_data(self):
        """Sve strategije: ulazni tržišni podaci ostaju nepromijenjeni."""
        for strategy in (moving_average_strategy, rsi_strategy, bollinger_bands_strategy):
            with self.subTest(strategy=strategy.__name__):
                data = pd.DataFrame({"close": [float(x) for x in range(60)]})
                strategy(data)
                self.assertEqual(list(data.columns), ["close"])


if __name__ == "__main__":
    unittest.main()
