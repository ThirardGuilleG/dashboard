from datetime import datetime
from models import Model
from database.models import db, Server, Update, UpdateAssociation
import unittest
from datetime import datetime
from loguru import logger


class TestAssociationUpdate(Model, unittest.TestCase):
    def add_data(self):
        """ enregistrement de données pour effectuer des tests"""
        servers = [ 
            Server(name="server1", ip="10.0.0.1"),
            Server(name="server2", ip="10.0.0.2"),
            Server(name="server3", ip="10.0.0.3")
        ]
        updates = [
            Update(kb="kb444545", title="update1", date=datetime.now()),
            Update(kb="kb444546", title="update2", date=datetime.now()),
            Update(kb="kb444547", title="update3", date=datetime.now()),
            Update(kb="kb444548", title="update4", date=datetime.now()),
            Update(kb="kb444549", title="update5", date=datetime.now())
        ]
        db.session.add_all(servers)
        db.session.add_all(updates)
        db.session.commit()

    def test_data(self):
        """ test si la donnée enregistrer de base est ok"""
        # ajout des données de base
        self.add_data()
        servers = Server.query.all()
        updates = Update.query.all()
        logger.debug(servers)
        self.assertEqual(len(updates), 5, "Il doit exister 5 update en bdd")
        self.assertEqual(len(servers), 3, "Il doit exister 3 serveur en bdd") 

    def test_add(self):
        """ test l'ajout d'une association"""
        # ajout des données de base
        self.add_data()
        update = Update.query.filter_by(kb="kb444545").first()
        update2 = Update.query.filter_by(kb="kb444546").first()
        server = Server.query.filter_by(name="server1").first()
        # ajout des données en plus
        association = UpdateAssociation(done=False,downloaded=False, rebootrequired=False,date=datetime.now(), installed=False) 
        association2 = UpdateAssociation(done=True,downloaded=True, rebootrequired=True,date=datetime.now(), installed=True) 
        # Ajout du server relié à l'update
        with db.session.no_autoflush:
            # 1
            association.update = update
            server.updates.append(association)
            db.session.add(server)
            # 2
            association2.update = update2
            server.updates.append(association2)
            db.session.add(server)
        db.session.commit()
        search = UpdateAssociation.query.filter_by(idServer=server.id).all()
        self.assertEqual(len(search), 2, "Il doit y avoir 2 association pour le serveur")

    def test_multiple(self):
        """ test l'ajout de plusieurs maj sur plusieurs serveurs"""
        # ajout des données de base
        self.add_data()
        # Updates
        update = Update.query.filter_by(kb="kb444549").first()
        update2 = Update.query.filter_by(kb="kb444546").first()
        # Servers
        server = Server.query.filter_by(name="server1").first()
        server2 = Server.query.filter_by(name="server2").first()
        # Etat de l'update
        association = UpdateAssociation(done=False,downloaded=False, rebootrequired=False,date=datetime.now(), installed=False) 
        association2 = UpdateAssociation(done=True,downloaded=True, rebootrequired=True,date=datetime.now(), installed=True) 
        # server 1
        with db.session.no_autoflush:
            # 1 | 1
            association.update = update
            server.updates.append(association)
            db.session.add(server)
            # 2 | 1
            association2.update = update2
            server.updates.append(association2)
            db.session.add(server)
        db.session.commit()
        # Etat de l'update
        association = UpdateAssociation(done=False,downloaded=False, rebootrequired=False,date=datetime.now(), installed=False) 
        association2 = UpdateAssociation(done=True,downloaded=True, rebootrequired=True,date=datetime.now(), installed=True) 
        # server 2
        with db.session.no_autoflush:
            # 1 | 2
            association.update = update
            server2.updates.append(association)
            db.session.add(server2)
            # 2 | 2
            association2.update = update2
            server2.updates.append(association2)
            db.session.add(server2)
        db.session.commit()
        search = UpdateAssociation.query.all()
        logger.debug(f"{search=}")
        # bon nombre de maj
        self.assertEqual(len(search), 4, "Il doit y avoir 4 association en tous")
        self.assertEqual(len(UpdateAssociation.query.filter_by(idUpdate=update.id).all()), 2, "L'update 1 doit etre associé au 2 serveur")
        self.assertEqual(len(UpdateAssociation.query.filter_by(idUpdate=update2.id).all()), 2, "L'update 2 doit etre associé au 2 serveur")
        self.assertEqual(len(UpdateAssociation.query.filter_by(idServer=server.id).all()), 2, "Le serveur 1 doit avoir 2 MAJ associé")
        self.assertEqual(len(UpdateAssociation.query.filter_by(idServer=server2.id).all()), 2, "Le serveur 2 doit avoir 2 MAJ associé")
        # test information ok
        self.assertEqual(search[0].server.id, 1, "L'association 1 doit etre reliée au serveur d'id 1")
        self.assertEqual(search[0].update.id, 5, "L'association 1 doit etre reliée a la MAJ d'id 5")
        self.assertEqual(search[1].server.id, 1, "L'association 2 doit etre reliée au serveur d'id 1")
        self.assertEqual(search[1].update.id, 2, "L'association 2 doit etre reliée au serveur d'id 2")
        self.assertEqual(search[2].server.id, 2, "L'association 3 doit etre reliée au serveur d'id 2")
        self.assertEqual(search[2].update.id, 5, "L'association 3 doit etre reliée au serveur d'id 5")
    
    def test_done(self):
        # ajout des données de base
        self.add_data()
        # Updates
        update = Update.query.filter_by(kb="kb444549").first()
        update2 = Update.query.filter_by(kb="kb444546").first()
        update3 = Update.query.filter_by(kb="kb444547").first()
        # Servers
        server = Server.query.filter_by(name="server3").first()
        # Etat de l'update
        association = UpdateAssociation(done=False,downloaded=False, rebootrequired=False,date=datetime.now(), installed=False) 
        association2 = UpdateAssociation(done=True,downloaded=True, rebootrequired=True,date=datetime.now(), installed=True) 
        association3 = UpdateAssociation(done=True,downloaded=True, rebootrequired=True,date=datetime.now(), installed=True) 
        with db.session.no_autoflush:
            # 1 
            association.update = update
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
        db.session.commit()
        self.assertEqual(len(UpdateAssociation.query.filter_by(done=True).all()), 2, " Il doit y avoir 2 MAJ avec l'etat done à True")
        self.assertEqual(len(UpdateAssociation.query.all()), 3, " Il doit y avoir 3 MAJ en BDD")