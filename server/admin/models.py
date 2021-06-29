from wtforms.fields.core import IntegerField
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, IPAddress, InputRequired

class ServerForm(FlaskForm):
    name = StringField('Nom', validators=[DataRequired(),InputRequired("Veuillez remplir ce champ")])
    ip = StringField("IP", validators=[DataRequired(),IPAddress()])
    version = IntegerField('Version', validators=[DataRequired(),InputRequired("Veuillez remplir ce champ")])
    submit = SubmitField(label="Envoyer")