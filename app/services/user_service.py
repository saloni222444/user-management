from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError

from app.errors import DuplicateEmailError, NotFoundError
from app.extensions import db
from app.models.user import User


def list_users(search=None, page=1, limit=10):
    """Return a page of users, optionally filtered by name/email search.

    Filtering and pagination both happen at the database level (SQL WHERE
    + LIMIT/OFFSET via .paginate()) so we never pull the whole table into
    memory just to slice it.
    """
    query = User.query

    if search:
        term = f"%{search}%"
        query = query.filter(
            or_(
                func.lower(User.name).like(func.lower(term)),
                func.lower(User.email).like(func.lower(term)),
            )
        )

    query = query.order_by(User.id.asc())
    result = query.paginate(page=page, per_page=limit, error_out=False)

    return {
        "items": [user.to_dict() for user in result.items],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": result.total,
            "pages": result.pages,
        },
    }


def get_user_by_id(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        raise NotFoundError("User not found")
    return user.to_dict()


def create_user(data):
    """Create a user. Duplicate emails are rejected two ways:

    1. An upfront lookup, for a fast, friendly 409 in the common case.
    2. A try/except around the commit, so a race between two concurrent
       requests still can't create two rows with the same email - the
       database's UNIQUE constraint is the real guarantee.
    """
    existing = User.query.filter(func.lower(User.email) == data["email"]).first()
    if existing is not None:
        raise DuplicateEmailError()

    user = User(name=data["name"], email=data["email"], role=data["role"])
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise DuplicateEmailError()

    return user.to_dict()
