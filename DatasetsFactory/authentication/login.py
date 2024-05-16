from flask import Blueprint, render_template, flash, redirect, url_for
from DatasetsFactory.models import UserIdentification, UserSession
from sqlalchemy import func
from DatasetsFactory import db, log_manager
from DatasetsFactory.forms import LoginForm
from flask_login import login_user, logout_user, current_user, login_required
from DatasetsFactory.usefull import verify_format_email

# Bluenprint("nume_blueprint", __name__ - numele modulului)
login_blueprint = Blueprint('Login', __name__, template_folder='templates', static_folder='static')


@login_blueprint.route('', methods=['GET', 'POST'])
@login_blueprint.route('login', methods=['GET', 'POST'])
def login():
    form_log = LoginForm()
    # Daca este logat user-ul redirectioneaza-l direct catre home page
    if current_user.is_authenticated:
        name = current_user.firstName + current_user.lastName
        flash("You are already logged in!", category="success")
        return redirect(url_for('Routes.home', name=name))
    # Daca nu este logat, ramanem pe login page pentru autentificare
    elif form_log.validate_on_submit():
        userdata = form_log.username.data
        if verify_format_email(userdata):
            userdb = UserIdentification.query.filter_by(email=userdata).first()
            login_user(userdb)  # remeber=True pastreaza id-ul in sesiune pentru email-ul introdus, la fel si pentru username
        else:
            userdb = UserIdentification.query.filter_by(userName=userdata).first()
            login_user(userdb)
        # Tinem evidenta in baza de date a userului cand s-a conectat! Aceasta se face dupa login_user pentru a prelua
        # id-ul user-ului
        new_session = UserSession(idUser=current_user.idUser)
        db.session.add(new_session)
        db.session.commit()
        flash('You have been logged in!', category='success')
        name = current_user.firstName
        return redirect(url_for('Routes.home', name=name))

    return render_template('authentication/signin.html', form_log=form_log, cur_object=current_user)

# user_loader este o functie de apelare care este utilizata pentru a reincarca obiectul utilizatorului pe baza ID-ului
# stocat in sesiune (returneaza None nu exceptie! daca id-ul nu e valid)


@log_manager.user_loader
def load_user(user: int):
    """
    Se incarca id-ul user-ului din DB in momentul logarii!
    :param user: Trebuie sa fie int!
    :return: ID-ul user-ului sau None!
    """
    if user:
        return UserIdentification.query.get(user)
    else:
        return None


@log_manager.unauthorized_handler
def unauthorized():
    """
    Redirectioneaza utilizatorii ce nu sunt logati catre pagina de login pentru logare sau autentificare!
    :return: redirect to login
    """
    flash("You have to sign in first!", category="error")
    return redirect(url_for("Login.login"))


@login_blueprint.route('/logout', methods=['GET'])
@login_required
def logout():
    # Preluam lista de autentificari din relSession pe baza id-ului celui conectat si luam ultima autentificare
    if current_user.relSession:
        endtime = current_user.relSession[-1]
        endtime.endTime = func.current_timestamp()
        db.session.commit()
    else:
        pass
    logout_user()
    flash("You have been logged out!", category="success")
    return redirect(url_for('Login.login'))
