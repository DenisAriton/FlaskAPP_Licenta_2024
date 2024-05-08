from flask import Blueprint, render_template, flash, url_for, redirect
from flask_login import login_required, current_user
from datasets_handler.forms import ResetPassword, ImageProfile
from werkzeug.utils import secure_filename
from datasets_handler import db
from datasets_handler.models import UserImage
import os
import uuid

# Crearea blueprintului pentru modulul views, primul argument este denumirea blueprintului,
# iar __name__ va returna modulul din care face parte
profile_blueprint = Blueprint('Profile', __name__)


@profile_blueprint.route('profile/<firstname>/<lastname>', methods=['GET', 'POST'])
@login_required
def profile(firstname, lastname):
    reset_form = ResetPassword()
    image_form = ImageProfile()
    if image_form.validate_on_submit():
        # preluam imaginea incarcata
        img_data = image_form.image_up.data
        # prelucram numele imaginii(eliminare spatii goale... etc.) si ii adaugam un id unic
        img_name = str(uuid.uuid4()) + "_" + secure_filename(img_data.filename)
        # Consultam daca mai exista vreo imagine cu un astfel de nume
        img_db = UserImage.query.filter_by(ImageName=img_name).first()
        # Vedem daca user-ul logat detine o imagine sau nu!
        img_user = current_user.image
        print(f'Id-ul imaginii atribuite user-ului {img_user}')
        # Daca user-ul nu are o imagine atribuita
        if not img_user:
            # Daca numele imaginii este unic facem insert
            if img_db is None:
                # Inseram numele imaginii in baza de date
                insert_img = UserImage(ImageName=img_name, idUser=current_user.idUser)
                db.session.add(insert_img)
                db.session.commit()
                # Salvam imaginea local
                img_data.save(os.path.join(os.path.dirname(__file__), 'static\\images', img_name))
                flash('Your image has been changed!', category="success")
                print(f'User-ul cu imaginea: {current_user.image} ')
                # Refresh la pagina ca sa se vada imaginea
                return redirect(url_for('views.profile', firstname=firstname, lastname=lastname))
            else:
                flash('Change the name of the image!', category="error")
        else:
            # Daca user-ul are deja o imagine atribuita atunci facem update
            # Stergem imaginea anterioara si o inlocuim cu cea noua
            # Apoi facem update pe db cu numele imaginii noi
            print("Suntem in cazul in care exista ceva!")
            os.remove(os.path.join(os.path.dirname(__file__), 'static\\images', img_user[0].ImageName))
            #  Update-ul in baza de date
            img_data.save(os.path.join(os.path.dirname(__file__), 'static\\images', img_name))
            img_user[0].ImageName = img_name
            db.session.commit()
            # Refresh la pagina ca sa se vada imaginea in front-end
            return redirect(url_for('Profile.profile', firstname=firstname, lastname=lastname))

    # Resetarea parolei, cauta AJAX, pentru a corecta inchiderea modalului dupa submit!
    # Probabil mutam intr-o functie de view separata!
    if reset_form.validate_on_submit():
        # preluam noua parola din formular
        new_password = reset_form.new_password.data
        # apelam methoda clasei pentru a fi hashuita si stocata
        current_user.set_password(new_password)
        # facem commit sa se poata incarca datele
        db.session.commit()
        flash('Your password has been updated!', category='success')

    return render_template('profile.html', cur_object=current_user, firstname=firstname, lastname=lastname,
                           reset_form=reset_form, image_form=image_form)
