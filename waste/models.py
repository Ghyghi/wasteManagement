from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import relationship
from . import db

class HouseUser(db.Model, UserMixin):
    __tablename__ = 'houseuser'
    house_id = db.Column(db.String(100), primary_key=True)
    firstname = db.Column(db.String(150), nullable=False)
    secondname = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    houseemail = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_collector = db.Column(db.Boolean, default=False, nullable=False)
    is_house = db.Column(db.Boolean, default=True, nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)

    # Relationship with HouseClient
    house_clients = relationship('HouseClient', backref='house_user', lazy=True)

    def get_id(self):
        return str(self.house_id)

class AdminUser(db.Model, UserMixin):
    __tablename__ = 'adminuser'
    admin_id = db.Column(db.String(100), primary_key=True)
    companyname = db.Column(db.String(150), unique=True, nullable=False)
    adminemail = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=True, nullable=False)
    is_collector = db.Column(db.Boolean, default=False, nullable=False)
    is_house = db.Column(db.Boolean, default=False, nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)

    # Relationships with Routes, RouteAssignment, and HouseClient
    routes = relationship('Routes', backref='company', lazy=True)
    route_assignments = relationship('RouteAssignment', backref='admin_user', lazy=True)
    house_clients = relationship('HouseClient', backref='admin_user', lazy=True)

    def get_id(self):
        return str(self.admin_id)

class CollectorUser(db.Model, UserMixin):
    __tablename__ = 'collectoruser'
    collector_id = db.Column(db.String(100), primary_key=True)
    firstname = db.Column(db.String(150), nullable=False)
    secondname = db.Column(db.String(150), nullable=False)
    company_id = db.Column(db.String(100), db.ForeignKey('adminuser.admin_id', ondelete='CASCADE', onupdate='CASCADE', name='fk_company_id'), nullable=False)
    collectoremail = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_collector = db.Column(db.Boolean, default=True, nullable=False)
    is_house = db.Column(db.Boolean, default=False, nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)

    # Relationship with AdminUser (company), RouteAssignment 
    company = relationship('AdminUser', backref='collectors')
    route_assignments = relationship('RouteAssignment', backref='collector', lazy=True)

    def get_id(self):
        return str(self.collector_id)
    
class Routes(db.Model):
    __tablename__ = 'routes'
    route_id = db.Column(db.String(100), primary_key=True)
    company_id = db.Column(db.String(100), db.ForeignKey('adminuser.admin_id', ondelete='CASCADE', onupdate='CASCADE', name='fk_admin_profile_adminuser_adminid'), nullable=False)
    route_name = db.Column(db.String(255), unique=True, nullable=False)
    pickup_days = db.Column(db.String(255), nullable=False)
    frequency = db.Column(db.String(255), nullable=False)

    # Relationship with RouteAssignment,  and HouseClient
    assignments = relationship('RouteAssignment', backref='route', lazy=True)
    house_clients = relationship('HouseClient', backref='route', lazy=True)

class RouteAssignment(db.Model):
    __tablename__ = 'routeassignment'
    pair_id = db.Column(db.String(100), primary_key=True)
    company_id = db.Column(db.String(100), db.ForeignKey('adminuser.admin_id', ondelete='CASCADE', onupdate='CASCADE', name='fk_admin_route_assignment'), nullable=False)
    collector_id = db.Column(db.String(100), db.ForeignKey('collectoruser.collector_id', ondelete='CASCADE', onupdate='CASCADE', name='fk_collector_route_pair_assignment'), nullable=False)
    route_id = db.Column(db.String(100), db.ForeignKey('routes.route_id', ondelete='CASCADE', onupdate='CASCADE', name='fk_route_id_assisgnment'), nullable=False)

class HouseClient(db.Model):
    __tablename__='houseclient'
    client_id = db.Column(db.String(100), primary_key=True)
    house_id = db.Column(db.String(100), db.ForeignKey('houseuser.house_id', ondelete='CASCADE', onupdate='CASCADE', name='fk_house_client'), nullable=False)
    company_id = db.Column(db.String(100), db.ForeignKey('adminuser.admin_id', ondelete='CASCADE', onupdate='CASCADE', name='fk_house_client_admin'), nullable=False)
    route_id = db.Column(db.String(100), db.ForeignKey('routes.route_id', ondelete='CASCADE', onupdate='CASCADE', name='fk_route_id_client'), nullable=False)
