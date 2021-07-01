from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, InputRequired, Length, EqualTo
from wtforms.fields.html5 import EmailField

class SignUpForm(FlaskForm):
    firstname = StringField('Prenom', validators=[DataRequired(),InputRequired("Veuillez remplir ce champ")])
    lastname = StringField('Nom', validators=[DataRequired(),InputRequired("Veuillez remplir ce champ")])
    username = StringField('Utilisateur', validators=[DataRequired(),InputRequired("Veuillez remplir ce champ")])
    email = EmailField('Email', validators=[DataRequired(),InputRequired("Veuillez remplir ce champ")])
    password = PasswordField('Mot de passe', validators=[DataRequired(),InputRequired("Veuillez remplir ce champ"), Length(min=8)])
    confirm_password = PasswordField('Confirmer mot de oasse', validators=[DataRequired(),EqualTo('password', message='Le mot de passe ne correspond pas')])
    submit = SubmitField('Inscription')


class SignInForm(FlaskForm):
    user_or_email = StringField('User ou Email', validators=[DataRequired(),InputRequired("Veuillez remplir ce champ")])
    password = PasswordField('Mot de passe', validators=[DataRequired(),InputRequired("Veuillez remplir ce champ"), Length(min=8)])
    submit = SubmitField('Connection')