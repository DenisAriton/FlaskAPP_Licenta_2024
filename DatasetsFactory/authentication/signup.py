from flask import Blueprint, render_template, flash, redirect, url_for
from DatasetsFactory.models import UserIdentification
from DatasetsFactory import db
from DatasetsFactory.forms import SignUpForm
from flask_login import current_user

signup_blueprint = Blueprint('Signup', __name__)


@signup_blueprint.route('signup', methods=['GET', 'POST'])
def signup():
    form_auth = SignUpForm()
    # aceasta functie verifica un POST request valid, in caz contrat returneaza False
    if form_auth.validate_on_submit():
        # preluam datele din formular
        fname = form_auth.firstname.data
        lname = form_auth.lastname.data
        username = form_auth.username.data
        email = form_auth.email.data
        keypas1 = form_auth.password.data

        # Initializam clasa corespunzatoare tabelului din DB cu valorile introduse in formular
        # new_user = UserIdentification(firstName=fname, lastName=lname, userName=username, email=email, keyRole=0)
        # Keyrole se va asigna direct din db, default User
        new_user = UserIdentification(firstName=fname, lastName=lname, userName=username, email=email)  # type: ignore[call-arg]
        new_user.set_password(key=keypas1)
        # introducem datele in baza de date
        db.session.add(new_user)
        db.session.commit()
        flash('Your account has been successfully created!', category='success')
        return redirect(url_for('Login.login'))

    return render_template('authentication/signup.html', form_auth=form_auth, cur_object=current_user)
