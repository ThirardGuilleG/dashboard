from os import name
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from datetime import datetime
import json
import re
# import modéle
from database.models import db

# import routes
from update.routes import updateB
from admin.routes import adminB

# app config
from createApp import app

# Blueprint
app.register_blueprint(updateB)
app.register_blueprint(adminB)

# Database
db.app = app
db.init_app(app)
db.create_all()


@app.route("/", methods=['GET', 'POST'])
def index():
    return 'None'


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    return render_template('dashboard.html')


if __name__ == "__main__":
    app.run("0.0.0.0", debug=True)