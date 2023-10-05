localDBConfig = {
    "host":                 "localhost",
    "port":                 "5432",
    "database":             "NATSInternal",
    "user":                 "postgres",
    "password":             "f.t0rres"
}

class Config:
    DEBUG = False
    APP_NAME = "NATSInternal"
    SECRET_KEY = "BackInBlackACDC"
    LOGGING = True
    CATCHING = True
    EMAIL = ""
    UPLOAD_FOLDER = "./app/static/upload"
    JSON_SORT_KEYS = False
    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem"
    TIME_ZONE = "Asia/Ho_Chi_Minh"

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = f"postgresql://{localDBConfig['user']}:{localDBConfig['password']}" \
                                        f"@{localDBConfig['host']}:{localDBConfig['port']}/" \
                                        f"{localDBConfig['database']}"
    SQLALCHEMY_ECHO = False
    
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:DMPu5pwzkSYbOFqKGPhf@containers-us-west-119.railway.app:7614/railway"
    SQLALCHEMY_ECHO = False