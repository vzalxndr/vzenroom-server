import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask
from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)

firebase_cred_json = os.environ.get("FIREBASE_CRED_JSON")

if not firebase_cred_json:
    with open(Config.FIREBASE_CRED_PATH) as f:
        firebase_cred_json = f.read()

cred_dict = json.loads(firebase_cred_json)
cred = credentials.Certificate(cred_dict)

firebase_admin.initialize_app(cred)
db = firestore.client()

from app.routes import data, plot, analyze, export, range


from app.routes import data, plot, analyze, export, range