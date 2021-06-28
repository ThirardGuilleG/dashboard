from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref

db = SQLAlchemy()


class UpdateAssociation(db.Model):
    __tablename__ = "UpdateAssociation"
    idUpdate = db.Column(db.Integer, db.ForeignKey('update.id'), primary_key=True)
    idServer = db.Column(db.Integer, db.ForeignKey('server.id'), primary_key=True)
    done = db.Column(db.Boolean)
    installed = db.Column(db.Boolean)
    rebootrequired = db.Column(db.Boolean)
    date = db.Column(db.DateTime)
    server = db.relationship("Server", back_populates="updates")
    update = db.relationship("Update", back_populates="servers")


class Update(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False, unique=True)
    maxSize = db.Column(db.Integer)
    date = db.Column(db.DateTime())
    url = db.Column(db.String(100))
    # updates = db.relationship('Server', secondary=updates, lazy='subquery', backref=db.backref('servers', lazy=True))
    servers = db.relationship("UpdateAssociation", back_populates="update")


class Server(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(75), unique=True, nullable=False)
    ip = db.Column(db.String(16), unique=True, nullable=False)
    version = db.Column(db.String(50))
    updates = db.relationship("UpdateAssociation", back_populates="server")



def get_db() -> SQLAlchemy:
    return db