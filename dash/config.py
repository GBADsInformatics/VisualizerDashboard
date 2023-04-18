"""Flask config."""
from os import environ, path

from dotenv import load_dotenv

BASE_DIR = path.abspath(path.dirname(__file__))
if path.exists("/.dockerenv"):
    # If we are running in a container, overwrite normal location
    BASE_DIR="/app"
load_dotenv(path.join(BASE_DIR, ".env"))


PROFILE_KEY = 'profile'
SECRET_KEY = environ.get('SECRET_KEY',"randomstringofcharacters")
JWT_PAYLOAD = 'jwt_payload'

class Config:
    # Flask config variables, uncomment for OAUTH login

    # General Config
    FLASK_APP = environ.get("FLASK_APP","wsgi.py")
    FLASK_ENV = environ.get("FLASK_ENV","production")
    # SECRET_KEY = environ.get("SECRET_KEY")

    DASH_BASE_URL = environ.get('DASH_BASE_URL','/dash')
    AUTH0_CALLBACK_URL = environ.get('AUTH0_CALLBACK_URL',DASH_BASE_URL+"/callback")
    # AUTH0_CLIENT_ID = environ.get('AUTH0_CLIENT_ID', None)
    # AUTH0_CLIENT_SECRET = environ.get('AUTH0_CLIENT_SECRET', None)
    # AUTH0_DOMAIN = environ.get('AUTH0_DOMAIN',"test-auth0-test1.us.auth0.com")
    # AUTH0_BASE_URL = 'https://' + AUTH0_DOMAIN
    # AUTH0_AUDIENCE = environ.get('AUTH0_AUDIENCE', None)