from flask import Blueprint, render_template
from flask_login import login_required, current_user

# Crearea blueprintului pentru modulul views, primul argument este denumirea blueprintului,
# iar __name__ va returna modulul din care face parte
routes_blueprint = Blueprint('Routes', __name__)


@routes_blueprint.route('home/<name>', methods=['GET'])
@login_required
def home(name):
    return render_template('home.html', cur_object=current_user)
