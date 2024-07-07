from models import db
import uuid
from sqlalchemy import ForeignKey




class Organisation(db.Model):
    __tablename__ = 'organisations'
    orgId = db.Column(db.String(255), primary_key=True, unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    users = db.relationship('User', backref='organisation', lazy=True)





    def __init__(self, name, description=None):
        self.name = name
        self.description = f"{name}'s default description"


    def __repr__(self):
        return f"<organisation {self.orgId}, {self.name}, {self.description}>"