def run_backtest(df, initial_balance=10000):

    balance = initial_balance
    position = 0
    buy_price = 0

    trades = []
    equity_curve = []

    for _, row in df.iterrows():

        current_price = row["close"]

        if row["position"] == 1 and position == 0:
            buy_price = current_price
            position = balance / buy_price
            balance = 0

            trades.append({
                "type": "BUY",
                "price": round(buy_price, 2),
                "profit_pct": None
            })

        elif row["position"] == -1 and position > 0:
            sell_price = current_price
            balance = position * sell_price
            position = 0

            profit_pct = ((sell_price - buy_price) / buy_price) * 100

            trades.append({
                "type": "SELL",
                "price": round(sell_price, 2),
                "profit_pct": round(profit_pct, 2)
            })

        current_equity = balance

        if position > 0:
            current_equity = position * current_price

        equity_curve.append(current_equity)

    if position > 0:
        final_price = df.iloc[-1]["close"]
        balance = position * final_price

    final_balance = balance

    return_pct = ((final_balance - initial_balance) / initial_balance) * 100

    max_drawdown = calculate_max_drawdown(equity_curve)
    win_rate = calculate_win_rate(trades)

    return {
        "initial_balance": round(initial_balance, 2),
        "final_balance": round(final_balance, 2),
        "return_pct": round(return_pct, 2),
        "max_drawdown_pct": round(max_drawdown, 2),
        "win_rate_pct": round(win_rate, 2),
        "number_of_trades": len([t for t in trades if t["type"] == "SELL"]),
        "trades": trades
    }


def calculate_max_drawdown(equity_curve):

    peak = equity_curve[0]
    max_drawdown = 0

    for equity in equity_curve:
        if equity > peak:
            peak = equity

        drawdown = ((peak - equity) / peak) * 100

        if drawdown > max_drawdown:
            max_drawdown = drawdown

    return max_drawdown


def calculate_win_rate(trades):

    sell_trades = [
        trade for trade in trades
        if trade["type"] == "SELL"
    ]

    if len(sell_trades) == 0:
        return 0

    winning_trades = [
        trade for trade in sell_trades
        if trade["profit_pct"] > 0
    ]

    return (len(winning_trades) / len(sell_trades)) * 100