import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase

logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_key_123")

# Configure SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///food_ordering.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'user_login'  

# Drop all tables and recreate them
with app.app_context():
    # Import models here to ensure they are registered
    from models import User, Restaurant, MenuItem, Order
    db.drop_all()  
    db.create_all()

    # Import routes after models to avoid circular imports
    from routes import init_sample_data
    init_sample_data()