from flask import Blueprint, request, jsonify, render_template
from datetime import datetime
import json, re
from flask_sqlalchemy import Pagination
from loguru import logger
from database.models import Server, Update, get_db, UpdateAssociation

updateB = Blueprint("update",__name__, url_prefix="/update")
db = get_db()


@updateB.route("/data", methods=["POST"])
def data():
    """
    Ajout des mise à jours en base de données
    """
    answer = request.get_data(as_text=True).encode('utf-8')
    resp = json.loads(answer.decode())
    if resp:
        for update in resp:
            nameUpdate = update.get('Title')
            server = update.get('PSComputerName')
            maxSize = update.get('MaxDownloadSize')
            url = update.get('SupportUrl')
            reboot = update.get('RebootRequired')
            installed = update.get('IsInstalled')
            time = update.get('LastDeploymentChangeTime')
            timestamp = int(re.search(r'\d+', time[0:16]).group())
            date = datetime.fromtimestamp(timestamp)
            # Server
            myServer = Server.query.filter_by(name=server).first()
            if not myServer:
                return jsonify("erreur",200)
            myUpdate = Update.query.filter_by(title=nameUpdate).first()
            if not myUpdate:
                # Création de la MAJ 
                newUpdate = Update(title=nameUpdate,maxSize=maxSize,date=date,url=url)
                myUpdate = newUpdate
            modifyinformation = UpdateAssociation.query.filter_by(idUpdate=myUpdate.id,idServer=myServer.id).first()
            if modifyinformation:
                # mise à jour des informations
                modifyinformation.installed = installed
                modifyinformation.rebootRequired = reboot
                modifyinformation.date = datetime.now()
                db.session.add(modifyinformation)
            else:
                logger.debug(myUpdate)
                with db.session.no_autoflush:
                    # Création de l'association
                    association = UpdateAssociation(done=False,installed=installed, rebootrequired=reboot,date=datetime.now()) # ajout des données en plus
                    # Ajout du server relié à l'update
                    db.session.no_autoflush
                    association.update = myUpdate
                    # ajout en bdd
                    # myUpdate.servers.append(association)
                    # db.session.add(myUpdate)
                    myServer.updates.append(association)
                    db.session.add(myServer)
                    db.session.commit()
        return jsonify("ok", 200)


@updateB.route('/<int:idServer>')
def update(idServer):
    names = ['Titre', "Taille Max(Mo)", "Demande un redémarrage", "Installé", "Lien + information", "date de sortie", "dernière MAJ"]
    rows = [["Une MAJ intéressante", 125, True, True, "https://wow.fr", "25/12/20", "28/06/21 14h00"], 
    ["Une MAJ intéressante 2", 125, True, True, "https://wow.fr", "25/12/20", "28/06/21 14h00"],
    ["Une MAJ intéressante 3", 125, True, True, "https://wow.fr", "25/12/20", "28/06/21 14h00"]]
    # updates = UpdateAssociation.query.filter_by(idServer=idServeur).all()
    updates = db.session.query(UpdateAssociation).filter(UpdateAssociation.idServer==idServer).join(Update, UpdateAssociation.update).all()
    rows = []
    print(updates)
    for row in updates:
        update = row.update
        rows.append([update.title, update.maxSize/1000000, row.rebootrequired, row.installed,update.url ,update.date, row.date])
        # update = Update.query.get(row.id)
        # if update:
        #     information = [update.title, update.maxSize, row.rebootrequired, row.installed, update.date]
    myServer = Server.query.get_or_404(idServer)
    return render_template('tables.html', title= f"{myServer.name}",description=f"Voici toutes les mises à jours pour : {myServer.name}", names=names, rows=rows, pagination=[], endpoint=[])


@updateB.route('/validate/<int:idUpdate>/<int:idServer>')
def validate(idUpdate,idServer):
    return "Not implemented"


@updateB.route("/test", methods=['GET', 'POST'])
def test():
    server = Server(name="SRVT2WP", ip="10.33.1.221")
    db.session.add(server)
    db.session.commit()
    return "ok"