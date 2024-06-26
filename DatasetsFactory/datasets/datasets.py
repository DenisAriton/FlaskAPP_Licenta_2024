from flask import Blueprint, render_template, flash, url_for, redirect, request
from flask_login import login_required, current_user
from DatasetsFactory.forms import UploadFile, FileFolderDescription, SearchItems, SearchFiles
from werkzeug.utils import secure_filename
from DatasetsFactory import db, app
from DatasetsFactory.models import DataFiles, Datasets, FilesInDataset, LogFile, FileAccess
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
        make_verify = mk_dir.make_folder()
        if not make_verify:
            dataset_to_db = Datasets(directory=form_folder.file_folder.data, description=form_folder.file_description.data)
            db.session.add(dataset_to_db)
            db.session.commit()

            flash(f'Folder {form_folder.file_folder.data} has been successfully created !', category='success')
            return redirect(url_for('Datasets.list_datasets'))
        else:
            flash(f'The folder\'{form_folder.file_folder.data}\' already exist locally, on the server!', category="error")
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
    # Vom parcurge fiecare folder care este creat local in parte pentru a avea acces la date si cream un dictionar de date
    # Teoretic nu as mai avea nevoie de db_dataset(id-ul adica), deoarece avem access la id prin datasets_folders
    # care gestioneaza si paginarea
    if folders_datasets:
        for folder_name in folders_datasets:
            db_dataset = Datasets.query.filter_by(directory=folder_name).first()
            if db_dataset:
                dict_datasets[db_dataset.directory] = [db_dataset.dataset_files, db_dataset]
    # Gestionam Search engine-ul
    if form_search.search.data and form_search.validate_on_submit():
        item_searched = form_search.search.data
        verify_exist_dataset = Datasets.query.order_by(Datasets.idDataset.desc()).filter(Datasets.directory.contains(item_searched))
        list_of_folders = list()
        # Preluam toate id-urile dataseturilor care corespund sirului cautat
        for el in verify_exist_dataset:
            list_of_folders.append(el.idDataset)
        if verify_exist_dataset:
            datasets_folders = db.paginate(db.select(Datasets).filter(Datasets.idDataset.in_(list_of_folders)),
                                           page=page,
                                           per_page=9,
                                           error_out=False)
            return render_template('datasets/datasetsfolder.html',
                                   cur_object=current_user,
                                   dict_datasets=dict_datasets,
                                   items_per_page=datasets_folders,
                                   form_search=form_search)
        else:
            flash(f'The dataset \'{item_searched}\' doesn\'t exist!', category="error")

    return render_template('datasets/datasetsfolder.html',
                           cur_object=current_user,
                           dict_datasets=dict_datasets,
                           items_per_page=datasets_folders,
                           form_search=form_search)


@datasets_blueprint.route('delete-datasets/<int:idfolder>', methods=['GET'])
@login_required
def delete_datasets(idfolder):
    # Cautam dataset-ul care se doreste a fi sters
    db_dataset = Datasets.query.filter_by(idDataset=idfolder).first()
    # Cautam asocierile
    file_access = FileAccess.query.filter_by(idDataset=idfolder).all()
    db_file_in_dataset = FilesInDataset.query.filter_by(idDataset=db_dataset.idDataset).all()
    # Daca datasetul exista atunci se va sterge
    if db_dataset:
        # Stergem din tabelul cu privilegii prima data
        if file_access:
            for dataset_access in file_access:
                db.session.delete(dataset_access)
        # Stergem din folder
        del_dir = CreateDirectory(path=app.config['DATASETS_PATH'], dir_name=db_dataset.directory)
        del_dir.remove_dir()
        # Se sterg toate aparitiile datasetului in FilesInDataset
        if db_file_in_dataset:
            for el in db_file_in_dataset:
                db_files = DataFiles.query.filter_by(idFile=el.idFile).first()
                db.session.delete(db_files)  # Stergem fisierul din DataFiles
                db.session.delete(el)  # Stergem fisierul din FilesInDataset
        # Sterge din tabelul asociat datasetului
        db.session.delete(db_dataset)
        flash(f'Dataset {db_dataset.directory} has been deleted!', category='success')
        # Facem commit-ul dupa mesaj ca sa afisam numele
        db.session.commit()
    else:
        flash('No dataset found!', category='error')

    return redirect(url_for('Datasets.list_datasets'))


@datasets_blueprint.route('upload/files-to-dataset/<string:dataset_name>', methods=['GET', 'POST'])
@login_required
def upload_file(dataset_name):
    # Desemnam pagina principala si facem o cerere a paginii care ar urma
    page = request.args.get('page', 1, type=int)
    # Ne trebuie aceasta in caz se va nimeri sa fie vreun nume la fel, sa nu primim erori!
    exist = True
    upload = UploadFile()
    form_search = SearchFiles()
    id_dataset = Datasets.query.filter_by(directory=dataset_name).first()

    # Doar daca s-a facut submit pe butonul de upload atunci sa gestioneze formularul de upload, altfel nu
    if upload.submit_file.data:
        if upload.validate_on_submit():
            for file in upload.file_up.data:
                file_name = str(uuid.uuid4()) + "^%20%^" + secure_filename(file.filename)
                # Se va cauta dupa nume in db fara extensie daca exista aceasta denumire
                file_db = DataFiles.query.filter_by(fileName=os.path.splitext(file_name)[0]).first()
                if file_db is None:
                    # Se salveaza in folderul destinat acestuia!
                    file.save(os.path.join(app.config['DATASETS_PATH'], dataset_name, file_name))
                    # Facem insert-ul pe tabelul data_files ca mai apoi sa aflam un id !
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
                        # Cream relative_path
                        relative_path_file = str(os.path.join(dataset_name, name))
                        # preluam marimea fisierului in bytes
                        abs_path_to_file = os.path.join(app.config['DATASETS_PATH'], relative_path_file)
                        get_size = os.stat(abs_path_to_file).st_size
                        #  convertim in KB
                        if round(get_size / 1024) < 1000:
                            size = round(get_size / 1024, 2)
                            file_exist.size = size
                            file_exist.sizeUnit = 'KB'
                        elif round(get_size / (1024 * 1024)) < 1000:
                            size = round(get_size / (1024 * 1024), 2)
                            file_exist.sizeUnit = 'MB'
                            file_exist.size = size

                        # stocam in db datele
                        # TODO: Mai trebuie sa adaugam numarul de linii si de coloane!
                        file_exist.relativePath = relative_path_file
                        file_exist.uploadTime = datetime.now()
                        db.session.add(file_exist)

                        # Acuma vom stoca in baza de date id-urile datasetului si fisierului in FilesInDataset
                        files_in_dataset = FilesInDataset(idDataset=id_dataset.idDataset, idFile=file_exist.idFile)
                        db.session.add(files_in_dataset)

                        # Commitul final pentru toate insert-urile
                        db.session.commit()
                else:
                    flash('Nu se incarca alte date despre fisier!', category="error")

            flash('Your files has been uploaded!', category="success")
    # Altfel verificam daca exista date pe search, doar atunci sa preia POST request-ul
    elif form_search.search_file.data:
        if form_search.validate_on_submit():
            # Preluam datele din formular
            item_searched = form_search.search_file.data
            # Cautam toate aparitiile datasetului in baza de date
            files_search = FilesInDataset.query.filter_by(idDataset=id_dataset.idDataset).all()
            # preluam toate id-urile pe care le-am gasit ca mai apoi sa le asignam query-ului care cauta toate
            # aparitiile fiserului in dataset
            id_file = list()
            for el in files_search:
                if item_searched in el.relation_file.fileName.split('^%20%^')[1]:
                    id_file.append(el.relation_file.idFile)
            # Doar atunci exista date in lista vom face query-ul, altfel nu !
            if id_file:
                items_per_page = db.paginate(FilesInDataset.query.order_by(FilesInDataset.idFile.desc()).filter(
                                             FilesInDataset.idFile.in_(id_file)),
                                             page=page,
                                             per_page=6,
                                             error_out=False)
                flash(f'The file \'{item_searched}\' was found!', category='success')

                return render_template('datasets/upload.html',
                                       upload=upload,
                                       cur_object=current_user,
                                       dataset_name=dataset_name,
                                       items_per_page=items_per_page,
                                       form_search=form_search)
            else:
                flash(f'No file found!', category="error")
    # Pregatim fisierele spre vizualizare si paginare
    items_per_page = db.paginate(FilesInDataset.query.order_by(FilesInDataset.idFile.desc()).filter_by(
        idDataset=id_dataset.idDataset),
        page=page,
        per_page=6,
        error_out=False)
    return render_template('datasets/upload.html',
                           upload=upload,
                           cur_object=current_user,
                           dataset_name=dataset_name,
                           items_per_page=items_per_page,
                           form_search=form_search)


@datasets_blueprint.route('delete_file/<string:dataset_name>/<int:id_file>', methods=['GET', 'POST'])
@login_required
def delete_file(id_file, dataset_name):
    if id_file:
        # Cautam fisierul
        query_file = DataFiles.query.filter_by(idFile=id_file).first()
        # Daca exista ii vom cauta asocieri cu alte tabele
        if query_file:
            name_file = query_file.fileName
            files_in_dataset = FilesInDataset.query.filter_by(idFile=query_file.idFile).first()
            log_file = LogFile.query.filter_by(idFile=query_file.idFile).all()
            # Daca exista asocieri in alte tabele le vom sterge
            if files_in_dataset:
                db.session.delete(files_in_dataset)
            if log_file:
                for el in log_file:
                    db.session.delete(el)
            # Si la final se sterg fisierele din tabelul destinat acestora
            db.session.delete(query_file)
            db.session.commit()
            # Se sterge local!
            try:
                os.remove(os.path.join(app.config['DATASETS_PATH'], query_file.relativePath))
            except FileNotFoundError:
                flash('No such file on filesystem locally !', category='error')

            flash(f'Your file \'{name_file.split('^%20%^')[1]}\' has been deleted!', category="success")
        else:
            # Asta nu are sens, dar in caz ca se fac request-uri pe endpoint-ul acesta sa se afiseze un mesaj!
            flash(f'The file doesn\'t exist!', category="error")

    return redirect(url_for('Datasets.upload_file', dataset_name=dataset_name))
