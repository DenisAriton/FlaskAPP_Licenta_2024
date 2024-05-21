from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from DatasetsFactory.forms import CreateGroup, SelectGroup
from DatasetsFactory import db
from DatasetsFactory.models import Groups

admin_blueprint = Blueprint('admin', __name__)


@admin_blueprint.route('create-groups', methods=['GET', 'POST'])
@login_required
def create_groups():
    form_create_group = CreateGroup()
    return render_template('admin/groups.html',
                           cur_object=current_user,
                           form_create_group=form_create_group)


@admin_blueprint.route('asign-group', methods=['GET', 'POST'])
@login_required
def asign_group():
    form_select_group = SelectGroup()
    return render_template('admin/users.html',
                           cur_object=current_user,
                           form_create_group=form_select_group)


@admin_blueprint.route('privileges-on-datasets', methods=['GET', 'POST'])
@login_required
def asign_privile():
    form_select_group = SelectGroup()
    return render_template('admin/datasets_pivileges.html',
                           cur_object=current_user,
                           form_create_group=form_select_group)
