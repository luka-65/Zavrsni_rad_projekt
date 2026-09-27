from flask import Blueprint, request
from database.db import save_simulation
from services.backtest_service import (
    run_moving_average, run_rsi, run_bollinger, compare_strategies,
)
from utils.errors import register_error_handlers
from utils.validation import parse_backtest_body, parse_request_inputs

backtest_bp = Blueprint("backtest", __name__)
register_error_handlers(backtest_bp)

STRATEGIES = {
    "moving-average": ("Moving Average Crossover", run_moving_average),
    "rsi": ("Relative Strength Index", run_rsi),
    "bollinger": ("Bollinger Bands", run_bollinger),
}


@backtest_bp.route("/api/backtests", methods=["POST"])
def create_backtest():
    strategy_key, common, parameters = parse_backtest_body(request.get_json(silent=True))
    strategy_name, runner = STRATEGIES[strategy_key]
    result = runner(**common, **parameters)
    simulation_id = save_simulation(strategy_name, common["symbol"], common["interval"], result,
                                    common["start_date"], common["end_date"], parameters)
    return {
        "status": "success",
        "id": simulation_id,
        "strategy": strategy_name,
        "symbol": common["symbol"],
        "interval": common["interval"],
        "start_date": common["start_date"],
        "end_date": common["end_date"],
        "parameters": parameters,
        "result": result,
    }, 201, {"Location": f"/api/simulations/{simulation_id}"}


@backtest_bp.route("/api/backtests/compare", methods=["GET"])
def compare():
    common, _ = parse_request_inputs(request.args)
    results = compare_strategies(**common)
    return {
        "status": "success",
        "symbol": common["symbol"],
        "interval": common["interval"],
        "start_date": common["start_date"],
        "end_date": common["end_date"],
        "initial_balance": common["initial_balance"],
        "results": results,
    }
