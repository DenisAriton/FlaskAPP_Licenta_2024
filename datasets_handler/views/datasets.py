from flask import Blueprint, render_template, flash, url_for, redirect
from flask_login import login_required, current_user
from datasets_handler.forms import UploadFile
from werkzeug.utils import secure_filename
from datasets_handler import db
from datasets_handler.models import DataFiles
import os
import uuid

# Crearea blueprintului pentru modulul views, primul argument este denumirea blueprintului,
# iar __name__ va returna modulul din care face parte
datasets_blueprint = Blueprint('Datasets', __name__)


@datasets_blueprint.route('upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    exist = True
    upload = UploadFile()
    print(upload.validate_on_submit())
    if upload.validate_on_submit():
        print('Dupa validare!')
        for file in upload.file_up.data:
            file_name = secure_filename(file.filename)
            # daca exista un fisier cu aceeasi denumire nu se va uploada
            file_db = DataFiles.query.filter_by(fileName=os.path.splitext(file_name)[0]).first()
            if file_db is None:
                # salvam fisierele in directorul uploads care se afla in directorul static
                # aflam calea absoluta catre acest modul
                file.save(os.path.join(os.path.dirname(__file__), 'static\\uploads', file_name))
                # introducem numele si extensia separat in db
                new_file = DataFiles(fileName=os.path.splitext(file_name)[0], format=os.path.splitext(file_name)[1])
                db.session.add(new_file)
                db.session.commit()
                flash('Your files has been uploaded!', category="success")
            else:
                exist = False
                flash('Change the name of the file!', category="error")
            # Mai facem odata query dupa ce s-a uploadat fisierul pentru ai putea adauga size-ul
            if exist is True:
                file_exist = DataFiles.query.filter_by(fileName=os.path.splitext(file_name)[0]).first()
                if file_exist:
                    # NU UITA: Doar dupa ce a urcat fisierul poti insera in db size, asa ca functia asta trebuie mutata de aici!!!
                    # cream denumirea fisierului cu tot cu extensie pentru a-i identifica marimea in MB sau KB
                    name = file_exist.fileName + file_exist.format
                    # preluam marimea fisierului in bytes
                    get_size = os.stat(os.path.join(os.path.dirname(__file__), 'static\\uploads', name)).st_size
                    #  convertim in KB
                    size = round(get_size / 1024)
                    # stocam in db datele
                    file_exist.size = size
                    file_exist.sizeUnit = 'KB'
                    db.session.add(file_exist)
                    db.session.commit()
            else:
                flash('Nu se incarca alte date despre fisier!', category="error")

    files_view = DataFiles.query.all()
    return render_template('upload.html', upload=upload, files_view=files_view, cur_object=current_user)


@datasets_blueprint.route('delete_file/<int:id_file>', methods=['GET', 'POST'])
@login_required
def delete_file(id_file):
    if id_file:
        query_file = DataFiles.query.filter_by(idFile=id_file).first()
        name_file = query_file.fileName + query_file.format
        os.remove(os.path.join(os.path.dirname(__file__), 'static\\uploads', name_file))
        db.session.delete(query_file)
        db.session.commit()
        flash('Your files has been deleted!', category="success")
    else:
        flash('The file doesn\'t exist!', category="error")
    return redirect(url_for('views.upload_file'))