"""Custom API exceptions and centralized JSON error handling.

Every error - expected (validation, not found, duplicate) or unexpected
(a bug, a DB outage) - is turned into the same JSON shape:
    {"success": false, "error": "..."}
so API clients never see Flask/Werkzeug's default HTML error pages.
"""

from flask import jsonify
from werkzeug.exceptions import HTTPException


class APIError(Exception):
    """Base class for all expected, application-raised API errors."""

    status_code = 500
    message = "Internal server error"

    def __init__(self, message=None, status_code=None):
        super().__init__(message or self.message)
        if message is not None:
            self.message = message
        if status_code is not None:
            self.status_code = status_code


class ValidationAPIError(APIError):
    status_code = 400


class NotFoundError(APIError):
    status_code = 404
    message = "User not found"


class DuplicateEmailError(APIError):
    status_code = 409
    message = "Email already exists"


def register_error_handlers(app):
    @app.errorhandler(APIError)
    def handle_api_error(err):
        return jsonify({"success": False, "error": err.message}), err.status_code

    @app.errorhandler(HTTPException)
    def handle_http_exception(err):
        # Covers routing-level errors Flask raises itself (404 on unknown
        # routes, 405 on wrong method, 400 on malformed request, etc.) so
        # they come back as JSON instead of Flask's default HTML page.
        messages = {
            400: "Bad request",
            404: "Resource not found",
            405: "Method not allowed",
        }
        message = messages.get(err.code, err.description or err.name)
        return jsonify({"success": False, "error": message}), err.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(err):
        # Anything not already handled above is a genuine bug - log the
        # full details server-side, but never leak them to the client.
        app.logger.exception("Unhandled exception")
        return jsonify({"success": False, "error": "Internal server error"}), 500
