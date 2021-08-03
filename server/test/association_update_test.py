from datetime import datetime
from models import Model
from database.models import db, Server, Update, UpdateAssociation
import unittest
from datetime import datetime
from loguru import logger


class TestAssociationUpdate(Model, unittest.TestCase):
    def add_data(self):
        servers = [ 
            Server(name="server1", ip="10.0.0.1"),
            Server(name="server2", ip="10.0.0.2"),
            Server(name="server3", ip="10.0.0.3")
        ]
        update = [
            Update(kb="kb444545", title="update1", date=datetime.now()),
            Update(kb="kb444546", title="update2", date=datetime.now()),
            Update(kb="kb444547", title="update3", date=datetime.now()),
            Update(kb="kb444548", title="update4", date=datetime.now()),
            Update(kb="kb444549", title="update5", date=datetime.now())
        ]
        db.session.add_all(servers)
        db.session.add_all(update)
        db.session.commit()

    def test_data(self):
        # ajout des données de base
        self.add_data()
        servers = Server.query.all()
        updates = Update.query.all()
        logger.debug(servers)
        assert len(servers) == 3
        assert len(updates) == 5

    def test_add(self):
        # ajout des données de base
        self.add_data()
        