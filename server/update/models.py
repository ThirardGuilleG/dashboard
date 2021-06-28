from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref

db = SQLAlchemy()


updates = db.Table('updates',
    db.Column('idServer', db.Integer, db.ForeignKey('server.id'), primary_key=True),
    db.Column('idUpdate', db.Integer, db.ForeignKey('update.id'), primary_key=True),
    db.Column('done', db.Boolean),
    db.Column('installed', db.Boolean),
    db.Column('rebootRequired', db.Boolean),
    db.Column('date', db.DateTime)
)

class Update(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False, unique=True)
    maxSize = db.Column(db.Integer)
    date = db.Column(db.DateTime())
    url = db.Column(db.String(100))
    updates = db.relationship('Server', secondary=updates, lazy='subquery', backref=db.backref('servers', lazy=True))


class Server(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(75), unique=True, nullable=False)
    ip = db.Column(db.String(16), unique=True, nullable=False)
    version = db.Column(db.String(50))



def get_db() -> SQLAlchemy:
    return db