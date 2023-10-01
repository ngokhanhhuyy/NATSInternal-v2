from flask import Flask
from app.config import Config
from flask_bcrypt import Bcrypt
import os


application = Flask(
    __name__,
    template_folder="views")
bcrypt = Bcrypt(application)

# Define application's configurations
application.config.from_object(Config)
application.json.sort_keys = False

# Routes
from app import controllers
from app.data.initial_data import initializeData
from app.data import initializeDatabase
initializeDatabase()
# initializeData()