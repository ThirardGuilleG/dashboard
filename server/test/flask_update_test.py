from datetime import datetime
from models import Model
from database.models import db, Server, Update, UpdateAssociation
import unittest
from enum import Enum
from loguru import logger
from bs4 import BeautifulSoup
from createApp import app


# Test de la page update/X 
# X est le numéro du serveur

class IconEtat(Enum):
    """ Enum avec l'etat qui correspond à la valeur sur la page html (google fonts icon) """
    done = "task_alt"
    not_done = "highlight_off"


class TestFlaskUpdate(Model, unittest.TestCase):
    def add_data(self) -> None:
        """ ajout de donnée de base pour les tests"""
        db.session.add(Server(name="test_flask",ip="10.33.1.1",version="19"))
        updates = [
            Update(kb="kb444545", title="update1", date=datetime.now()),
            Update(kb="kb444546", title="update2", date=datetime.now()),
            Update(kb="kb444547", title="update3", date=datetime.now()),
            Update(kb="kb444548", title="update4", date=datetime.now()),
            Update(kb="kb444549", title="update5", date=datetime.now())
        ]
        db.session.add_all(updates)
        db.session.commit()
        # On associe des updates au serveur
        # server
        server = Server.query.first()
        logger.debug(f"{server=}")
        # update 1 et 2
        update1 = Update.query.filter_by(title="update1").first()
        update2 = Update.query.filter_by(title="update2").first()
        update3 = Update.query.filter_by(title="update3").first()
        update4 = Update.query.filter_by(title="update4").first()
        association = UpdateAssociation(done=False,downloaded=False, rebootrequired=False,date=datetime.now(), installed=False) 
        association2 = UpdateAssociation(done=True,downloaded=True, rebootrequired=False,date=datetime.now(), installed=True) 
        association3 = UpdateAssociation(done=False,downloaded=True, rebootrequired=True,date=datetime.now(), installed=True) 
        association4 = UpdateAssociation(done=False,downloaded=True, rebootrequired=False,date=datetime.now(), installed=False) 
        with db.session.no_autoflush:
            # 1
            association.update = update1
            server.updates.append(association)
            db.session.add(server)
            # 2
            association2.update = update2
            server.updates.append(association2)
            db.session.add(server)
            # 3
            association3.update = update3
            server.updates.append(association3)
            db.session.add(server)
            # 4
            association4.update = update4
            server.updates.append(association4)
            db.session.add(server)
        db.session.commit()

    def test_add_data(self):
        """ test des données de base"""
        self.add_data()
        logger.debug(UpdateAssociation.query.all())
        self.assertEqual(len(Server.query.all()), 1)
        self.assertEqual(len(Update.query.all()), 5)
        self.assertEqual(len(UpdateAssociation.query.all()), 4)
        self.assertEqual(len(UpdateAssociation.query.filter_by(done=False).all()), 3)
        self.assertEqual(len(UpdateAssociation.query.filter_by(rebootrequired=True).all()), 1)
        self.assertEqual(len(UpdateAssociation.query.filter_by(downloaded=True).all()), 3)
        self.assertEqual(len(UpdateAssociation.query.filter_by(installed=True).all()), 2)

    def test_response(self):
        """ test des codes de réponse """
        self.add_data()
        with app.test_client() as c:
            response = c.get('/update/1', follow_redirects=False)
            logger.debug(response)
            # le serveur 1 est trouvé
            self.assertEqual(response.status_code, 200, "le code http de réponse doit etre 200")  
            # serveur 2 n'existe pas
            self.assertEqual(c.get('/update/2', follow_redirects=False).status_code, 404, "le code http de réponse doit etre 404(le serveur n'existe pas)")           
    
    def test_in_progress_informations(self):
        """ test si les bonnes données sont affichés pour les MAJ en cours """
        self.add_data()
        with app.test_client() as c:
            response = c.get('/update/1', follow_redirects=False)
            # vérification des données sur la page 
            soup = BeautifulSoup(response.data, 'lxml')
            # mise à jours en cours
            in_progress_update = soup.find("div", {'id': 'update'})
            self.assertIsNotNone(in_progress_update, "la div contenant les maj en cours n'existe pas")
            in_progress_row = in_progress_update.tbody.find_all("tr")
            # 3 MAJ en cours
            self.assertEqual(len(in_progress_row), 3, "Il doit y avoir 3 mise à jours en cours")
            # vérification des bonnes informations
            right_informations = [
                {'title': 'update1', 'reboot': IconEtat.not_done, 'installed': IconEtat.not_done, 'downloaded': IconEtat.not_done, 'action': '/update/validate/1/1'},
                {'title': 'update3', 'reboot': IconEtat.done, 'installed': IconEtat.done, 'downloaded': IconEtat.done, 'action': '/update/validate/1/3'},
                {'title': 'update4', 'reboot': IconEtat.not_done, 'installed': IconEtat.not_done, 'downloaded': IconEtat.done, 'action': '/update/validate/1/4'}
                ]
            # updates
            for informations in zip(in_progress_row, right_informations):
                # colonnes
                data_update = informations[0].find_all('td')
                logger.debug(data_update)
                information = informations[1]
                self.assertEqual(len(data_update), 9, "il doit y avoir 9 colonnes")
                # titre
                logger.debug(f"test maj : {information.get('title')}")
                logger.debug(data_update[0].text.strip())
                self.assertEqual(data_update[0].text.strip(), information.get('title'))
                # rebootrequired
                self.assertEqual(data_update[2].text.strip(), information.get('reboot').value)
                # downloaded
                self.assertEqual(data_update[4].text.strip(), information.get('downloaded').value)
                # installed
                self.assertEqual(data_update[3].text.strip(), information.get('installed').value)
                # forcer etat
                logger.debug(data_update[-1].find('a', href=True))
                self.assertEqual(data_update[-1].find('a', href=True).get('href'), information.get('action'))
            
    def test_done_information(self):
        """ test si les bonnes données sont affichés pour les MAJ finis """
        self.add_data()
        with app.test_client() as c:
            response = c.get('/update/1', follow_redirects=False)
            # vérification des données sur la page 
            soup = BeautifulSoup(response.data, 'lxml')
            # mise à jours finis
            done_update = soup.find("div", {'id': 'update_done'})
            self.assertIsNotNone(done_update, "la div contenant les maj effectué n'existe pas")
            # 1 MAJ fini
            done_update_row = done_update.tbody.find_all("tr")
            self.assertEqual(len(done_update_row), 1, "Il doit n'y avoir que une mise à jours avec etat done")
            # vérification des bonnes informations
            data = done_update_row[0].find_all('td')
            self.assertEqual(len(data), 3, "il doit y avoir 3 colonnes")
            # titre
            logger.debug(f"{data[0].text.strip()=}")
            self.assertEqual(data[0].text.strip(), "update2", "le titre ne correspond pas")
            # kb
            self.assertEqual(data[1].text.strip(), "kb444546", "le KB ne correspond pas")
            # date
            self.assertIsNotNone(data[2].text.strip(), "la date ne doit pas etre null")

    def test_validation_update(self):
        """ test pour forcer l'etat a done pour une MAJ"""
        self.add_data()
        with app.test_client() as c:
            response = c.get('/update/1', follow_redirects=False)
            soup = BeautifulSoup(response.data, 'lxml')
            done_update = soup.find("div", {'id': 'update_done'})
            # 1 MAJ fini
            self.assertEqual(len(done_update.tbody.find_all("tr")), 1, "Il doit n'y avoir que une mise à jours avec etat done")
            # on force l'etat de maj 1 
            c.get('/update/validate/1/1', follow_redirects=True)
            # On test à nouveau
            response = c.get('/update/1', follow_redirects=False)
            soup = BeautifulSoup(response.data, 'lxml')
            done_update = soup.find("div", {'id': 'update_done'})
            # 2 MAJ fini
            self.assertEqual(len(done_update.tbody.find_all("tr")), 2, "Il doit n'y avoir que une mise à jours avec etat done")
