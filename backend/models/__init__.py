# Initialize the models package
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models after defining db to avoid circular imports
from .db_models import User, Notification, Invoice  # Import your models here
