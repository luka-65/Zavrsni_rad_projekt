from flask import Blueprint
from database.db import get_all_simulations

simulations_bp = Blueprint("simulations", __name__)

@simulations_bp.route("/api/simulations", methods=["GET"])
def simulations():
    data = get_all_simulations()

    return {
        "status": "success",
        "records": len(data),
        "data": data
    }