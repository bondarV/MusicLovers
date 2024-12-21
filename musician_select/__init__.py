
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import urllib

from sqlalchemy import MetaData

from config import Config

from flask_bcrypt import Bcrypt
from flask_login import LoginManager
app = Flask(__name__)

app.config.from_object(Config)
app.config.from_object(Config)

metadata = MetaData(naming_convention={
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
})

db = SQLAlchemy(app,metadata=metadata)
migrate = Migrate(app, db)

# app.app_context().push()
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = "login_page"
login_manager.login_message_category = "info"

from musician_select import routes,models  #avoid circular imports
