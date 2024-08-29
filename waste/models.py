from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import relationship
from . import db

class HouseUser(db.Model, UserMixin):
    __tablename__ = 'houseuser'
    house_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    firstname = db.Column(db.String(150), nullable=False)
    secondname = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    houseemail = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_collector = db.Column(db.Boolean, default=False, nullable=False)
    is_house = db.Column(db.Boolean, default=True, nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)

    def get_id(self):
        return str(self.house_id)

class AdminUser(db.Model, UserMixin):
    __tablename__ = 'adminuser'
    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    companyname = db.Column(db.String(150), unique=True, nullable=False)
    adminemail = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=True, nullable=False)
    is_collector = db.Column(db.Boolean, default=False, nullable=False)
    is_house = db.Column(db.Boolean, default=False, nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)

    # Relationship with Routes
    routes = relationship('Routes', backref='company', lazy=True)

    def get_id(self):
        return str(self.admin_id)

class CollectorUser(db.Model, UserMixin):
    __tablename__ = 'collectoruser'
    collector_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    firstname = db.Column(db.String(150), nullable=False)
    secondname = db.Column(db.String(150), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('adminuser.admin_id', ondelete='CASCADE', onupdate='CASCADE', name='fk_company_id'), nullable=False)
    collectoremail = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_collector = db.Column(db.Boolean, default=True, nullable=False)
    is_house = db.Column(db.Boolean, default=False, nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)

    # Relationship with AdminUser (company)
    company = relationship('AdminUser', backref='collectors')

    # Relationship with RouteAssignment
    route_assignments = relationship('RouteAssignment', backref='collector', lazy=True)

    def get_id(self):
        return str(self.collector_id)
    
class Routes(db.Model):
    __tablename__ = 'routes'
    route_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.Integer, db.ForeignKey('adminuser.admin_id', ondelete='CASCADE', onupdate='CASCADE', name='fk_admin_profile_adminuser_adminid'), nullable=False)
    route_name = db.Column(db.String(255), unique=True, nullable=False)
    pickup_days = db.Column(db.String(255), nullable=False)
    frequency = db.Column(db.String(255), nullable=False)

    # Relationship with RouteAssignment
    assignments = relationship('RouteAssignment', backref='route', lazy=True)

class RouteAssignment(db.Model):
    __tablename__ = 'routeassignment'
    pair_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.Integer, db.ForeignKey('adminuser.admin_id', ondelete='CASCADE', onupdate='CASCADE', name='fk_admin_route_assignment'), nullable=False)
    collector_id = db.Column(db.Integer, db.ForeignKey('collectoruser.collector_id', ondelete='CASCADE', onupdate='CASCADE', name='fk_collector_route_pair_assignment'), nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.route_id', ondelete='CASCADE', onupdate='CASCADE', name='fk_route_id_assisgnment'), nullable=False)
