from flask import Blueprint, render_template, flash, url_for, redirect, request
from flask_login import login_required, current_user
from DatasetsFactory.forms import UploadFile, FileFolderDescription, SearchItems
from werkzeug.utils import secure_filename
from DatasetsFactory import db, app
from DatasetsFactory.models import DataFiles, Datasets
from DatasetsFactory.usefull import CreateDirectory
from datetime import datetime
import os
import uuid

# Crearea blueprintului pentru modulul views, primul argument este denumirea blueprintului,
# iar __name__ va returna modulul din care face parte
datasets_blueprint = Blueprint('Datasets', __name__)


@datasets_blueprint.route('create-folder', methods=['GET', 'POST'])
@login_required
def create_folder():
    form_folder = FileFolderDescription()
    if form_folder.validate_on_submit():
        mk_dir = CreateDirectory(path=app.config['DATASETS_PATH'], dir_name=form_folder.file_folder.data)
        mk_dir.make_folder()

        dataset_to_db = Datasets(directory=form_folder.file_folder.data, description=form_folder.file_description.data)
        db.session.add(dataset_to_db)
        db.session.commit()

        flash(f'Folder {app.config['DATASET_FOLDER']} has been successfully created !', category='success')
        return redirect(url_for('Datasets.list_datasets'))

    return render_template('datasets/createfolder.html', cur_object=current_user, form_folder=form_folder)


@datasets_blueprint.route('list-datasets', methods=['GET', 'POST'], defaults={'page': 1})
@datasets_blueprint.route('list-datasets/page=<int:page>', methods=['GET', 'POST'])
@login_required
def list_datasets(page):
    """
    Acest view va fi de vizualizare, paginare si cautare!
    :return: selectfolder.html
    """
    page = page
    form_search = SearchItems()
    datasets_folders = db.paginate(db.select(Datasets).order_by(Datasets.idDataset.desc()),
                                   page=page,
                                   per_page=9,
                                   error_out=False)

    dict_datasets = dict()
    folders_datasets = os.listdir(app.config['DATASETS_PATH'])
    # Vom parcurge fiecare folder in parte pentru a avea acces la date si cream un dictionar de date
    if folders_datasets:
        for folder_name in folders_datasets:
            db_dataset = Datasets.query.filter_by(directory=folder_name).first()
            if db_dataset:
                dict_datasets[db_dataset.directory] = [db_dataset.dataset_files, db_dataset]
    # print(dict_datasets)
    if form_search.search.data and form_search.validate_on_submit():
        item_searched = form_search.search.data
        print(item_searched)
        datasets_folders = db.paginate(db.select(Datasets).filter_by(directory=item_searched),
                                       per_page=9,
                                       error_out=False)
        print(datasets_folders.items)
        for el in datasets_folders:
            print(el)
        return render_template('datasets/datasetsfolder.html',
                               cur_object=current_user,
                               dict_datasets=dict_datasets,
                               items_per_page=datasets_folders,
                               form_search=form_search)

    return render_template('datasets/datasetsfolder.html',
                           cur_object=current_user,
                           dict_datasets=dict_datasets,
                           items_per_page=datasets_folders,
                           form_search=form_search)


@datasets_blueprint.route('delete-datasets/<int:idF>', methods=['GET'])
@login_required
def delete_datasets(idF):
    db_dataset = Datasets.query.filter_by(idDataset=idF).first()
    if db_dataset:
        del_dir = CreateDirectory(path=app.config['DATASETS_PATH'], dir_name=db_dataset.directory)
        del_dir.remove_dir()

        db.session.delete(db_dataset)
        db.session.commit()

        flash('Dataset deleted!', category='success')
    else:
        flash('Something went wrong!', category='error')

    return redirect(url_for('Datasets.list_datasets'))


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

        flash('Your files has been uploaded!', category="success")

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
