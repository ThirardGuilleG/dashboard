# Test des fonctions en rapport avec les MAJs
from datetime import datetime, time, timedelta
import unittest
from loguru import logger
from database.models import db, Update, UpdateAssociation, Server
import sqlalchemy
from models import Model

class TestUpdates(Model, unittest.TestCase):
    """
    Test des fonction pour les updates
    """

    def test_lookup(self):
        """ test si aucune donnée de base"""
        updates = Update.query.all()
        self.assertEqual(len(updates), 0, "aucune donnée de base ne doit exister")
    
    def test_add(self):
        """ test l'ajout d'une MAJ """
        update = Update(kb="kb0514335", title="test update", description="an awsome test description", size="150kb", date=datetime.now(), infoUrl="http://test.fr")
        db.session.add(update)
        db.session.commit()
        logger.debug("records :")
        logger.debug(Update.query.all())
        self.assertIsNotNone(Update.query.all())
        self.assertEqual(len(Update.query.all()), 1, "il doit exister une MAJ en bdd")

    def test_failed_add_update(self):
        """ test l'unicité du kb et du title d'une MAJ """
        update = Update(kb="kb0514335", title="test update", description="an awsome test description", size="150kb", date=datetime.now(), infoUrl="http://test.fr")
        db.session.add(update)
        db.session.commit() 
        unique_kb = Update(kb="kb0514335", title="an other test update", description="an awsome test description", size="150kb", date=datetime.now(), infoUrl="http://test.fr")
        # on test que le kb est unique
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            db.session.add(unique_kb)
            db.session.commit() 
        # on retire le dernier ajout 
        db.session.rollback()
        # on test que le titre est unique
        unique_title = Update(kb="kb0514335", title="test update", description="an awsome test description", size="150kb", date=datetime.now(), infoUrl="http://test.fr")
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            db.session.add(unique_title)
            db.session.commit()    
        db.session.rollback()
        
    def test_order_by_date(self):
        """ test la query avec les updates les plus récentes en premier"""
        yesterday = (datetime.now() - timedelta(days=1))
        now = datetime.now()
        update = Update(kb="kb0514335", title="test update", date=now, infoUrl="http://test.fr")
        update_yesterday = Update(kb="kb0514336", title="test update2", date=yesterday, infoUrl="http://test.fr")
        db.session.add(update)
        db.session.add(update_yesterday)
        query = db.session.query(Update).order_by(Update.date.desc()).all()
        logger.debug(f"{query=}")
        self.assertNotEqual(query, [], "La recherche ne peut pas etre nulle")
        self.assertEqual(query[0].date, now)
        self.assertEqual(query[1].date, yesterday)

