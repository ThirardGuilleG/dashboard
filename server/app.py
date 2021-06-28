from os import name
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from datetime import datetime
import json
import re
# import modéle
from update.models import db, Server, Update
from update.routes import updateB
# app config
app = Flask(__name__, template_folder='template')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///updates.sqlite3'
app.config['SECRET_KEY'] = "zdzhdhzdh"
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'


app.register_blueprint(updateB)

# db
db.app = app
db.init_app(app)
db.create_all()

# admin view
# admin = Admin(app, name='Updates', template_mode='bootstrap3')
# admin.add_view(ModelView(Server, db.session))
# admin.add_view(ModelView(Update, db.session))

@app.route("/", methods=['GET', 'POST'])
def index():
    return 'None'


@app.route("/test", methods=['GET', 'POST'])
def test():
    server = Server(name="SRVT2WP", ip="10.33.1.221")
    db.session.add(server)
    db.session.commit()
    return "ok"


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    return render_template('dashboard.html')


if __name__ == "__main__":
    app.run("0.0.0.0", debug=True)