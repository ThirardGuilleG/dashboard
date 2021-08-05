from flask import Flask, redirect, url_for, render_template, jsonify, jsonify, request, abort
from config import ProdConfig,TestConfig,DevConfig
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_login import LoginManager
from database.models import Server, UpdateAssociation, Etat_Service
from sqlalchemy import or_
from loguru import logger
from utils import get_or_create_img, get_number_update


app = Flask(__name__, template_folder='template', static_folder='static')
app.config.from_object(DevConfig)


# import routes
from Blueprint.update.routes import updateB
from Blueprint.admin.routes import adminB
from Blueprint.auth.routes import authB

from database.models import db, User

# routes
@app.route("/", methods=['GET'])
def index():
    return redirect(url_for('dashboard'))


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    updates = UpdateAssociation.query.filter(UpdateAssociation.done==False).all()
    done_updates = UpdateAssociation.query.filter(UpdateAssociation.done==True).all()
    has_to_restart = [server.id for server in Server.query.filter(Server.rebootrequired==True)]
    anomalie = Etat_Service.query.filter(or_(
    Etat_Service.zabbix==False,
    Etat_Service.graylog_sidecar==False,
    Etat_Service.winlogbeat==False,
    Etat_Service.eaton==False,
    Etat_Service.fsecure==False,
    Etat_Service.fsecure_activate==False,
    )).all()
    return render_template('dashboard.html', number_update=len(updates), done_updates=len(done_updates), nmbr_restart= len(has_to_restart), anomalie=len(anomalie))


@app.post('/servers')
def servers():
    args= request.form
    token = args.get('token')
    logger.info(f"Demande de la liste des serveurs de : {request.remote_addr}")
    goodToken = "5i3#&N4.r`ftp~s/CG:?t7tCq}zE#5g4Xf58m7.t"
    if token == goodToken:
        servers = [(server.name,server.ip) for server in Server.query.all()]
        logger.debug(servers)
        return jsonify(servers)
    abort(403)


@app.get('/server')
def server_view():
    all_servers = Server.query.all()
    servers = [ {'id': server.id, 'name': server.name, 'ip': server.ip, 'version': server.version, 'need_restart': server.rebootrequired,
                'img': get_or_create_img(server.id), 'update':get_number_update(server.id) } for server in all_servers
                ]
    def sort_by_number_update(element):
        if element.get('need_restart') is True:
            return 9999
        if element.get('update') == 'O':
            return 0
        return element.get('update')
    servers.sort(key=sort_by_number_update, reverse=True)
    return render_template('card.html', servers=servers)


@app.get('/test')
def test():
    import subprocess
    completed = subprocess.run(["powershell", "-Command", "mstsc /v:10.33.1.111:3389"], capture_output=True)
    print(completed)
    return "sss"
# Blueprint
app.register_blueprint(updateB)
app.register_blueprint(adminB)
app.register_blueprint(authB)

# Bootstrap
Bootstrap(app)

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