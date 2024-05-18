from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired, FileSize, MultipleFileField, FileField
from wtforms import StringField, PasswordField, SubmitField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp
from .models import UserIdentification
from .usefull import verify_format_email
from flask_login import current_user
from os import listdir
from DatasetsFactory import app

# https: // github.com / marcelomd / flask - wtf - login - example / blob / master / app / forms.py
# https://github.com/toddbirchard/flasklogin-tutorial/blob/master/flask_login_tutorial/forms.py\
# https: // github.com / techwithtim / Flask - Web - App - Tutorial / blob / main / website / models.py
# pentru email trebuie instalat email_validator


class SignUpForm(FlaskForm):
    firstname = StringField(
        'First Name',
        validators=
        [
            DataRequired(message='Please enter your first name'),
            Regexp(r'[a-zA-Z\s]+$', message='Please enter your name with letters only!')
        ],
        render_kw={"placeholder": "Olga Devin"})
    # lastname trebuie sa fie format doar din litere, se introduce doar numele: Ariton
    lastname = StringField(
        'Last Name',
        validators=
        [
            DataRequired(message='Please enter your last name'),
            Regexp(r'[a-zA-Z\s]+$', message='Please enter just your last name with letters only!')
        ],
        render_kw={"placeholder": "Enderson"})
    # TODO: Trebuie pus un regex pe username, astfel incat sa nu existe niciun spatiu in input!
    username = StringField(
        'Username',
        validators=
        [
            DataRequired(message='Please enter your username'),
            Length(min=6, message="Username must be greater than 6 characters")
        ],
        render_kw={"placeholder": "olgadevin23"})

    email = StringField(
        'Email',
        validators=
        [
            DataRequired(message='Please enter your email'),
            Email(message="Please enter a valid email", check_deliverability=True)
        ],
        render_kw={"placeholder": "youremail@example.com"})

    password = PasswordField(
        'Password',
        validators=
        [
            DataRequired(message='Please enter your password'),
            Length(min=6, message="Select a stronger password!")
        ],
        render_kw={"placeholder": "Type your password"})
    confirm_password = PasswordField(
        'Confirm Password',
        validators=
        [
            DataRequired(message='Repeat your password!'),
            EqualTo('password', message='Passwords must be similar!')
        ],
        render_kw={"placeholder": "Confirm your password"})

    submit = SubmitField('Sign Up')

    # Aceste metode validate_NumeCampInput vor fi instantiate in momentul in care exista in db username-ul sau email-ul
    def validate_username(form, field):
        form_data = field.data
        user = UserIdentification.query.filter_by(userName=form_data).first()
        if user:
            raise ValidationError('An account was created with this username already!')

    def validate_email(form, field):
        form_data = field.data
        email = UserIdentification.query.filter_by(email=form_data).first()
        if email:
            raise ValidationError('An account was created with this email already!')


class LoginForm(FlaskForm):
    username = StringField(
        'User ID',
        validators=
        [
            DataRequired(message='Please enter your username or email address'),
        ],
        render_kw={"placeholder": "Type your username"})
    password = PasswordField(
        'Password',
        validators=
        [
            DataRequired(message='Please enter your password'),
        ],
        render_kw={"placeholder": "Type your password"})

    submit = SubmitField('Log In')

    def validate_username(form, field):
        """
        Verify if the username or email exists in the database
        :param field: validate_username
        :return: Raise an ValidationError
        """
        data_form = field.data
        if verify_format_email(data_form):
            userid = UserIdentification.query.filter_by(email=data_form).first()
            if userid is None:
                raise ValidationError('Incorrect email!')
        else:
            userid = UserIdentification.query.filter_by(userName=data_form).first()
            if userid is None:
                raise ValidationError('Incorrect username!')

    def validate_password(form, field):
        data_form = form.username.data
        # Creeaza o instanta a clasei UserIdentification pe baza userid-ului introdus pentru putea face verificarea parolei
        if verify_format_email(data_form):
            userdb = UserIdentification.query.filter_by(email=data_form).first()
        else:
            userdb = UserIdentification.query.filter_by(userName=data_form).first()
        if userdb:
            if userdb.check_password(keypass=field.data) is False:
                raise ValidationError('Incorrect password!')
        else:
            raise ValidationError('Enter a corect UserID first!')


class FileFolderDescription(FlaskForm):
    file_description = TextAreaField(
        'Add a description for dataset:',
        render_kw={"placeholder": "This dataset contains values for iris dataset..."}
    )
    file_folder = StringField(
        'Create a folder:',
        render_kw={"placeholder": "Folder name"}
    )
    submit_folder = SubmitField('Save')

    def validate_file_folder(form, field):
        folder_name = field.data
        folders_list = listdir(app.config['DATASETS_PATH'])
        if folder_name in folders_list:
            raise ValidationError(f'This name \'{folder_name}\' already exists!')


class UploadFile(FlaskForm):

    file_up = MultipleFileField(
        'Upload File',
        validators=
        [
            FileRequired(message='Upload a file!'),
            FileSize(max_size=25 * 1024 * 1024,
                     message="File's size must be less than 25MB!"),
            FileAllowed(['txt', 'csv', 'xlsx', 'pdf', 'docx', 'doc'],
                        message='Files with these extensions are allowed! .pdf, .txt, .csv, .doc, .xlxs')
        ])

    submit_file = SubmitField("Upload")

    def validate_file_up(form, field):
        if field.data and len(field.data) >= 5:
            raise ValidationError('Just 5 files are allowed!')


class ImageProfile(FlaskForm):
    image_up = FileField(
        'Change',
        validators=
        [
            FileRequired(message='Upload an image!'),
            FileSize(max_size=5 * 1024 * 1024,
                     message="File's size must be less than 5MB!"),
            FileAllowed(['jpg', 'jpeg', 'png'],
                        message='Images with these extensions are allowed! .jpeg, .jpg, .png !')
        ])

    submit_image = SubmitField("Change")


class ProfileForm(FlaskForm):
    firstname = StringField(
        'First Name',
        validators=
        [
            DataRequired(message='Please enter your first name'),
            Regexp(r'[a-zA-Z\s]+$', message='Please enter your name with letters only!')
        ],
        render_kw={"placeholder": "Olga Devin"})
    # lastname trebuie sa fie format doar din litere, se introduce doar numele: Ariton
    lastname = StringField(
        'Last Name',
        validators=
        [
            DataRequired(message='Please enter your last name'),
            Regexp(r'[a-zA-Z\s]+$', message='Please enter just your last name with letters only!')
        ],
        render_kw={"placeholder": "Enderson"})

    email = StringField(
        'Email',
        validators=
        [
            DataRequired(message='Please enter your email'),
            Email(message="Please enter a valid email", check_deliverability=True)
        ],
        render_kw={"placeholder": "youremail@example.com"})

    submit = SubmitField('Change')

    def validate_email(form, field):
        form_data = field.data
        email = UserIdentification.query.filter_by(email=form_data).first()
        if email:
            raise ValidationError('An account was created with this email already!')


class ResetPassword(FlaskForm):
    """
    Reseteaza parola:
        - confirma parola veche
        - adauga o parola noua care trebuie hashuita!
        - confirma parola noua
        - parola noua nu are voie sa fie aceeasi cu cea veche !
    """
    old_password = PasswordField(
        'Old Password',
        validators=
        [
            DataRequired(message='Enter your old password!')
        ],
        render_kw={"placeholder": "Old password"})
    new_password = PasswordField(
        'New Password',
        validators=
        [
            DataRequired(message='Enter your new password!')
        ],
        render_kw={"placeholder": "New password"})

    confirm_new_password = PasswordField(
        'Confirm New Password',
        validators=
        [
            DataRequired(message='Repeat your new password!'),
            EqualTo('new_password', message='Passwords must be similar!')
        ],
        render_kw={"placeholder": "Confirm your new password"})
    submit = SubmitField("Save")

    def validate_old_password(form, field):
        """
        Verificam daca vechea parola este corecta!
        :param field:
        :return:
        """
        data_form = field.data
        if current_user:
            if current_user.check_password(keypass=data_form) is False:
                raise ValidationError('Incorrect password!')

    def validate_new_password(form, field):
        """
        Verificam daca noua parola nu este la fel ca cea veche!
        :param field:
        :return:
        """
        data_form = field.data
        if current_user:
            if current_user.check_password(keypass=data_form):
                raise ValidationError('The new password can\'t be similar to old password!')
