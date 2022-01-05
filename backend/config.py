from decouple import config
import os


class Config:
    SECRET_KEY = config("SECRET_KEY")


class DevConfig:
    MONGO_URI = f"mongodb://{config('SERVER_ADDRESS')}/{config('DB_NAME')}"
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProdConfig:
    pass


class TestConfig:
    pass
