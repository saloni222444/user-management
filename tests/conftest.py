import pytest

from app import create_app
from app.extensions import db as _db
from app.models.user import User


@pytest.fixture(scope="session")
def app():
    application = create_app("testing")

    db_uri = application.config["SQLALCHEMY_DATABASE_URI"]
    assert db_uri, (
        "No database configured for tests. Set TEST_DATABASE_URL (or DATABASE_URL) "
        "in your .env file."
    )
    # Safety net: this fixture calls create_all()/drop_all(). Refuse to run
    # against anything that isn't clearly a dedicated test database, so a
    # misconfigured .env can't wipe a real database.
    assert "test" in db_uri.lower(), (
        "TEST_DATABASE_URL must point at a database with 'test' in its name "
        "(e.g. users_test) - refusing to run tests against what looks like "
        "a non-test database."
    )

    with application.app_context():
        _db.create_all()

    # Deliberately not holding the app context open across the yield: doing
    # so would make Flask's test client reuse this context for every
    # request instead of pushing/popping its own, which skips
    # teardown_appcontext (and therefore session cleanup) after each
    # request and leaves connections open for the whole test run.
    yield application

    with application.app_context():
        _db.drop_all()


@pytest.fixture(autouse=True)
def _clean_db(app):
    """Ensure every test starts with an empty users table."""
    with app.app_context():
        _db.session.query(User).delete()
        _db.session.commit()
    yield


@pytest.fixture
def client(app):
    return app.test_client()
