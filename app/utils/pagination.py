from app.errors import ValidationAPIError

DEFAULT_PAGE = 1
DEFAULT_LIMIT = 10
MAX_LIMIT = 100


def parse_pagination_params(args):
    """Read page/limit from query args and validate them at the boundary.

    - page/limit must be plain positive integers (page >= 1, limit >= 1)
    - limit is silently capped at MAX_LIMIT so no one can request the
      entire table in one page
    """
    page_raw = args.get("page", str(DEFAULT_PAGE))
    limit_raw = args.get("limit", str(DEFAULT_LIMIT))

    try:
        page = int(page_raw)
        limit = int(limit_raw)
    except (TypeError, ValueError):
        raise ValidationAPIError("Invalid pagination parameters")

    if page < 1 or limit < 1:
        raise ValidationAPIError("Invalid pagination parameters")

    limit = min(limit, MAX_LIMIT)
    return page, limit
