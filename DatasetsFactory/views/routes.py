from flask import Blueprint, render_template, send_from_directory, jsonify
from flask_login import login_required, current_user
from DatasetsFactory.models import Datasets, DataFiles, FileAccess, FilesInDataset

# Crearea blueprintului pentru modulul views, primul argument este denumirea blueprintului,
# iar __name__ va returna modulul din care face parte
routes_blueprint = Blueprint('Routes', __name__)


@routes_blueprint.route('home/<name>', methods=['GET'])
@login_required
def home(name):
    return render_template('home.html', cur_object=current_user)


@routes_blueprint.route('/datasets/list-all', methods=['GET'])
def datasets_list():
    datasets = [(el.idDataset, (el.directory, el.description)) for el in Datasets.query.all()]
    return jsonify(datasets)
