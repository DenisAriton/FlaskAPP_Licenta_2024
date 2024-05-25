"""This is the configuration file for my Flask application."""
import os
from dotenv import load_dotenv

# Preluam calea absoluta catre acest modul
abs_path_to_config = os.path.abspath(os.path.dirname(__file__))
# Incarcam variabilele de sistem localizate in .env
load_dotenv(os.path.join(abs_path_to_config, ".env"))


class Config(object):
    """
        The basic configuration for the application using an .env file!
        * mysql - este engine de rulare a bazei de date
        * pymysql - este un driver fara care nu va merge conexiunea la db
        * exista si engine mariadb si mariadbconnector ca driver
    """
    # Absolute path for application repository
    ABS_PATH_TO_REPO = abs_path_to_config
    # Flask Config
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-SQLAlchemy Config
    SQLALCHEMY_DATABASE_URI = os.environ.get('DB_URL')

    # Account for admin
    ADMIN_ID = os.environ.get('ADMIN_ID')
    ADMIN_PASSWORD = os.environ.get('ADMIM_PASSWORD')

    # Directories which has to be created at initialization
    ABS_UPLOADS_PATH = os.path.join(abs_path_to_config, "Uploads")
    DATASETS_PATH = os.path.join(ABS_UPLOADS_PATH, "Datasets")
    IMG_PATH = os.path.join(ABS_UPLOADS_PATH, "Profile_Img")
