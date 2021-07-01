from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import enum
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
    servers = db.relationship("UpdateAssociation", back_populates="update")


class Server(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(75), unique=True, nullable=False)
    ip = db.Column(db.String(16), unique=True, nullable=False)
    version = db.Column(db.String(50))
    description = db.Column(db.String(250))
    updates = db.relationship("UpdateAssociation", back_populates="server")


class UserType(enum.Enum):
    admin = 1
    update = 2
    server = 3
    regular = 4


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, 
        primary_key=True
        )
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


def get_db() -> SQLAlchemy:
    return db