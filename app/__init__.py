from flask import Flask
from app.config import configurations
from flask_bcrypt import Bcrypt

application = Flask(
    __name__,
    template_folder="views")
bcrypt = Bcrypt(application)

# Define application's configurations
application.config["DEBUG"] = configurations["debug"]
application.config["SECRET_KEY"] = configurations["secretKey"]
application.config["DATABASE_URI"] = configurations["databaseURI"]
application.config["LOGGING"] = configurations["logging"]
application.config["CATCHING"] = configurations["catching"]
application.config["EMAIL"] = configurations["email"]
application.config["UPDATE_FOLDER"] = configurations["uploadFolder"]
application.config["MAX_CONTENT_LENGTH"] = configurations["maxContentLength"]
application.config["SQLALCHEMY_DATABASE_URI"] = configurations["databaseURI"]
application.config['JSON_SORT_KEYS'] = False
application.config["SESSION_PERMANENT"] = False
application.config["SESSION_TYPE"] = "filesystem"
application.json.sort_keys = False


# Routes
from app import controllers
from app.data.initial_data import initializeData
from app.data import initializeDatabase
initializeDatabase()
# initializeData()