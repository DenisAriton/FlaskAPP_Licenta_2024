from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired, FileSize, MultipleFileField, FileField
from wtforms import StringField, PasswordField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp
from .models import UserIdentification
from .settings import verify_format_email
from flask_login import current_user


# https: // github.com / marcelomd / flask - wtf - login - example / blob / master / app / forms.py
# https://github.com/toddbirchard/flasklogin-tutorial/blob/master/flask_login_tutorial/forms.py\
# https: // github.com / techwithtim / Flask - Web - App - Tutorial / blob / main / website / models.py
# pentru email trebuie instalat email_validator


class SignUpForm(FlaskForm):
    # firstname trebuie sa fie format doar din litere, se pot introduce maxim 2 prenume: Denis Adrian
    firstname = StringField(
        'First Name',
        validators=
        [
            DataRequired(message='Please enter your first name'),
            Regexp(r"^[a-zA-Z]+$|^[a-zA-Z]+\s+[a-zA-Z]+$", message='Please enter your name with letters only!')
        ],
        render_kw={"placeholder": "Olga Devin"})
    # lastname trebuie sa fie format doar din litere, se introduce doar numele: Ariton
    lastname = StringField(
        'Last Name',
        validators=
        [
            DataRequired(message='Please enter your last name'),
            Regexp(r"^[a-zA-Z]+$", message='Please enter just your last name with letters only!')
        ],
        render_kw={"placeholder": "Enderson"})

    username = StringField(
        'Username',
        validators=
        [
            DataRequired(message='Please enter your username'),
            Length(min=6, message="Username must be greater than 6 characters")
        ],
        render_kw={"placeholder": "Type your username"})

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
    def validate_username(self, field):
        form_data = self.username.data
        user = UserIdentification.query.filter_by(userName=form_data).first()
        if user:
            raise ValidationError('An account was created with this username already!')

    def validate_email(self, field):
        form_data = self.email.data
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

    def validate_username(self, field):
        """
        Verify if the username or email exists in the database
        :param field: validate_username
        :return: Raise an ValidationError
        """
        data_form = self.username.data
        if verify_format_email(data_form):
            userid = UserIdentification.query.filter_by(email=data_form).first()
            if userid is None:
                raise ValidationError('Incorrect email!')
        else:
            userid = UserIdentification.query.filter_by(userName=data_form).first()
            if userid is None:
                raise ValidationError('Incorrect username!')

    def validate_password(self, field):
        data_form = self.username.data
        # Creeaza o instanta a clasei UserIdentification pe baza userid-ului introdus pentru putea face verificarea parolei
        if verify_format_email(data_form):
            userdb = UserIdentification.query.filter_by(email=data_form).first()
        else:
            userdb = UserIdentification.query.filter_by(userName=data_form).first()
        if userdb:
            if userdb.check_password(keypass=field.data) is False:
                raise ValidationError('Incorrect password!')


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


class ImageProfile(FlaskForm):
    image_up = FileField(
        'Change Image',
        validators=
        [
            FileRequired(message='Upload an image!'),
            FileSize(max_size=5 * 1024 * 1024,
                     message="File's size must be less than 25MB!"),
            FileAllowed(['jpg', 'jpeg', 'png'],
                        message='Images with these extensions are allowed! .jpeg, .jpg, .png')
        ])

    submit_image = SubmitField("Change Image")


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
        render_kw={"placeholder": "Type your old password"})
    new_password = PasswordField(
        'New Password',
        validators=
        [
            DataRequired(message='Enter your new password!')
        ],
        render_kw={"placeholder": "Type your new password"})

    confirm_new_password = PasswordField(
        'Confirm New Password',
        validators=
        [
            DataRequired(message='Repeat your new password!'),
            EqualTo('new_password', message='Passwords must be similar!')
        ],
        render_kw={"placeholder": "Confirm your new password"})
    submit = SubmitField("Save")

    def validate_old_password(self, field):
        """
        Verificam daca vechea parola este corecta!
        :param field:
        :return:
        """
        data_form = self.old_password.data
        if current_user:
            if current_user.check_password(keypass=data_form) is False:
                raise ValidationError('Incorrect password!')

    def validate_new_password(self, field):
        """
        Verificam daca noua parola nu este la fel ca cea veche!
        :param field:
        :return:
        """
        data_form = self.new_password.data
        if current_user:
            if current_user.check_password(keypass=data_form):
                raise ValidationError('New password can\'t be similar to old password!')
