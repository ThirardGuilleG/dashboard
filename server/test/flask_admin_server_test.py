from models import Model
from database.models import db, Server, Update, UpdateAssociation
from Blueprint.admin.models import ServerForm 
import unittest
from loguru import logger
from createApp import app
import sqlalchemy


def app_context():
    with app.app_context():
        yield


class TestFlaskAddUpdate(Model, unittest.TestCase):
    def test_server_form(self):
        "test du formulaire d'ajout de Server"
        # form = ServerForm()
        pass

    def test_server_add(self):
        " test de l'ajout du serveur"
        app_context()
        self.assertEqual(len(Server.query.all()), 0, "il ne doit exister aucun serveur")
        with app.test_client() as c:
            # ajout du serveur
            response = c.post('/admin/add/server', data={'name': 'srvtest', 'ip':'10.10.10.10', 'version': '19', 'description': 'this test must work'})
            logger.debug(response.status_code)
            self.assertEqual(len(Server.query.all()), 1, "1 serveur doit etre crée en bdd")
            # mauvaise ip
            c.post('/admin/add/server', data={'name': 'srvtest2', 'ip':'10.10.10', 'version': '19', 'description': 'this test must not work'})
            self.assertEqual(len(Server.query.all()), 1, "Le serveur ne doit pas etre rajouté car son ip est mauvaise")
            # unique
            with self.assertRaises(sqlalchemy.exc.IntegrityError):
                c.post('/admin/add/server', data={'name': 'srvtest', 'ip':'10.10.10.10', 'version': '19', 'description': 'this test must not work'})
