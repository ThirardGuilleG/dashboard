from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import enum
db = SQLAlchemy()


class UpdateAssociation(db.Model):
    """ Table qui gère l'association entre une update et un serveur.
    Gère également l'état de l'update (téléchargé/installé/fini)
    """
    __tablename__ = "UpdateAssociation"
    idUpdate = db.Column(db.Integer, db.ForeignKey('update.id'), primary_key=True)
    idServer = db.Column(db.Integer, db.ForeignKey('server.id'), primary_key=True)
    done = db.Column(db.Boolean)
    installed = db.Column(db.Boolean)
    downloaded = db.Column(db.Boolean)
    rebootrequired = db.Column(db.Boolean, default=False)
    date = db.Column(db.DateTime)
    server = db.relationship("Server", back_populates="updates")
    update = db.relationship("Update", back_populates="servers")


class Update(db.Model):
    """
    Table qui gère les différentes mise à jours.
    """
    id = db.Column(db.Integer, primary_key=True)
    kb = db.Column(db.String(15), unique=True)
    title = db.Column(db.String(250), nullable=False, unique=True)
    description = db.Column(db.String(350))
    size = db.Column(db.String(15))
    date = db.Column(db.DateTime(), default=datetime.now())
    infoUrl = db.Column(db.String(250))
    servers = db.relationship("UpdateAssociation", back_populates="update")


class Server(db.Model):
    """
    Table de gestion des serveurs.
    TODO Récupérer dans l'ad ?
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(75), unique=True, nullable=False)
    ip = db.Column(db.String(16), unique=True, nullable=False)
    version = db.Column(db.String(50))
    description = db.Column(db.String(250))
    rebootrequired = db.Column(db.Boolean, default=False)
    updates = db.relationship("UpdateAssociation", back_populates="server")
    bind_etat = db.relationship("Etat_Service", backref="etat", uselist=False)


class UserType(enum.Enum):
    """
    Pas utilisé et temporaire 
    """
    admin = 1
    update = 2
    server = 3
    regular = 4


class User(db.Model, UserMixin):
    """
    Table de gestions des utilisateurs. Egalement utilise par flask_login pour la connection utilisateur.
    """
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(75))
    lastname = db.Column(db.String(75))
    username = db.Column(db.String(75), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    type = db.Column(db.Integer, nullable=False)
    creation_date = db.Column(db.DateTime) 
    last_connection_date = db.Column(db.DateTime) 

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(
            password,
            method='sha256'
        )
    
    def check_password(self, password):
        return check_password_hash(self.password,password)


class Etat_Service(db.Model):
    __tablename__ = 'Etat Service'
    id = db.Column(db.Integer, primary_key=True)
    zabbix = db.Column(db.Boolean, default=False)
    graylog_sidecar = db.Column(db.Boolean, default=False)
    winlogbeat = db.Column(db.Boolean, default=False)
    fsecure = db.Column(db.Boolean, default=False)
    fsecure_activate = db.Column(db.Boolean, default=False)
    eaton = db.Column(db.Boolean, default=False)
    last_update_date = db.Column(db.DateTime, default=datetime.now())
    id_server = db.Column(db.Integer, db.ForeignKey('server.id'))


def get_db() -> SQLAlchemy:
    """
        obtention de l'objet db
    """
    return db