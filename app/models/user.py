from app.extensions import db


class User(db.Model):
    """Maps to the `users` table. The UNIQUE constraint on email is the
    source of truth for uniqueness - the service layer also checks it
    up front so callers get a clean 409 instead of a raw DB error."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    role = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
        }
