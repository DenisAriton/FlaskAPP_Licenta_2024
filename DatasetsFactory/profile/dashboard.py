from flask import Blueprint, render_template, flash, url_for, redirect, send_from_directory, jsonify, request
from flask_login import login_required, current_user
from DatasetsFactory.forms import ImageProfile, ResetPassword, ProfileForm
from DatasetsFactory import db, app
from DatasetsFactory.models import UserIdentification
from datetime import datetime
import os
import uuid

# Crearea blueprintului pentru modulul views, primul argument este denumirea blueprintului,
# iar __name__ va returna modulul din care face parte
profile_blueprint = Blueprint('Profile', __name__)


@profile_blueprint.route('profile/<firstname>/<lastname>', methods=['GET', 'POST'])
@login_required
def profile(firstname, lastname):
    image_form = ImageProfile()
    profile_form = ProfileForm()
    print(f'Image submit: {image_form.image_up.data}')
    if image_form.image_up.data is not None:
        print("Submit image success!")
        if image_form.validate_on_submit():
            # preluam imaginea incarcata in formular
            img_data = image_form.image_up.data
            # prelucram numele imaginii(eliminare spatii goale... etc.) si ii adaugam un id unic
            # img_name = str(uuid.uuid4()) + "_" + secure_filename(img_data.filename)
            img_name = str(uuid.uuid4()) + os.path.splitext(img_data.filename)[1]
            # Consultam db daca mai exista vreo imagine cu un astfel de nume
            img_db = db.session.execute(db.select(UserIdentification).filter_by(ImageName=img_name)).first()
            # Vedem daca user-ul logat detine o imagine sau nu!
            img_user = current_user.ImageName
            # Cream calea absoluta pana la imagine
            path_to_img = os.path.join(app.config['IMG_PATH'], img_name)
            # Daca user-ul nu are o imagine atribuita
            if not img_user:
                # Daca numele imaginii este unic facem insert
                if img_db is None:
                    # Inseram numele imaginii in baza de date
                    current_user.ImageName = img_name
                    db.session.commit()
                    # Salvam imaginea local
                    img_data.save(path_to_img)
                    flash('Your image has been changed!', category="success")
                    # Refresh la pagina ca sa se vada imaginea
                    return redirect(url_for('Profile.profile', firstname=firstname, lastname=lastname))
                else:
                    flash('Change the name of the image!', category="error")
            else:
                # Daca user-ul are deja o imagine atribuita atunci facem update
                # Stergem imaginea anterioara si o inlocuim cu cea noua
                # Apoi facem update pe db cu numele imaginii noi
                path_img = os.path.join(app.config['IMG_PATH'], img_user)
                os.remove(path_img)
                #  Update-ul in baza de date
                img_data.save(path_to_img)
                current_user.ImageName = img_name
                db.session.commit()
                # Refresh la pagina ca sa se vada imaginea in front-end
                return redirect(url_for('Profile.profile', firstname=firstname, lastname=lastname))

    elif profile_form.submit.data:
        print(f'Profile submit: {profile_form.submit.data}')
        if profile_form.validate_on_submit():
            # TODO: Mai trebuie sa verificam ca datele sa nu fie nule, pentru a putea modifica doar una cele 3 inputuri
            first_data = profile_form.firstname.data
            last_data = profile_form.lastname.data
            email = profile_form.email.data
            current_user.firstName = first_data
            current_user.lastName = last_data
            current_user.email = email
            current_user.timeReset = datetime.now()
            db.session.commit()
            flash('Your profile has been updated!', category="success")
            return redirect(url_for('Profile.profile', firstname=current_user.firstName, lastname=current_user.lastName))

    return render_template('profile/Dashboard.html',
                           cur_object=current_user,
                           firstname=firstname,
                           lastname=lastname,
                           image_form=image_form,
                           profile_form=profile_form)


@profile_blueprint.route('serving/image/<filename>', methods=['GET'])
@login_required
def serving_image(filename):
    return send_from_directory(app.config["IMG_PATH"], filename)


@profile_blueprint.route('delete-image', methods=['POST'])
@login_required
def delete_image():
    # Preluam numele imaginii trimis prin JS
    data_js = request.json
    if data_js is not None:
        # Cautam care user detine imaginea
        user_img = UserIdentification.query.filter_by(ImageName=data_js).first()
        if user_img is not None:
            user_img.ImageName = None
            db.session.commit()
            os.remove(os.path.join(app.config['IMG_PATH'], data_js))
            return jsonify({"good": True})
    else:
        return jsonify({"noimage": True})


@profile_blueprint.route('ResetPassword', methods=['GET', 'POST'])
@login_required
def reset_password():
    reset_form = ResetPassword()
    if reset_form.validate_on_submit():
        current_user.set_password(reset_form.new_password.data)
        current_user.timeReset = datetime.now()
        db.session.commit()
        flash('Your password has been changed!', category="success")
        return redirect(url_for('Profile.profile', firstname=current_user.firstName, lastname=current_user.lastName))
    return render_template('profile/ResetPassword.html', cur_object=current_user, reset_form=reset_form)
