from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    nome =db.Column(db.String(255), nullable=False)
    cognome =db.Column(db.String(255), nullable=False)
    data_nascita = db.Column(db.Date, nullable=False)
    luogo_nascita = db.Column(db.String(255), nullable=False)
    codice_fiscale = db.Column(db.String(16),unique=True, nullable=True)
    sesso = db.Column(db.String(2), nullable=False)
    prov = db.Column(db.String(5), nullable=False)