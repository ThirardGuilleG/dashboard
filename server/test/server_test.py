from enum import unique
from re import search
from models import Model
import unittest
from database.models import db, Server
from loguru import logger
import sqlalchemy


class TestServer(Model, unittest.TestCase):
    """
    Test de la table serveur
    """
    def test_empty(self):
        """ Aucune donnée """
        search = Server.query.all()
        logger.debug(f"{search=}")
        self.assertEqual(search, [], "il ne doit y avoir aucune donnée") 

    def test_add(self):
        """ ajout d'un serveur"""
        server_to_add = Server(name="test server", ip="127.0.0.1", version="19", description="an awsome description", active=True)
        db.session.add(server_to_add)
        db.session.commit()
        all_server = Server.query.all()
        logger.debug(f"{all_server =}")
        logger.debug(all_server[0].active)
        self.assertNotEqual(all_server, [], "la recherche ne peut pas etre nul")
        self.assertEqual(len(all_server), 1, "il doit y avoir 1 server en bdd") 
    
    def test_default_state(self):
        """ Valeurs par défaut pour active et rebootrequired doit etre False"""
        server_to_add = Server(name="test", ip="127.0.0.1", version="19", description="an awsome description")
        db.session.add(server_to_add)
        db.session.commit()
        test_server = Server.query.filter_by(name="test").first()
        self.assertIsNotNone(test_server)
        self.assertFalse(test_server.active)
        self.assertFalse(test_server.rebootrequired)

    def test_failed_unique_constraint(self):
        """ test que le nom et l'ip sont uniques"""
        server_to_add = Server(name="test", ip="127.0.0.1", version="19", description="an awsome description")
        db.session.add(server_to_add)
        db.session.commit()
        unique_ip = Server(name="test2", ip="127.0.0.1", version="19", description="an awsome description")
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            db.session.add(unique_ip)
            db.session.commit()
        db.session.rollback()
        unique_name = Server(name="test", ip="0.0.0.0", version="19", description="an awsome description")
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            db.session.add(unique_name)
            db.session.commit()
        db.session.rollback()

    def test_search_active(self):
        """test de recherche des serveurs actif"""
        servers = [
            Server(name="test", ip="10.0.0.2", version="19", description="an awsome description", active=True),
            Server(name="test2", ip="10.0.0.3", version="19", description="an awsome description2", active=True),
            Server(name="test3", ip="10.0.0.4", version="19", description="an awsome description3", active=True),
            Server(name="test4", ip="10.0.0.5", version="19", description="an awsome description4")
        ]
        db.session.add_all(servers)
        db.session.commit()
        self.assertEqual(len(Server.query.all()), 4, "Il doit y avoir 4 serveur en bdd")
        self.assertEqual(len( Server.query.filter_by(active=True).all()), 3, "il doit y avoir 3 serveur activés")

    def test_search_need_reboot(self):
        """ test d'une recherche sur rebootrequired"""
        servers = [
            Server(name="test", ip="10.0.0.2", version="19", description="an awsome description", rebootrequired=True),
            Server(name="test2", ip="10.0.0.3", version="19", description="an awsome description2", rebootrequired=True),
            Server(name="test3", ip="10.0.0.4", version="19", description="an awsome description3", rebootrequired=True),
            Server(name="test4", ip="10.0.0.5", version="19", description="an awsome description4")
        ]
        db.session.add_all(servers)
        db.session.commit()
        rebootrequired_servers = Server.query.filter_by(rebootrequired=True).all()
        self.assertEqual(len(Server.query.all()), 4)
        self.assertNotEqual(rebootrequired_servers, [])
        self.assertEqual(len(rebootrequired_servers),3)

    def test_version_group(self):
        """ test de query group_by par la version windows"""
        servers = [
            Server(name="test", ip="10.0.0.2", version="19", description="an awsome description"),
            Server(name="test2", ip="10.0.0.3", version="16", description="an awsome description2"),
            Server(name="test3", ip="10.0.0.4", version="19", description="an awsome description3"),
            Server(name="test4", ip="10.0.0.5", version="12", description="an awsome description4"),
            Server(name="test5", ip="10.0.0.6", version="12", description="an awsome description5"),
            Server(name="test6", ip="10.0.0.7", version="19", description="an awsome description6")
        ]
        db.session.add_all(servers)
        db.session.commit()
        search = db.session.query(Server.version, sqlalchemy.func.count(Server.name)).group_by(Server.version).all()
        logger.debug(f"{search=}")
        self.assertEqual(len(search), 3)
        self.assertEqual(search[0], ('12', 2))
        self.assertEqual(search[1], ('16', 1))
        self.assertEqual(search[2], ('19', 3))


