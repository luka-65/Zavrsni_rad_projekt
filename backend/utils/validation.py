import math
import re
from datetime import datetime, timezone


MAX_RANGE_DAYS = {
    "1h": 90, "4h": 365, "1d": 1825, "1w": 3650, "1M": 3650,
}


class ValidationError(ValueError):
    pass


def validation_response(error):
    message = str(error)
    return {"status": "error", "message": message, "error": message}, 400


def positive_integer(value, name, minimum=1, maximum=None):
    if isinstance(value, bool) or not re.fullmatch(r"[0-9]+", str(value)):
        raise ValidationError(f"{name} mora biti cijeli broj najmanje {minimum}.")
    try:
        number = int(value)
    except (ValueError, OverflowError):
        raise ValidationError(f"{name} nije valjan cijeli broj.") from None
    if number < minimum or (maximum is not None and number > maximum):
        bound = f" između {minimum} i {maximum}" if maximum else f" najmanje {minimum}"
        raise ValidationError(f"{name} mora biti{bound}.")
    return number


def finite_number(value, name, positive=False):
    try:
        if isinstance(value, bool):
            raise ValueError
        number = float(value)
    except (ValueError, TypeError, OverflowError):
        raise ValidationError(f"{name} mora biti broj.") from None
    if not math.isfinite(number):
        raise ValidationError(f"{name} mora biti konačan broj.")
    if positive and number <= 0:
        raise ValidationError(f"{name} mora biti veći od 0.")
    return number


def validate_dates(interval, start_date, end_date):
    if start_date is None and end_date is None:
        return None, None
    if not start_date or not end_date:
        raise ValidationError("Potrebno je odabrati datum od i datum do.")
    parsed = []
    for value in (start_date, end_date):
        if not isinstance(value, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
            raise ValidationError("Datum mora biti u formatu YYYY-MM-DD.")
        try:
            parsed.append(datetime.strptime(value, "%Y-%m-%d").date())
        except ValueError:
            raise ValidationError("Datum nije valjan kalendarski datum.") from None
    start, end = parsed
    if end < start:
        raise ValidationError("Datum do ne može biti prije datuma od.")
    if end > datetime.now(timezone.utc).date():
        raise ValidationError("Datum do ne može biti u budućnosti.")
    if (end - start).days > MAX_RANGE_DAYS[interval]:
        raise ValidationError(
            f"Za interval {interval} moguće je odabrati najviše {MAX_RANGE_DAYS[interval]} dana."
        )
    return start_date, end_date


def validate_market_inputs(symbol, interval, limit, start_date=None, end_date=None):
    if not isinstance(symbol, str) or not re.fullmatch(r"[A-Z0-9]{2,30}", symbol):
        raise ValidationError("Simbol mora sadržavati 2–30 velikih slova ili znamenki, npr. BTCUSDT.")
    if not isinstance(interval, str) or interval not in MAX_RANGE_DAYS:
        raise ValidationError("Podržani intervali su 1h, 4h, 1d, 1w i 1M.")
    limit = positive_integer(limit, "limit", maximum=1000)
    start_date, end_date = validate_dates(interval, start_date, end_date)
    return dict(symbol=symbol, interval=interval, limit=limit,
                start_date=start_date, end_date=end_date)


STRATEGY_PARAMETERS = {
    "moving-average": ("short_window", "long_window"),
    "rsi": ("period", "oversold", "overbought"),
    "bollinger": ("window", "num_std"),
}

BACKTEST_FIELDS = {
    "symbol", "interval", "limit", "start_date", "end_date", "initial_balance", "strategy", "parameters",
}


def validate_strategy(strategy, parameters):
    if strategy == "moving-average":
        short = positive_integer(parameters.get("short_window", 20), "short_window")
        long = positive_integer(parameters.get("long_window", 50), "long_window")
        if short >= long:
            raise ValidationError("short_window mora biti manji od long_window.")
        return dict(short_window=short, long_window=long)
    if strategy == "rsi":
        period = positive_integer(parameters.get("period", 14), "period")
        oversold = finite_number(parameters.get("oversold", 30), "oversold")
        overbought = finite_number(parameters.get("overbought", 70), "overbought")
        if not 0 <= oversold < overbought <= 100:
            raise ValidationError("RSI granice moraju zadovoljiti 0 <= oversold < overbought <= 100.")
        return dict(period=period, oversold=oversold, overbought=overbought)
    if strategy == "bollinger":
        return dict(
            window=positive_integer(parameters.get("window", 20), "window", minimum=2),
            num_std=finite_number(parameters.get("num_std", 2), "num_std", positive=True),
        )
    raise ValidationError("Nepoznata strategija.")


def parse_request_inputs(values, strategy=None, include_balance=True, default_limit=200):
    if hasattr(values, "getlist"):
        for key in values:
            if len(values.getlist(key)) > 1:
                raise ValidationError(f"Parametar {key} smije biti naveden samo jednom.")
    common = validate_market_inputs(
        values.get("symbol", "BTCUSDT"), values.get("interval", "1d"),
        values.get("limit", default_limit), values.get("start_date"), values.get("end_date"),
    )
    if include_balance:
        common["initial_balance"] = finite_number(
            values.get("initial_balance", 10000), "initial_balance", positive=True
        )
    params = validate_strategy(strategy, values) if strategy else {}
    return common, params


def require_market_rows(df, minimum):
    if df.empty:
        raise ValidationError("Za odabrani simbol i razdoblje nema tržišnih podataka.")
    if len(df) < minimum:
        raise ValidationError(
            f"Nedovoljno tržišnih podataka: potrebno je najmanje {minimum} OHLCV zapisa, dostupno {len(df)}."
        )


def parse_backtest_body(body):
    if not isinstance(body, dict):
        raise ValidationError("Tijelo zahtjeva mora biti JSON objekt.")
    unknown = sorted(set(body) - BACKTEST_FIELDS)
    if unknown:
        raise ValidationError(f"Nepoznata polja zahtjeva: {', '.join(unknown)}.")

    strategy = body.get("strategy")
    if not isinstance(strategy, str) or strategy not in STRATEGY_PARAMETERS:
        raise ValidationError("strategy mora biti moving-average, rsi ili bollinger.")

    parameters = body.get("parameters", {})
    if not isinstance(parameters, dict):
        raise ValidationError("parameters mora biti JSON objekt.")
    unknown = sorted(set(parameters) - set(STRATEGY_PARAMETERS[strategy]))
    if unknown:
        raise ValidationError(f"Nepoznati parametri za strategiju {strategy}: {', '.join(unknown)}.")

    common, _ = parse_request_inputs(body)
    return strategy, common, validate_strategy(strategy, parameters)
