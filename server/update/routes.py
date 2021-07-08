from flask import Blueprint, request, jsonify, render_template, flash, url_for
import json
from sqlalchemy import and_
from loguru import logger
from werkzeug.utils import redirect
from database.models import Server, Update, get_db, UpdateAssociation
from update.utils import addUpdates, doneUpdates


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
        statut = addUpdates(resp.get('updates'))
        doneUpdates(resp.get('history'))
        need_restart = resp.get('needRestart')
        server = resp.get('server')
        queryServer = Server.query.filter_by(name=server).first()
        if queryServer:
            logger.debug(f'Update etat du serveur {server}')
            queryServer.rebootrequired = need_restart
            db.session.add(queryServer)
            db.session.commit()
        return jsonify(statut)


@updateB.route('/<int:idServer>')
def update(idServer):
    names = ['Titre mise à jour', "Taille Max(Mo)", "Demande un redémarrage", "Installé", "Lien + information", "date de sortie", "dernière MAJ"]
    # updates = UpdateAssociation.query.filter_by(idServer=idServeur).all()
    updates = db.session.query(UpdateAssociation).filter(and_(UpdateAssociation.idServer==idServer,UpdateAssociation.done==False)).join(Update, UpdateAssociation.update).all()
    done = db.session.query(UpdateAssociation).filter(and_(UpdateAssociation.idServer==idServer,UpdateAssociation.done==True)).join(Update, UpdateAssociation.update).all()
    doneUpdates = [ (update.update.title, update.update.kb, update.date) for update in done]
    rows = []
    ids = [ (update.idServer,update.idUpdate) for update in updates]
    for row in updates:
        update = row.update
        rows.append([update.title, update.size, row.rebootrequired, row.installed,row.downloaded ,update.infoUrl ,update.date, row.date])
    logger.debug(rows)
    myServer = Server.query.get_or_404(idServer)
    return render_template('update/view.html', title= f"{myServer.name}",description=f"Voici toutes les mises à jours pour : {myServer.name}", 
            names=names, rows=rows, ids=ids, doneUpdates=doneUpdates)


@updateB.get('/last', defaults={'page':1})
@updateB.get('/last/<int:page>')
def last_update(page):
    names = ['Titre mise à jour', "serveur", "date de sortie", "dernière MAJ"]
    updates = db.session.query(UpdateAssociation).filter(UpdateAssociation.done==False).join(Update, UpdateAssociation.update).paginate(page=page,per_page=1000)
    ids = [(update.idServer,update.idUpdate) for update in updates.items]
    rows = [(row.update.title, row.server.name ,row.update.date, row.date) for row in updates.items]
    return render_template('update/tables.html', title= "Dernière mise a jours", names=names, rows=rows,ids=ids, pagination=updates,endpoint='update.last_update')


@updateB.route('/validate/<int:idServer>/<int:idUpdate>')
def validate(idUpdate,idServer):
    valide_update = UpdateAssociation.query.filter(and_(UpdateAssociation.idUpdate==idUpdate,UpdateAssociation.idServer==idServer)).first()
    if valide_update:
        valide_update.done = True
        valide_update.downloaded = True
        valide_update.installed = True
        db.session.add(valide_update)
        db.session.commit()
        flash("Validation réussie", "success")
        return redirect(url_for('update.update', idServer=idServer))
    flash("erreur dans la validation", "error")
    return redirect(url_for('update.update', idServer=idServer))


@updateB.route("/test", methods=['GET', 'POST'])
def test():
    return render_template('update/view.html')