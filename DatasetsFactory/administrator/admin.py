from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from DatasetsFactory.forms import CreateGroup, SearchGroup, EditGroup, SelectUser, SelectDataset
from DatasetsFactory import db
from DatasetsFactory.models import Groups, FileAccess, UserGroup, UserIdentification, Datasets
from datetime import datetime

admin_blueprint = Blueprint('Admin', __name__)


@admin_blueprint.route('create-group', methods=['GET', 'POST'])
@login_required
def create_group():
    page = request.args.get('page', default=1, type=int)
    form = CreateGroup()
    form_search = SearchGroup()
    form_edit = EditGroup()

    # Dropdown list pentru selectare de useri
    form_select_user = SelectUser()
    # Prima data trebuie sa luam doar acei useri care nu au o grupa asociata, doar aceea vor putea fi selectati
    already_assigned_to_group = [el.idUser for el in UserGroup.query.order_by(UserGroup.idUserGroup.asc()).all()]
    user_id = UserIdentification.query.order_by(UserIdentification.lastName.asc()).all()
    users_not_assigned = [el1 for el1 in user_id if el1.idUser not in already_assigned_to_group]
    choices_users = [(user.idUser, f'{user.lastName} {user.firstName}') for user in users_not_assigned if user.keyRole == 'User']
    choices_users.insert(0, (" ", "Select a user..."))
    form_select_user.user.choices = choices_users

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
                           exit_items=exist_items,
                           form_select_user=form_select_user)


@admin_blueprint.route('search/<string:item_searched>', methods=['GET'])
@login_required
def search_group(item_searched):
    form_edit = EditGroup()
    form_select_user = SelectUser()
    # Prima data trebuie sa luam doar acei useri care nu au o grupa asociata, doar aceea vor putea fi selectati
    already_assigned_to_group = [el.idUser for el in UserGroup.query.order_by(UserGroup.idUserGroup.asc()).all()]
    user_id = UserIdentification.query.order_by(UserIdentification.lastName.asc()).all()
    users_not_assigned = [el1 for el1 in user_id if el1.idUser not in already_assigned_to_group]
    choices_users = [(user.idUser, f'{user.lastName} {user.firstName}') for user in users_not_assigned if user.keyRole == 'User']
    choices_users.insert(0, (" ", "Select a user..."))
    form_select_user.user.choices = choices_users

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
                           form_edit=form_edit,
                           form_select_user=form_select_user)


@admin_blueprint.route('delete/<string:id_group>', methods=['GET'])
@login_required
def delete_group(id_group):
    """
    Vom sterge fiecare aparitie a grupei din orice tabel exista!
    Odata sters, se va pierde si dreptul pe un anume dataset!
    """
    db_group = Groups.query.filter_by(idGroup=id_group).first()
    db_access = FileAccess.query.filter_by(idGroup=id_group).all()
    db_user = UserGroup.query.filter_by(idGroup=id_group).all()
    if db_access:
        for el1 in db_access:
            db.session.delete(el1)
    if db_user:
        for el2 in db_user:
            db.session.delete(el2)
    if db_group:
        db.session.delete(db_group)
    flash(f'The group \'{db_group.groupName}\' was deleted!', category="success")
    db.session.commit()
    return redirect(url_for('Admin.create_group'))


@admin_blueprint.route('members/<string:id_group>', methods=['GET'])
@login_required
def members(id_group):
    """
    Vom lista toti membrii grupei!
    """
    page = request.args.get('page', 1, type=int)
    name_group = Groups.query.filter_by(idGroup=id_group).first()
    items_per_page = db.paginate(UserGroup.query.filter_by(idGroup=id_group), page=page, per_page=10, error_out=False)
    items_exist = list(items_per_page)
    return render_template('admin/members.html',
                           cur_object=current_user,
                           items_per_page=items_per_page,
                           id_group=id_group,
                           group_name=name_group.groupName,
                           items_exist=items_exist)


@admin_blueprint.route('delete/<string:id_group>/<string:id_member>', methods=['GET'])
@login_required
def delete_member(id_group, id_member):
    db_member = UserGroup.query.filter_by(idUser=id_member).first()
    name_group = Groups.query.filter_by(idGroup=id_group).first()
    if db_member:
        if db_member.groupsId.members == 1:
            db_member.groupsId.members = None
        else:
            db_member.groupsId.members = db_member.groupsId.members - 1
        name = db_member.userId.firstName + " " + db_member.userId.lastName
        db.session.delete(db_member)
        db.session.commit()
        flash(f'The member \'{name}\' was deleted from the group {name_group.groupName} !', category='success')
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


@admin_blueprint.route('asign-members-to-group/<string:group_id>', methods=['GET', 'POST'])
@login_required
def assign_group(group_id):
    form_select_user = SelectUser()
    # Ca sa putem prelua datele trebuie sa adaugam choices si aici ca altfel nu va merge validate...
    user_id = UserIdentification.query.order_by(UserIdentification.firstName.asc()).all()
    choices_users = [(user.idUser, f'{user.lastName} {user.firstName}') for user in user_id if user.keyRole == 'User']
    choices_users.insert(0, (" ", "Select a user..."))
    form_select_user.user.choices = choices_users

    if form_select_user.validate_on_submit():
        group_db = Groups.query.filter_by(idGroup=group_id).first()
        user_id = form_select_user.user.data
        user_name_db = UserIdentification.query.filter_by(idUser=user_id).first()
        # Verificam sa nu mai fie deja asignat unei alte grupe
        user_db = UserGroup.query.filter_by(idUser=user_id).first()
        if user_db is None:
            # Contorizam fiecare membru ce se va adauga la grupa
            if group_db.members is not None:
                nr_members = group_db.members + 1
                group_db.members = nr_members
            else:
                nr_members = 1
                group_db.members = nr_members

            user_group = UserGroup(idUser=user_id, idGroup=group_id)
            db.session.add(user_group)
            flash(f'The user \'{user_name_db.firstName + " " + user_name_db.lastName}\' was assignet to the group \'{group_db.groupName}\'!', category="success")
            db.session.commit()
        else:
            flash(f'The user \'{user_id}\' has already assigned to the group \'{user_db.groupsId.groupName}\'', category="error")
            return redirect(url_for('Admin.create_group'))
    else:
        flash(f'Select error: {form_select_user.user.errors[0]}', category='error')
    return redirect(url_for('Admin.create_group'))


@admin_blueprint.route('assign-priveleges-on-datasets/<string:group_id>', methods=['GET', 'POST'])
@login_required
def assign_privileges(group_id):
    select_dataset = SelectDataset()
    # Preluam toate datseturile care nu au fost atribuite grupei acesteia
    datasets_db = Datasets.query.order_by(Datasets.directory.asc()).all()
    # Preluam grupele care au deja un dataset atribuit
    groups_with_rights = FileAccess.query.filter_by(idGroup=group_id).all()
    # Cream o lista de chei ca sa verificam daca exista dataseturi deja atribuite si cu access
    file_access_db = [el.idDataset for el in groups_with_rights if el.keyAccess == 1]
    # Verificam sa nu existe vreun dataset deja atribuit aceleiasi grupe
    not_assigned = [el for el in datasets_db if el.idDataset not in file_access_db]
    # Cream lista de tupluri pentru optiunile selectfield-ului
    choices_datasets = [(dataset_group.idDataset, dataset_group.directory) for dataset_group in not_assigned]
    # Cream un placeholder pentru prima valoare
    choices_datasets.insert(0, (" ", "Select a dataset..."))
    select_dataset.dataset.choices = choices_datasets
    # Facem query-ul sa afisam numele grupei pe care face atribuirea de dataseturi
    group_db = Groups.query.filter_by(idGroup=group_id).first()

    if select_dataset.validate_on_submit():
        dataset_id = select_dataset.dataset.data
        query_dataset = FileAccess.query.filter_by(idDataset=dataset_id, idGroup=group_id).first()
        if query_dataset and query_dataset.keyAccess == 0:
            # Doar facem update pe coloana sa dam acces
            query_dataset.keyAccess = 1
            query_dataset.TimeGetAccess = datetime.now()
            db.session.commit()
            flash(f'The dataset {query_dataset.datasets_access.directory} has been assigned to {group_db.groupName}!', category='success')
            return redirect(url_for('Admin.assign_privileges', group_id=group_id))
        else:
            # Altfel facem insert daca nu exista deja in db
            dataset_name = Datasets.query.filter_by(idDataset=dataset_id).first()
            file_access_insert = FileAccess(idGroup=group_id, idDataset=dataset_id, keyAccess=1)
            db.session.add(file_access_insert)
            db.session.commit()
            flash(f'The dataset {dataset_name.directory} has been assigned to {group_db.groupName}!', category='success')
            return redirect(url_for('Admin.assign_privileges', group_id=group_id))
    else:
        if request.method == "POST":
            flash(f'Select error: {select_dataset.dataset.errors[0]}', category="error")
            return redirect(url_for('Admin.assign_privileges', group_id=group_id))

    return render_template('admin/privileges.html',
                           cur_object=current_user,
                           group_db=group_db,
                           select_dataset=select_dataset,
                           groups_with_rights=groups_with_rights)


@admin_blueprint.route('erase-access-on-dataset/for-group<int:group_id>/<int:dataset_id>')
@login_required
def erase_access(group_id, dataset_id):
    print(group_id, dataset_id)
    dataset_access = FileAccess.query.filter_by(idGroup=group_id, idDataset=dataset_id).first()
    if dataset_access and dataset_access.keyAccess == 1:
        dataset_access.keyAccess = 0
        dataset_access.TimeTakeAccess = datetime.now()
        db.session.commit()
        flash(f'The access on dataset {dataset_access.datasets_access.directory} has been erased!', category='success')
        return redirect(url_for('Admin.assign_privileges', group_id=group_id))
    else:
        flash(f'The group {dataset_access.groups.groupName} has not access on {dataset_access.datasets_access.directory}!',
              category='error')
        return redirect(url_for('Admin.assign_privileges', group_id=group_id))
