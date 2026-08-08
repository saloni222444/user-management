from flask import jsonify


def success_response(data, status_code=200, pagination=None):
    """Build the standard success envelope: {"success": true, "data": ...}."""
    body = {"success": True, "data": data}
    if pagination is not None:
        body["pagination"] = pagination
    return jsonify(body), status_code
