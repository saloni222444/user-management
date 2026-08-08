from flask_sqlalchemy import SQLAlchemy

# Single shared SQLAlchemy instance, initialized against the app in create_app().
db = SQLAlchemy()
