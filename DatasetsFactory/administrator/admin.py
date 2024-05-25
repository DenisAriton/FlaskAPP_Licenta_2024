from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from DatasetsFactory.forms import CreateGroup, SelectGroup, SearchGroup, EditGroup
from DatasetsFactory import db
from DatasetsFactory.models import Groups, FileAccess, UserGroup

admin_blueprint = Blueprint('Admin', __name__)


@admin_blueprint.route('create-group', methods=['GET', 'POST'])
@login_required
def create_group():
    page = request.args.get('page', default=1, type=int)
    form = CreateGroup()
    form_search = SearchGroup()
    form_edit = EditGroup()
    if form.group_name.data:
        # Daca se valideaza formularul de creare grupa se va face insert
        if form.validate_on_submit():
            group_insert = Groups(groupName=form.group_name.data)
            db.session.add(group_insert)
            db.session.commit()
            flash(f'The group with the name {form.group_name.data} has been created!', category="success")
            return redirect(url_for('Admin.create_group'))

    elif form_search.search_group.data:
        if form_search.validate_on_submit():
            searched_item = form_search.search_group.data
            return redirect(url_for('Admin.search_group', item_searched=searched_item))

    else:
        if request.method == "POST":
            flash('You have to enter a value first', category="error")

    items_per_page = db.paginate(Groups.query.order_by(Groups.groupName.desc()),
                                 page=page,
                                 per_page=10,
                                 error_out=False)
    exist_items = list(items_per_page)
    return render_template('admin/groups.html',
                           cur_object=current_user,
                           form_group=form,
                           form_search=form_search,
                           items_per_page=items_per_page,
                           form_edit=form_edit,
                           exit_items=exist_items)


@admin_blueprint.route('search/<string:item_searched>', methods=['GET'])
@login_required
def search_group(item_searched):
    form_edit = EditGroup()
    page = request.args.get('page', 1, type=int)
    group_id = list()
    search_group_db = Groups.query.filter(Groups.groupName.contains(f'{item_searched}')).all()
    for group in search_group_db:
        group_id.append(group.idGroup)
    if not group_id:
        flash('No group found!', category="error")
        return redirect(url_for('Admin.create_group'))

    items_per_page = db.paginate(Groups.query.filter(Groups.idGroup.in_(group_id)),
                                 page=page,
                                 per_page=10,
                                 error_out=False)
    return render_template('admin/search_group.html',
                           cur_object=current_user,
                           items_per_page=items_per_page,
                           item=item_searched,
                           form_edit=form_edit)


@admin_blueprint.route('delete/<string:id_group>', methods=['GET'])
@login_required
def delete_group(id_group):
    """
    Vom sterge fiecare aparitie a grupei din orice tabel exista!
    Odata sters, se va pierde si dreptul pe un anume dataset!
    """
    db_group = Groups.query.filter_by(idGroup=id_group).first()
    db_access = FileAccess.query.filter_by(idGroup=id_group).first()
    db_user = UserGroup.query.filter_by(idGroup=id_group).first()
    if db_group:
        db.session.delete(db_group)
    if db_access:
        db.session.delete(db_access)
    if db_user:
        db.session.delete(db_user)
    flash(f'The group \'{db_group.groupName}\' was deleted!', category="success")
    db.session.commit()
    return redirect(url_for('Admin.create_group'))


@admin_blueprint.route('members/<string:id_group>', methods=['GET'], defaults={'page': 1})
@admin_blueprint.route('members/<string:id_group>', methods=['GET'])
@login_required
def members(id_group, page):
    """
    Vom lista toti membrii grupei!
    """
    items_per_page = db.paginate(UserGroup.query.filter_by(idGroup=id_group), page=page, per_page=10, error_out=False)
    return render_template('admin/members.html',
                           cur_object=current_user,
                           items_per_page=items_per_page)


@admin_blueprint.route('delete/<string:id_group>/<string:id_member>', methods=['GET'])
@login_required
def delete_member(id_group, id_member):
    db_member = UserGroup.query.filter_by(idUser=id_member).first()
    if db_member:
        name = db_member.userId.firstName + " " + db_member.userId.lastName
        db.session.delete(db_member)
        db.session.commit()
        flash(f'The member \'{name}\' was deleted!', category='success')
        return redirect(url_for('Admin.members', id_group=id_group))
    else:
        flash(f'Something went wrong!', category='error')
        return redirect(url_for('Admin.members', id_group=id_group))


@admin_blueprint.route('edit/<string:id_group>', methods=['POST'])
@login_required
def edit_group(id_group):
    """
    Aici vom edita numele grupei in caz ca se doreste!
    - fiecare linie din tabel cu numele grupei va fi defapt un float-label form
    - valoarea default afisata va fi numele grupei!
    """
    form_edit = EditGroup()
    db_group = Groups.query.filter_by(idGroup=id_group).first()
    old_name = db_group.groupName
    if db_group and form_edit.validate_on_submit():
        db_group.groupName = form_edit.name.data
        db.session.commit()
        flash(f'The group \'{old_name}\' was changed into \'{db_group.groupName}\'!', category="success")
        return redirect(url_for('Admin.create_group'))
    elif form_edit.validate_on_submit() is False:
        flash(f'Edit error: {form_edit.name.errors[0]}', category='error')
        return redirect(url_for('Admin.create_group'))

# @admin_blueprint.route('asign-group', methods=['GET', 'POST'])
# @login_required
# def asign_group():
#     form_select_group = SelectGroup()
#     return render_template('admin/users.html',
#                            cur_object=current_user,
#                            form_create_group=form_select_group)
#
#
# @admin_blueprint.route('privileges-on-datasets', methods=['GET', 'POST'])
# @login_required
# def asign_privileges():
#     form_select_group = SelectGroup()
#     return render_template('admin/datasets_pivileges.html',
#                            cur_object=current_user,
#                            form_create_group=form_select_group)
