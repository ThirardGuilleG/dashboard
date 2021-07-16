from flask.helpers import url_for
import requests
from database.models import UpdateAssociation
from pathlib import Path
from loguru import logger
from sqlalchemy import and_
import os
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
    path = os.path.abspath(os.getcwd())
    try:
        with open(f"{path}/static/img/number/{name_file}", "wb") as file:
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
    current_path = os.path.abspath(os.getcwd())
    logger.debug(current_path)
    path = f"{current_path}/static/img/number/{filename}"
    if not Path(path).is_file():
        logger.debug(f"Creation img pour : {idServer}")
        if not get_img(text=str(number), name_file=filename):
            logger.warning("Erreur dans la génération de l'image")
            return url_for('static', filename=f"img/number/error.png")
    logger.debug("Image existe déjà")
    return url_for('static', filename=f"img/number/{filename}")




if __name__ == "__main__":
    # get_img("12", 400, "000000", "ffffff","12.png")
    print(get_number_update(2))