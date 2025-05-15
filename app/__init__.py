# app/__init__.py
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask
from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)

cred = credentials.Certificate(Config.FIREBASE_CRED_PATH)
firebase_admin.initialize_app(cred)

db = firestore.client()

from app.routes import data, plot, analyze, export, range