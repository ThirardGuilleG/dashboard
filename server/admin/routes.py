from flask import Blueprint,redirect, flash
from flask.helpers import url_for
from flask.templating import render_template
from admin.models import ServerForm
from database.models import get_db, Server
from loguru import logger
import sqlite3

adminB = Blueprint("admin",__name__, url_prefix="/admin")


db = get_db()


@adminB.route("/", methods=['GET'])
def index():
    return "admin"


@adminB.get("/servers", defaults={'page': 1})
@adminB.get("/servers/<int:page>")
def servers(page=1):
    names = ['ID','Nom',"IP","Version"]
    servers = Server.query.paginate(page=page,per_page=2)
    rows = [[server.id,server.name,server.ip,server.version] for server in servers.items]
    args = {"names": names, "rows": rows, "pagination": servers, "endpoint": "admin.servers", 
            "modifyUrl": "admin.modify_server", "deleteUrl": "admin.delete_server"}
    return render_template("admin/tables.html", **args)


@adminB.route("add/server",methods=['GET','POST'])
def add_server():
    form = ServerForm()
    if form.validate_on_submit():
        newServer = Server()
        form.populate_obj(newServer)
        try:
            db.session.add(newServer)
            db.session.commit()
            flash("Création réussi","success")
        except sqlite3.Error as errBdd:
            logger.exception("Erreur BDD E01")
            flash(f"Erreur : {errBdd}")
        return redirect(url_for("admin.servers"))
    return render_template("form.html", form=form, title="Ajout d'un serveur")

@adminB.route("modify/server/<int:idServer>")
def modify_server(idServer):
    return f"Not implemented : modif id : {idServer}"


@adminB.route("delete/server/<int:idServer>")
def delete_server(idServer):
    return f"Not implemented : delete id : {idServer}"