from models import Model
from database.models import db, Server, Update, UpdateAssociation
import unittest
from datetime import datetime
from loguru import logger
from createApp import app
import json


class TestFlaskAddUpdate(Model, unittest.TestCase):
    def test_add(self):
        with open('test/mock/updates/VMBOA.json') as j:
            # data = str(j.read()).strip("'<>() ").replace('\'', '\"')
            data = str(j.read())
            logger.debug(data[2:-1])
            updates = json.load(data)
        db.session.add(Server(name="VMBOA", ip="10.33.1.131", version="19", description="for test purposes"))
        db.session.commit()
        with app.test_client() as c:
            response = c.post('/update/data', data=updates)
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.data, "success")
