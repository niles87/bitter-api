import os
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())

class Config(object):
    TESTING = False
    
    
class Development(Config):
    ENV = os.getenv("ENV")
    DEVELOPMENT = os.getenv("DEVELOPMENT")
    SECRET_KEY = os.getenv("DEV_SECRET")
    
