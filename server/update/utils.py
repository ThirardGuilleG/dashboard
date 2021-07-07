from database.models import Update,Server,UpdateAssociation, get_db
from sqlalchemy import and_, or_
from datetime import datetime
from loguru import logger

import enum

db = get_db()

class Etat(enum.Enum):
    """
    Etat des mise à jours
    """
    Succeeded = True
    Failed = False
    Aborted = False
    InProgress = False


def doneUpdates(history_updates: list):
    """Passe une mise à jours à done si elle est trouvée dans l'historique des mise à jours

    Args:
        history_updates (list): liste contenant l'historique des mise à jours sur 5 jours
    """
    
    try:
        for update in history_updates:
            server = update.get('ComputerName')
            kb = update.get('KB')
            title = update.get('Title')
            date = datetime.fromtimestamp(int(update.get('Date')[6:16]))
            result = Etat[update.get('Result').strip()]
            logger.debug(f"check des mise à jours pour : {server}")
            if result.value is True:
                s = Server.query.filter_by(name=server).first()
                update = Update.query.filter(or_(Update.kb==kb,Update.title==title)).first()
                if update:
                    uptade_to_valid = UpdateAssociation.query.filter(and_(UpdateAssociation.idUpdate==update.id,
                                                                    UpdateAssociation.idServer==s.id), UpdateAssociation.done==False).first()
                    # Update des informations
                    if uptade_to_valid:
                        logger.info(f"La mise à jours : {uptade_to_valid.idUpdate} est ok pour : {server}")
                        uptade_to_valid.done=True
                        uptade_to_valid.date=date
                        uptade_to_valid.installed=True
                        uptade_to_valid.downloaded=True
                        uptade_to_valid.rebootrequired=False
                        db.session.add(uptade_to_valid)
                        db.session.commit()
    except Exception as err:
        logger.exception(err)


class Response(enum.Enum):
    """
    Reponse à renvoyer
    """
    success = ("success", 201)
    error = ("error", 202)
    something_wrong = ("Not all data has been handled check logs", 202)



def addUpdates(pUpdates: list):
    """Ajoute les mise à jours et les associations avec les serveurs

    Args:
        pUpdates (list): liste de mise à jours pour un serveur

    Returns:
        tuple: (message,code_http)
    """
    try:
        response = Response.success.value
        logger.debug(f"DATA : {pUpdates}")
        # check si on obtiens un dict vide
        if pUpdates != {}:
            # check si l'objet obtenu est bien une liste (dans le cas ou une seul maj est trouvé on obtient un dict)
            if not (isinstance(pUpdates, list)):
                pUpdates = [pUpdates]
                logger.debug(f'new data : {pUpdates}')
            for update in pUpdates:
                try:
                    title = update.get('Title').encode('utf-8')
                    description = update.get('Description').encode('utf-8')
                    server = update.get('ComputerName')
                    size = update.get('Size')
                    kb = update.get('KB')
                    reboot = update.get('RebootRequired')
                    installed = update.get('IsInstalled')
                    downloaded = update.get('IsDownloaded')
                    url = update.get('MoreInfoUrls')
                    deployementDate = datetime.fromtimestamp(int(update.get('LastDeploymentChangeTime')[6:16]))
                    logger.debug(deployementDate)
                    logger.info(f'Mise à jour récupérée pour : {server}')
                except AttributeError as errA:
                    logger.exception(errA)
                    return Response.something_wrong.value
                # Server
                myServer = Server.query.filter_by(name=server).first()
                if not myServer:
                    logger.warning("le serveur n'est pas en bdd")
                    return Response.something_wrong.value
                myUpdate = Update.query.filter(or_(Update.kb==kb,Update.title==title)).first()
                logger.debug(myUpdate)
                # Création de la MAJ si elle existe pas
                if not myUpdate:
                    logger.debug(f"Création de la MAJ : {kb}")
                    newUpdate = Update(kb=kb,title=title,date=deployementDate,size=size,infoUrl=url,description=description)
                    myUpdate = newUpdate

                modifyinformation = UpdateAssociation.query.filter_by(idUpdate=myUpdate.id,idServer=myServer.id).first()
                # Regarde la chaine so
                if modifyinformation:
                    # mise à jour des informations
                    logger.debug(f"L'association entre la MAJ {modifyinformation} existe déjà modification des informations")
                    modifyinformation.installed = installed
                    modifyinformation.downloaded = downloaded
                    modifyinformation.rebootRequired = reboot
                    modifyinformation.date = datetime.now()
                    db.session.add(modifyinformation)
                else:
                    logger.debug(f"Création de l'association pour la MAJ {myUpdate} et server : {server}")
                    with db.session.no_autoflush:
                        # Création de l'association
                        # ajout des données en plus
                        association = UpdateAssociation(done=False,downloaded=downloaded, rebootrequired=reboot,date=datetime.now(), installed=installed) 
                        # Ajout du server relié à l'update
                        db.session.no_autoflush
                        association.update = myUpdate
                        # ajout en bdd
                        myServer.updates.append(association)
                        db.session.add(myServer)
                db.session.commit()
            return response
    except Exception as err:
        logger.exception(err)
        return Response.error.value

