"""The initialization file for the application."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from config import Config


class Base(DeclarativeBase):
    pass


# instance_relative_config=False inseamna ca modulul config.py nu se afla la nivelul aplicatiei in folderul instance, ci il va
# cauta in radacina aplicatiei, adica in repository FlaskAPP_Licenta_2024 in acest caz
app = Flask(__name__, instance_relative_config=False)
csrf_val = CSRFProtect()
db = SQLAlchemy(model_class=Base, disable_autonaming=True)
log_manager = LoginManager()


def create_app():
    """
    The application factory.
    :return: app
    """
    # Incarcam configurarile din clasa Config necesare initializarii aplicatiei Flask
    app.config.from_object(Config)
    # Initializarea SQLALchemy - se creeaza engine-ul pe baza URI-ului
    db.init_app(app)
    # Initializam CSRFProtect pentru a ne gestiona token-urile pentru formulare
    csrf_val.init_app(app)

    # Inregistrarea blueprinturilor aplicatiei
    from .authentication import login, signup
    from .views import routes
    from DatasetsFactory.profile import dashboard
    from DatasetsFactory.datasets import datasets
    from DatasetsFactory.administrator import admin
    app.register_blueprint(login.login_blueprint, url_prefix='/')
    app.register_blueprint(signup.signup_blueprint, url_prefix='/authentication')
    app.register_blueprint(routes.routes_blueprint, url_prefix='/routes')
    app.register_blueprint(dashboard.profile_blueprint, url_prefix='/dashboard')
    app.register_blueprint(datasets.datasets_blueprint, url_prefix='/datasets')
    app.register_blueprint(admin.admin_blueprint, url_prefix='/admin')

    # Cream baza de date cu toate tabelele definite in ORM-ul models
    from .models import (UserIdentification, UserSession, DataFiles, LogFile, FileAccess, UserGroup, Groups, Datasets,
                         FilesInDataset)
    with app.app_context():
        db.create_all()

        # Cream contul de admin - pentru acest insert avem nevoie de un context_app, deoarece nu avem un request anume in sesiune
        from .usefull import CreateAdmin, CreateDirectory
        admin_obj = CreateAdmin(admin_id=app.config["ADMIN_ID"], admin_pw=app.config["ADMIN_PASSWORD"])
        admin_obj.set_admin()

    # Initializarea login_managerului se face dupa crearea bazei de date !
    log_manager.init_app(app)
    log_manager.blueprint_login_views = {"Login": "login"}

    # Se creeaza folder-ul Uploads cu ierarhia specifica acestuia: Uploads/datasets si Uploads/profile_img
    for key, el in app.config.items():
        if key == "DATASETS_PATH" or key == "IMG_PATH" or key == "ABS_UPLOADS_PATH":
            dir_maker = CreateDirectory(path=el)
            dir_maker.make_folder()

    # Afisam dictionarul app.config sa vedem valorile - debugging doar
    # for key, el in app.config.items():
    #     print(f'{key}: {el}')

    return app
