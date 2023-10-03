from flask import Flask
from app.config import Config, ProductionConfig, DevelopmentConfig
from flask_bcrypt import Bcrypt
import os


application = Flask(
    __name__,
    template_folder="views")
bcrypt = Bcrypt(application)
# Define application's configurations
application.config.from_object(Config)
# Determine database connection string
if os.getenv("FLASK_ENV") == "development":
    application.config["SQLALCHEMY_DATABASE_URI"] = DevelopmentConfig.SQLALCHEMY_DATABASE_URI
elif os.getenv("FLASK_ENV") == "production":
    application.config["SQLALCHEMY_DATABASE_URI"] = ProductionConfig.SQLALCHEMY_DATABASE_URI
else:
    raise ValueError
application.json.sort_keys = False

# Routes
from app import controllers
from app.data.initial_data import initializeData
from app.data import initializeDatabase
initializeDatabase()
# initializeData()