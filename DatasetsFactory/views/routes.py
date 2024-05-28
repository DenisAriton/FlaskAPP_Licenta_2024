from flask import Blueprint, render_template, send_from_directory, jsonify
from flask_login import login_required, current_user
from DatasetsFactory.models import Datasets, DataFiles, FileAccess, FilesInDataset, UserIdentification
import os
from DatasetsFactory import app

# Crearea blueprintului pentru modulul views, primul argument este denumirea blueprintului,
# iar __name__ va returna modulul din care face parte
routes_blueprint = Blueprint('Routes', __name__)


@routes_blueprint.route('home/<name>', methods=['GET'])
@login_required
def home(name):
    return render_template('home.html', cur_object=current_user)


@routes_blueprint.route('datasets', methods=['GET'])
@login_required
def user_dataset():
    # Cautam grupa din care face parte userul
    id_group = current_user.groups[0]
    print(id_group)
    # Preluam toate dataseturile pe care le detine grupa careia i-a fost atribuita userului
    datasets_access = FileAccess.query.filter_by(idGroup=id_group.idGroup).all()
    # Cautam doar acele dataseturi pe care exista dreptul de acces
    list_access_datasets = [dataset for dataset in datasets_access if dataset.keyAccess == 1]
    print(list_access_datasets)

    dir_info = dict()
    folders = os.listdir(app.config['DATASETS_PATH'])
    if folders:
        for folder_name in folders:
            db_dataset = Datasets.query.filter_by(directory=folder_name).first()
            if db_dataset:
                dir_info[db_dataset.directory] = [db_dataset.dataset_files, db_dataset]
    print(dir_info)

    return render_template('datasets/datasets_for_user.html',
                           cur_object=current_user,
                           list_access_datasets=list_access_datasets,
                           dir_info=dir_info)


@routes_blueprint.route('/datasets/list-all/<string:token>', methods=['GET'])
def datasets_list(token):
    check_user = UserIdentification.query.filter_by(TokenKey=token).first()
    if check_user:
        datasets_access = list()
        send_to_user = dict()
        group = check_user.groups[0].idGroup
        files = list()
        print(group)
        # Cautam toate dataseturile la care are acces si pastram lista de fisiere a fiecarui dataset
        datasets_access = [(el.datasets_access.directory, el.datasets_access.dataset_files)
                           for el in FileAccess.query.filter_by(idGroup=group).all()
                           if el.keyAccess == 1]
        for dataset in datasets_access:
            for file in dataset[1]:
                if file:
                    files.append(file.relation_file.idFile)
                else:
                    files.clear()
            send_to_user[dataset[0]] = files.copy()
            files.clear()

        print(send_to_user)
        return jsonify(send_to_user)
    else:
        return f'Your token key is not valid. Please try again!'


@routes_blueprint.route('load/dataset/<string:id_file>/<string:token>', methods=['GET'])
def load_dataset(id_file, token):
    check_user = UserIdentification.query.filter_by(TokenKey=token).first()
    if check_user:
        files = DataFiles.query.filter_by(idFile=id_file).first()
        if files:
            info_file = files.relativePath.split('\\')
            abs_path_to_file = str(os.path.join(app.config['DATASETS_PATH'], info_file[0]))
            return send_from_directory(abs_path_to_file, info_file[1], as_attachment=True)
        else:
            return 'No such file! Check the id!'
    else:
        return f'Your token key is not valid. Please try again!'
