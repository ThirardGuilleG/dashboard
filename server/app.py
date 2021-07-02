from flask import Flask, request, jsonify, render_template, abort, flash
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_login import LoginManager
from database.models import User
import json
import re, base64

from loguru import logger
# import modéle
from database.models import db, Server

# import routes
from update.routes import updateB
from admin.routes import adminB
from auth.routes import authB

# app config
from createApp import app
Bootstrap(app)

# Blueprint
app.register_blueprint(updateB)
app.register_blueprint(adminB)
app.register_blueprint(authB)

# Database
db.app = app
db.init_app(app)
db.create_all()

# Migration de bdd (update et ajout de table)
migrate = Migrate(app, db)

# connection
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = "info"
login_manager.login_message  = "Veuillez vous connecter"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    """Check if user is logged-in on every page load."""
    if user_id is not None:
        return User.query.get(user_id)
    return None


@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template('base.html')


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
        logger.debug(servers)
        return jsonify(servers)
    abort(403)


@app.get('/server')
def server_view():
    all_servers = Server.query.all()
    servers = [ {'id': server.id, 'name': server.name, 'ip': server.ip, 'version': server.version } for server in all_servers]
    logger.debug(servers)
    flash('Hello',"info")
    return render_template('card.html', servers=servers)


if __name__ == "__main__":
    app.run("0.0.0.0", debug=True)