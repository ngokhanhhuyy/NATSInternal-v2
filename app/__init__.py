from flask import Flask
from app.config import Config, ProductionConfig, DevelopmentConfig
from flask_bcrypt import Bcrypt
import os


application = Flask(__name__)
bcrypt = Bcrypt(application)
# Define application's configurations
application.config.from_object(Config)
# Determine database connection string
if os.getenv("FLASK_ENV") == "production":
    application.config["SQLALCHEMY_DATABASE_URI"] = ProductionConfig.SQLALCHEMY_DATABASE_URI
    application.config["SQLALCHEMY_ECHO"] = ProductionConfig.SQLALCHEMY_ECHO
else:
    application.config["SQLALCHEMY_DATABASE_URI"] = DevelopmentConfig.SQLALCHEMY_DATABASE_URI
    application.config["SQLALCHEMY_ECHO"] = DevelopmentConfig.SQLALCHEMY_ECHO
application.json.sort_keys = False

# Routes
from app import controllers
from app.data.initial_data import initializeData
from app.data import initializeDatabase
initializeDatabase()
# initializeData()