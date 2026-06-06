from flask import Blueprint, request
from services.symbols_service import search_symbols

symbols_bp = Blueprint("symbols", __name__)

@symbols_bp.route("/api/symbols/search", methods=["GET"])
def search():
    query = request.args.get("query", "")

    data = search_symbols(query)

    return {
        "status": "success",
        "records": len(data),
        "data": data
    }