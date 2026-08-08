from flask import Blueprint, request

from app.schemas.user_schema import validate_user_payload
from app.services import user_service
from app.utils.pagination import parse_pagination_params
from app.utils.responses import success_response

user_bp = Blueprint("users", __name__, url_prefix="/users")


@user_bp.route("", methods=["GET"])
def get_users():
    search = request.args.get("search", "").strip() or None
    page, limit = parse_pagination_params(request.args)

    result = user_service.list_users(search=search, page=page, limit=limit)
    return success_response(result["items"], pagination=result["pagination"])


@user_bp.route("", methods=["POST"])
def create_user():
    payload = request.get_json(silent=True) or {}
    data = validate_user_payload(payload)

    user = user_service.create_user(data)
    return success_response(user, status_code=201)


@user_bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = user_service.get_user_by_id(user_id)
    return success_response(user)
