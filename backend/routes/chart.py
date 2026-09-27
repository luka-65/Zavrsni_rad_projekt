from flask import Blueprint, request
from services.chart_service import (
    get_moving_average_chart,
    get_rsi_chart,
    get_bollinger_chart
)
from utils.errors import register_error_handlers
from utils.validation import parse_request_inputs

chart_bp = Blueprint("chart", __name__)
register_error_handlers(chart_bp)


def chart_result(strategy_key, builder):
    common, parameters = parse_request_inputs(request.args, strategy_key, include_balance=False)
    return builder(**common, **parameters)


@chart_bp.route("/api/chart/moving-average", methods=["GET"])
def moving_average_chart():
    return chart_result("moving-average", get_moving_average_chart)


@chart_bp.route("/api/chart/rsi", methods=["GET"])
def rsi_chart():
    return chart_result("rsi", get_rsi_chart)


@chart_bp.route("/api/chart/bollinger", methods=["GET"])
def bollinger_chart():
    return chart_result("bollinger", get_bollinger_chart)
