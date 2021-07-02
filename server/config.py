class Config(object):
    SECRET_KEY = 'dXrDzC9ij6YmcTFSG4a'


class ProdConfig(Config):
    ENV = 'prod'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///../server/updates.db'


class DevConfig(Config):
    ENV = 'dev'
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = 'sqlite:///../server/dev.db'


class TestConfig(Config):
    ENV = 'test'
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_ECHO = True

