from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask("hello")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class StorageItem(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    handle = db.Column(db.String(64), unique = True, nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
