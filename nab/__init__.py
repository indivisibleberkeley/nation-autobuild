from flask import Flask
from nab.database import NationAutoBuildDatabase
import signal
import os

app = Flask(__name__)
app.config.update(os.environ)
if os.path.isfile("nab/config.json"):
    app.config.from_json("config.json")

from nab import routes
