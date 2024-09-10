from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from itsdangerous import URLSafeTimedSerializer
from dotenv import load_dotenv
import os

#Load environment variables
load_dotenv()
secret_key = os.getenv("SECRET_KEY")

#Initialize Flask extensions
db = SQLAlchemy()
migrate = Migrate()
s = URLSafeTimedSerializer(secret_key)

def create_app():
    app = Flask(__name__)
    app.config.from_object('waste.config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    from .models import HouseUser, AdminUser, CollectorUser
    from .routes import register_routes

    @login_manager.user_loader
    def load_user(user_id):
        # Attempt to find the user by user_id in AdminUser first
        adminuser = AdminUser.query.get(user_id)
        if adminuser:
            return adminuser

        # Attempt to find the user by house_id in HouseUser
        houseuser = HouseUser.query.get(user_id)
        if houseuser:
            return houseuser

        # Attempt to find the user by collector_id in CollectorUser
        collectoruser = CollectorUser.query.get(user_id)
        if collectoruser:
            return collectoruser

        # If no user found
        return None
    
    with app.app_context():
        db.create_all()

    register_routes(app)
    
    return app

def generate_confirmation_token(email):
    return s.dumps(email, salt='email-confirmation-salt')

def confirm_token(token, expiration=3600):
    try:
        email = s.loads(token, salt='email-confirmation-salt', max_age=expiration)
    except:
        return False
    return email

from waste.mailapi import send_email

def confirm_admin(user_email, user_name):
    token = generate_confirmation_token(user_email)
    confirm_url = url_for('confirm_email', token=token, _external=True)
    html = render_template('email/companyActivate.html', confirm_url=confirm_url, user_name=user_name)
    send_email(user_email, 'Please confirm your email', html)

def confirm_house(user_email, user_name):
    token = generate_confirmation_token(user_email)
    confirm_url = url_for('confirm_email_house', token=token, _external=True)
    html = render_template('email/houseActivate.html', confirm_url=confirm_url, user_name=user_name)
    send_email(user_email, 'Please confirm your email', html)

def confirmed_user(user_email, name):
    html = render_template('email/adminActivate.html', name=name)
    send_email(user_email, 'You are now a verified user.', html)