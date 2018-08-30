from flask import Flask
from app.config import Config
from flask_sqlalchemy import SQLAlchemy			


app = Flask(__name__)
app.debug=True
app.config.from_object(Config)

from app import routes