import json
from flask.helpers import url_for
import requests
from database.models import UpdateAssociation, Server
from pathlib import Path
from loguru import logger
from sqlalchemy import and_
import os
import requests
import certifi
# https://dummyimage.com/ api de création d'img


def get_img(text: str, name_file: str, width: int = 400, text_color:str = "000000", background_color: str = "ffffff"):
    """Génération d'une image PNG en fonction des critéres demandés

    Args:
        text (str): Texte dans l'image
        name_file (str): Nom du fichier
        width (int, optional): Taille de l'image. Defaults to 400.
        text_color (str, optional): Couleur du texte. Fromat suivant : #000000. Defaults to "000000".
        background_color (str, optional): Couleur du fond de l'image. Format suivant : #cccccc Defaults to "ffffff".

    Returns:
        bool: True si l'image est généré avec succés sinon False
    """
    url = f"https://dummyimage.com/{ width }/{background_color }/{ text_color }&text={ text }"
    response = requests.get(url)
    path_to_file = Path(__file__).absolute().parent.__str__() + "\\static\\img\\number\\" + name_file
    logger.debug(path_to_file)
    try:
        with open(path_to_file.__str__(), "wb") as file:
            file.write(response.content)
        return True
    except OSError as errO:
        logger.exception(errO)
        return False


def get_number_update(idServer: int):
    """Obtention du nombre de MAJ en cours pour un serveur

    Args:
        idServer (int): id du serveur

    Returns:
        int: Nombre de MAJ
    """
    updates = UpdateAssociation.query.filter(and_(UpdateAssociation.idServer==idServer,UpdateAssociation.done==False)).all()
    return len(updates) if updates else "O" # return de O car 0 pas géré par l'api 


def get_or_create_img(idServer: int):
    """Creation d'une image avec le nombre de MAJ si nécessaire pour un serveur ou obtention du path si elle existe déjà.

    Args:
        idServer (int): id du serveur.

    Returns:
        str: Path de l'image crée ou de l'image trouvée
    """ 
    number = get_number_update(idServer)
    logger.debug(f"{number} MAJ pour id server :{idServer}")
    filename = f"{number}.png"
    path = Path(__file__).absolute().parent.__str__() + "\\static\\img\\number\\" + filename
    logger.debug(f'{path=}')
    if not Path(path).is_file():
        logger.debug(f"Creation img pour : {idServer}")
        if not get_img(text=str(number), name_file=filename):
            logger.warning("Erreur dans la génération de l'image")
            return url_for('static', filename=f"img/number/error.png")
    logger.debug("Image existe déjà")
    return url_for('static', filename=f"img/number/{filename}")


def test_dashboard_alert(url_dashboard: str = "https://grafana.thirard.fr:3000/api/dashboards/uid/H76dsyinz"):
    """Test la présence d'alert pour nos serveurs
        Le nom de la row contenant les alertes doit etre nommée correctement.
    Args:
        url_dashboard (str, optional): url du dashboard grafana. Defaults to "https://grafana.thirard.fr:3000/api/dashboards/uid/H76dsyinz".
    """
    payload={}
    headers = {
    'Authorization': 'Bearer eyJrIjoieW5PSG1Sck53TnBZMlpKNjZQOGZKVjZocFhVbFNVWGUiLCJuIjoiZWRpdCIsImlkIjoxfQ=='
    }
    try:
        response = requests.get(url_dashboard, headers=headers, data=payload)
        # reponse json
        json_response = json.loads(response.text)
        # list serveurs
        list_serveurs = [server.Name for server in Server.query.all()] 
        logger.debug(list_serveurs)
        # list_debug = ['SRVT2WP', 'SRVY2ARR', 'SRVY2IISA', 'SRVY2IISB', 'SRVT2SMTP',
        #             'SRVT2EB1', 'SRVT2FS', 'SRVY2SQL', 'SRVY2RAD', 'SRVY2RPT',
        #             'SRVY2WP', 'SRVT2EB2', 'SRVT2OXO', 'SRVT2RDS', 'SRVT2ST', 
        #             'VMCOMMUNICATION', 'VMAUTOMATISME', 'VMBOA', 'SRVT2SV', 'SRVT2SL2',
        #             'SRV80390Q1', 'VMTBD', 'VMOPTIMAPOLSKA', 'VMINTRANET', 
        #             'VMSTATISTIQUES', 'SRVT2CIEL', 'SRVSAGEV8', 'SRVAMADA', 
        #             'SRVT2VEEAM']
        dashboard = json_response.get('dashboard', {})
        grafana_id = dashboard.get('id')
        panels = dashboard.get("panels", [])
        for panel in panels:
            if panel.get('type') == 'row':
                row_title = panel.get('title')
                row_title = row_title.strip()
                # si on trouve le serveur on le retire de la liste
                if row_title in list_serveurs:
                    list_serveurs.pop(list_serveurs.index(row_title))
            # sub_panels = panel.get('panels', [])
            # for sub_panel in sub_panels:
            #     logger.debug(sub_panel)
        logger.info("Pas d'alert configuré pour les serveurs suivants :")
        logger.info(list_serveurs)
        return list_serveurs
    except requests.exceptions.SSLError as err:
        print('SSL Error. Adding custom certs to Certifi store...')
        cafile = certifi.where()
        with open('chain.pem', 'rb') as infile:
            customca = infile.read()
        with open(cafile, 'ab') as outfile:
            outfile.write(customca)
            print('That might have worked.')


if __name__ == "__main__":
    # get_img("12", 400, "000000", "ffffff","12.png")
    test_dashboard_alert()