from flask import Flask
from config import ProdConfig,TestConfig,DevConfig
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__, template_folder='template')
app.config.from_object(DevConfig)


# import routes
from Blueprint.update.routes import updateB
from Blueprint.admin.routes import adminB
from Blueprint.auth.routes import authB

from database.models import db, User

# Blueprint
app.register_blueprint(updateB)
app.register_blueprint(adminB)
app.register_blueprint(authB)

# Bootstrap
Bootstrap(app)

# Database
db.app = app
db.init_app(app)
db.create_all()

# Migration de bdd (update et ajout de table)
migrate = Migrate(app, db)

# connection
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = "info"
login_manager.login_message  = "Veuillez vous connecter"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    """Check if user is logged-in on every page load."""
    if user_id is not None:
        return User.query.get(user_id)
    return None