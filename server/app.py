from flask import Flask, request, jsonify, render_template, abort
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from datetime import datetime
import json
import re, base64
# import modéle
from database.models import db, Server

# import routes
from update.routes import updateB
from admin.routes import adminB

# app config
from createApp import app
Bootstrap(app)

# Blueprint
app.register_blueprint(updateB)
app.register_blueprint(adminB)

# Database
db.app = app
db.init_app(app)
db.create_all()

migrate = Migrate(app, db)


@app.route("/", methods=['GET', 'POST'])
def index():
    return 'None'


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    return render_template('dashboard.html')


@app.post('/servers')
def servers():
    args= request.form
    token = args.get('token')
    goodToken = "5i3#&N4.r`ftp~s/CG:?t7tCq}zE#5g4Xf58m7.t"
    if token == goodToken:
        servers = [(server.name,server.ip) for server in Server.query.all()]
        return jsonify(servers)
    abort(403)

if __name__ == "__main__":
    app.run("0.0.0.0", debug=True)