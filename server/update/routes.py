from flask import Blueprint, request, jsonify, render_template
from datetime import datetime
import json, re
from flask_sqlalchemy import Pagination
from sqlalchemy import and_
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
            logger.info(f'Mise à jour récupérée pour : {server}')
            # Server
            myServer = Server.query.filter_by(name=server).first()
            if not myServer:
                logger.warning("le serveur n'est pas en bdd")
                return jsonify("erreur",200)
            myUpdate = Update.query.filter_by(title=nameUpdate).first()
            if not myUpdate:
                # Création de la MAJ 
                logger.debug(f"Création de la MAJ : {nameUpdate}")
                newUpdate = Update(title=nameUpdate,maxSize=maxSize,date=date,url=url)
                myUpdate = newUpdate
            modifyinformation = UpdateAssociation.query.filter_by(idUpdate=myUpdate.id,idServer=myServer.id).first()
            if modifyinformation:
                # mise à jour des informations
                logger.debug(f"L'association entre la MAJ {modifyinformation} existe déjà modification des informations")
                modifyinformation.installed = installed
                modifyinformation.rebootRequired = reboot
                modifyinformation.date = datetime.now()
                db.session.add(modifyinformation)
            else:
                logger.debug(f"Création de l'association pour la MAJ {myUpdate} et server : {server}")
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
    names = ['Titre mise à jour', "Taille Max(Mo)", "Demande un redémarrage", "Installé", "Lien + information", "date de sortie", "dernière MAJ"]
    # updates = UpdateAssociation.query.filter_by(idServer=idServeur).all()
    updates = db.session.query(UpdateAssociation).filter(and_(UpdateAssociation.idServer==idServer,UpdateAssociation.done==False)).join(Update, UpdateAssociation.update).all()
    rows = []
    ids = [ (update.idServer,update.idUpdate) for update in updates]
    for row in updates:
        update = row.update
        rows.append([update.title, update.maxSize/1000000, row.rebootrequired, row.installed,update.url ,update.date, row.date])
        # update = Update.query.get(row.id)
        # if update:
        #     information = [update.title, update.maxSize, row.rebootrequired, row.installed, update.date]
    myServer = Server.query.get_or_404(idServer)
    return render_template('update/view.html', title= f"{myServer.name}",description=f"Voici toutes les mises à jours pour : {myServer.name}", names=names, rows=rows,ids=ids)


@updateB.get('/last', defaults={'page':1})
@updateB.get('/last/<int:page>')
def last_update(page):
    names = ['Titre mise à jour', "serveur", "date de sortie", "dernière MAJ"]
    updates = db.session.query(UpdateAssociation).filter(UpdateAssociation.done==False).join(Update, UpdateAssociation.update).paginate(page=page,per_page=10)
    ids = [(update.idServer,update.idUpdate) for update in updates.items]
    rows = [(row.update.title, "test" ,row.update.date, row.date) for row in updates.items]
    return render_template('update/tables.html', title= "Dernière mise a jours", names=names, rows=rows,ids=ids, pagination=updates,endpoint='update.last_update')


@updateB.route('/validate/<int:idServer>/<int:idUpdate>')
def validate(idUpdate,idServer):
    return "Not implemented"


@updateB.route("/test", methods=['GET', 'POST'])
def test():
    return render_template('update/view.html')