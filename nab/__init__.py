from flask import Flask
from nab.database import NationAutoBuildDatabase
import signal

app = Flask(__name__)
app.config.from_json("config.json")

from nab import routes
