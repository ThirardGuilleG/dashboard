from datetime import datetime
from flask import Blueprint,redirect, flash, request
from flask.helpers import url_for
from flask.templating import render_template
from Blueprint.admin.models import ServerForm
from database.models import get_db, Server, Etat_Service
from loguru import logger
import sqlite3
import json

adminB = Blueprint("admin",__name__, url_prefix="/admin")


db = get_db()


@adminB.route("/", methods=['GET'])
def index():
    return "admin"


@adminB.get("/servers", defaults={'page': 1})
@adminB.get("/servers/<int:page>")
def servers(page=1):
    names = ['ID','Nom',"IP","Version"]
    servers = Server.query.paginate(page=page,per_page=10)
    rows = [[server.id,server.name,server.ip,server.version] for server in servers.items]
    args = {"names": names, "rows": rows, "pagination": servers, "endpoint": "admin.servers", 
            "modifyUrl": "admin.modify_server", "deleteUrl": "admin.delete_server"}
    return render_template("admin/tables.html", **args)


@adminB.route("/add/server",methods=['GET','POST'])
def add_server():
    form = ServerForm()
    logger.debug("ajout d'un serveur")
    if form.validate_on_submit():
        logger.debug("le formulaire est ok")
        newServer = Server()
        form.populate_obj(newServer)
        try:
            db.session.add(newServer)
            db.session.commit()
            logger.info(f"Création du serveur : {newServer.name}")
            flash("Création réussi","success")
        except sqlite3.Error as errBdd:
            logger.exception("Erreur BDD E01")
            flash(f"Erreur : {errBdd}")
        return redirect(url_for("admin.servers"))
    return render_template("form.html", form=form, title="Ajout d'un serveur")


@adminB.route("/modify/server/<int:idServer>")
def modify_server(idServer):
    return f"Not implemented : modif id : {idServer}"


@adminB.route("/delete/server/<int:idServer>")
def delete_server(idServer):
    return f"Not implemented : delete id : {idServer}"


@adminB.post("/data")
def data():
    data = request.get_data(as_text=True).encode('utf-8')
    resp = json.loads(data)
    logger.debug(resp)
    name_server = resp.get('server')
    etat = resp.get('etat')
    logger.info(f"Update des etats pour : {name_server}")
    logger.debug(etat)
    server = Server.query.filter_by(name=name_server).first()
    if not server:
        return "error"
    etat_server = Etat_Service.query.filter_by(id_server=server.id).first()
    if etat_server:
        etat_server.zabbix = etat.get('zabbix')
        etat_server.graylog_sidecar = etat.get('graylog')
        etat_server.winlogbeat = etat.get('winlogbeat')
        etat_server.eaton = etat.get('eaton')
        etat_server.fsecure = etat.get('fsecure')
        etat_server.fsecure_activate = etat.get('fsecure_activate')
        etat_server.last_update_date = datetime.now()
    else:
        etat_server = Etat_Service()
        etat_server.zabbix = etat.get('zabbix')
        etat_server.graylog_sidecar = etat.get('graylog')
        etat_server.winlogbeat = etat.get('winlogbeat')
        etat_server.eaton = etat.get('eaton')
        etat_server.fsecure = etat.get('fsecure')
        etat_server.fsecure_activate = etat.get('fsecure_activate')
        etat_server.last_update_date = datetime.now()
        etat_server.id_server = server.id
    db.session.add(etat_server)
    db.session.commit()
    return "OK", 201


@adminB.post('/active')
def active():
    """
        Update de l'etat activé ou non d'un serveur
    """
    data = request.get_data(as_text=True).encode('utf-8')
    resp = json.loads(data)
    server_name = resp.get('server')
    etat = resp.get('etat')
    logger.info(f"Reception de l'etat windows pour : {server_name} etat : {etat}")
    server = Server.query.filter_by(name=server_name).first_or_404()
    server.active = etat
    db.session.add(server)
    db.session.commit()
    return ("success", 201)


@adminB.get("/server_view/<int:idServer>")
def server_view(idServer):
    """View pour l'etat des services d'un serveur.

    Args:
        idServer (int): id du serveur

    Returns:
        response: view html
    """
    services = Etat_Service.query.filter_by(id_server=idServer).first_or_404()
    server = Server.query.get_or_404(idServer)
    return render_template("services.html", services=services, server=server)


@adminB.get("/services_view")
def services_view():
    """
        View des serveurs pours lesquels un service n'est pas installé
    """
    servers_without_zabbix = [(Server.query.get(server.id_server).name, server.zabbix) for server in Etat_Service.query.filter_by(zabbix=0).order_by(Etat_Service.last_update_date).all()]
    logger.debug(f"{servers_without_zabbix=}")
    servers_without_graylog = [(Server.query.get(server.id_server).name, server.graylog_sidecar) for server in Etat_Service.query.filter_by(graylog_sidecar=0).order_by(Etat_Service.last_update_date).all()]
    servers_without_eaton = [(Server.query.get(server.id_server).name, server.eaton) for server in Etat_Service.query.filter_by(eaton=0).order_by(Etat_Service.last_update_date).all()]
    servers_without_fsecure = [(Server.query.get(server.id_server).name, server.fsecure) for server in Etat_Service.query.filter_by(fsecure=0).order_by(Etat_Service.last_update_date).all()]
    servers_without_active_fsecure = [(Server.query.get(server.id_server).name, server.fsecure_activate) for server in Etat_Service.query.filter_by(fsecure_activate=0).order_by(Etat_Service.last_update_date).all()]
    logger.debug(f"{servers_without_graylog=}")
    logger.debug(f"{servers_without_eaton=}")
    logger.debug(f"{servers_without_active_fsecure=}")
    return ""