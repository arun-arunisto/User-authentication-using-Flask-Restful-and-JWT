from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(70), unique=True)
    password = db.Column(db.String(500))

    def __init__(self, name, email, password):
        self.public_id = str(uuid.uuid4())
        self.name = name
        self.email = email
        self.password = generate_password_hash(password)

