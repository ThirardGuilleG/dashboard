from flask import Flask

app = Flask(__name__, template_folder='template')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///updates.sqlite3'
app.config['SECRET_KEY'] = "zdzhdhzdh"
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'