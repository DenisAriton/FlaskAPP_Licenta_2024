from flask import Blueprint, render_template, flash, url_for, redirect
from flask_login import login_required, current_user
from DatasetsFactory.forms import UploadFile, FileFolderDescription
from werkzeug.utils import secure_filename
from DatasetsFactory import db, app
from DatasetsFactory.models import DataFiles
from DatasetsFactory.usefull import CreateDirectory
from datetime import datetime
import os
import uuid

# Crearea blueprintului pentru modulul views, primul argument este denumirea blueprintului,
# iar __name__ va returna modulul din care face parte
datasets_blueprint = Blueprint('Datasets', __name__)


@datasets_blueprint.route('Select-Folder', methods=['GET', 'POST'])
@login_required
def select_folder():
    form_folder = FileFolderDescription()
    if form_folder.validate_on_submit():
        folder_name = form_folder.file_folder.data
        dataset_description = form_folder.file_description.data
        app.config['DATASET_FOLDER'] = folder_name
        app.config['DATASET_DESCRIPTION'] = dataset_description
        mk_dir = CreateDirectory(path=app.config['DATASETS_PATH'], dir_name=app.config['DATASET_FOLDER'])
        mk_dir.make_folder()
        print(f'Folder name: {app.config['DATASET_FOLDER']}\nDescription: {app.config['DATASET_DESCRIPTION']}')
    folders_datasets = os.listdir(app.config['DATASETS_PATH'])
    return render_template('datasets/selectfolder.html',
                           cur_object=current_user,
                           form_folder=form_folder,
                           folders_datasets=folders_datasets)


@datasets_blueprint.route('Upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    exist = True
    upload = UploadFile()
    if upload.validate_on_submit():
        for file in upload.file_up.data:
            file_name = str(uuid.uuid4()) + "_" + secure_filename(file.filename)
            # Se va cauta dupa nume in db fara extensie daca exista aceasta denumire
            file_db = DataFiles.query.filter_by(fileName=os.path.splitext(file_name)[0]).first()
            if file_db is None:
                # TODO: Trebuie creat un folder pentru seturile de date ce se uploadeaza si descrierea folderului!
                file.save(os.path.join(app.config['DATASETS_PATH'], file_name))
                # introducem numele si extensia separat in db
                new_file = DataFiles(fileName=os.path.splitext(file_name)[0], extension=os.path.splitext(file_name)[1])
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
                    name = file_exist.fileName + file_exist.extension
                    # preluam marimea fisierului in bytes
                    get_size = os.stat(os.path.join(app.config['DATASETS_PATH'], name)).st_size
                    #  convertim in KB
                    size = round(get_size / 1024)
                    # stocam in db datele
                    file_exist.size = size
                    file_exist.sizeUnit = 'KB'
                    file_exist.uploadTime = datetime.now()
                    db.session.add(file_exist)
                    db.session.commit()
            else:
                flash('Nu se incarca alte date despre fisier!', category="error")

    files_view = DataFiles.query.all()
    return render_template('datasets/upload.html', upload=upload, files_view=files_view, cur_object=current_user)


@datasets_blueprint.route('delete_file/<int:id_file>', methods=['GET', 'POST'])
@login_required
def delete_file(id_file):
    if id_file:
        query_file = DataFiles.query.filter_by(idFile=id_file).first()
        name_file = query_file.fileName + query_file.extension
        os.remove(os.path.join(app.config['DATASETS_PATH'], name_file))
        db.session.delete(query_file)
        db.session.commit()
        flash('Your files has been deleted!', category="success")
    else:
        flash('The file doesn\'t exist!', category="error")
    return redirect(url_for('Datasets.upload_file'))
