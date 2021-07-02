from flask import Flask
from config import ProdConfig,TestConfig,DevConfig


app = Flask(__name__, template_folder='template')
app.config.from_object(DevConfig)