# Test des fonctions en rapport avec les MAJs
import unittest
from createApp import app
from database.models import db
from config import TestConfig


class Model(unittest.TestCase):
    def setUp(self):
        app.config.from_object(TestConfig)
        db.session.close()
        db.drop_all()
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()


# lancement des tests 
# python -m unittest discover -s test -p "*_test.py"