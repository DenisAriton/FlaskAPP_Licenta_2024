from flask import Blueprint, render_template, send_from_directory, jsonify, flash, redirect, url_for
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
    id_group_list = current_user.groups
    if id_group_list == []:
        flash(f'You haven\'t a dataset assigned yet!', category='error')
        return redirect(url_for('Routes.home', name=current_user.firstName+current_user.lastName))
    else:
        id_group = id_group_list[0]
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
    """
    Vom returna o lista de dataseturi existente si disponibile fiecarui user!
    :param token: unique token for every user
    :return: list(available_datasets)
    """
    # Identificam user-ul care face GET request-ul
    check_user = UserIdentification.query.filter_by(TokenKey=token).first()
    # Verificam daca exista vreun user cu acest token, altfel trimitem un mesaj!
    if check_user:
        # Verificam daca are vreo grupa asignata prima data
        exist_group = check_user.groups
        if exist_group:
            # Identificam grupa din care face parte user-ul
            group = check_user.groups[0].idGroup
            # Verificam daca exista vreun dataset asignat user-ului, altfel trimitem mesaj!
            exist_datasets = FileAccess.query.filter_by(idGroup=group, keyAccess=1).all()
            if exist_datasets:
                # Cautam toate dataseturile la care are acces si pastram numele datasetului
                files_in_dataset = [{el.datasets_access.directory:
                                    list(map(lambda x: {x.relation_file.idFile: x.relation_file.relativePath.split("^%20%^")[1]}, FilesInDataset.query.filter_by(idDataset=el.idDataset).all()))}
                                    for el in exist_datasets]
                return jsonify(files_in_dataset)
            else:
                return "Your group has not a dataset assigned!", 404
        else:
            return (f'You have not a group assigned!\n'
                    f'\tYou have to be assigned to a group first, and after this, you can access datasets!', 404)
    else:
        return f'Your token key is not valid. Please try again!', 404


@routes_blueprint.route('load/dataset/<string:token>/<string:id_file>', methods=['GET'])
def load_dataset(token, id_file):
    check_user = UserIdentification.query.filter_by(TokenKey=token).first()
    # Verificam sa existe token-ul trimis
    if check_user:
        file = DataFiles.query.filter_by(idFile=id_file).first()
        # Tine cont de faptul ca path-ul in unix este determinat prin slash / nu backslah \\ ca la Windows!!!!!
        details_file = file.relativePath.split('/')
        print(file.relativePath)
        abs_path_to_file = str(os.path.join(app.config['DATASETS_PATH'], details_file[0]))
        if file:
            return send_from_directory(abs_path_to_file, details_file[1], as_attachment=True)
        else:
            return f'This file doesn\'t exist!', 404
    else:
        return f'Your token is not valid. Please try again!', 404
