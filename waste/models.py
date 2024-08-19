from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import relationship
from . import db


class HouseUser(db.Model, UserMixin):
    __tablename__ = 'houseuser'
    house_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    firstname = db.Column(db.String(150), unique=True, nullable=False)
    secondname = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    role = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)

class AdminUser(db.Model, UserMixin):
    __tablename__ = 'adminuser'
    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    companyname = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    role = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)

    def get_id(self):
        return str(self.admin_id)

class CollectorUser(db.Model, UserMixin):
    __tablename__ = 'collectoruser'
    collector_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    firstname = db.Column(db.String(150), nullable=False)
    secondname = db.Column(db.String(150), nullable=False)
    companyname = db.Column(db.String(150), db.ForeignKey('adminuser.companyname'), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    role = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)

    # Relationship with AdminUser (company)
    company = relationship('AdminUser', backref='collectors')