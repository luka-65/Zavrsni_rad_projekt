from flask import Blueprint
from database.db import (get_all_simulations, get_dashboard_stats, get_best_backtest, get_simulation_by_id, delete_simulation)

simulations_bp = Blueprint("simulations", __name__)

@simulations_bp.route("/api/simulations", methods=["GET"])
def simulations():
    data = get_all_simulations()

    return {
        "status": "success",
        "records": len(data),
        "data": data
    }

@simulations_bp.route("/api/dashboard-stats", methods=["GET"])
def dashboard_stats():

    stats = get_dashboard_stats()

    return {
        "status": "success",
        "data": stats
    }

@simulations_bp.route("/api/best-backtest", methods=["GET"])
def best_backtest():

    data = get_best_backtest()

    return {
        "status": "success",
        "data": data
    }

@simulations_bp.route("/api/simulations/<int:simulation_id>", methods=["GET"])
def simulation_details(simulation_id):
    data = get_simulation_by_id(simulation_id)

    if data is None:
        return {
            "status": "error",
            "message": "Simulation not found"
        }, 404

    return {
        "status": "success",
        "data": data
    }

@simulations_bp.route("/api/simulations/<int:simulation_id>", methods=["DELETE"])
def remove_simulation(simulation_id):
    deleted = delete_simulation(simulation_id)

    if not deleted:
        return {
            "status": "error",
            "message": "Simulation not found"
        }, 404

    return {
        "status": "success",
        "message": "Simulation deleted"
    }
