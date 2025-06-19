from flask import Flask
from models import db
from config import DATABASE_URI
from flask_migrate import Migrate, upgrade

def init_db():
    """Initialize the database with migrations"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    migrate = Migrate(app, db)
    
    with app.app_context():
        upgrade()

if __name__ == '__main__':
    init_db()
