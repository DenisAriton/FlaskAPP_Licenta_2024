from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from DatasetsFactory.forms import CreateGroup, SelectGroup
from DatasetsFactory import db
from DatasetsFactory.models import Groups

admin_blueprint = Blueprint('admin', __name__)


@admin_blueprint.route('groups', methods=['GET', 'POST'])
@login_required
def groups():

    return render_template('admin/groups.html')