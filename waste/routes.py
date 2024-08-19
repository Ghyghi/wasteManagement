from flask import *
from waste.forms import *
from waste.models import *
from flask_login import login_required, current_user, login_user, logout_user
from waste import *
from sqlalchemy import or_, and_
from waste.mailapi import *

def flash_message(message, category):
    flash(message, category)

# APP routes
def register_routes(app):
    
    #Home Route
    @app.route('/')
    def home():
        return render_template('index.html')
    
    # Email Confirmation Route
    @app.route('/confirm/<token>')
    def confirm_email(token):
        try:
            email = confirm_token(token)
        except:
            flash_message('The confirmation link is invalid or has expired.', 'danger')
            return redirect(url_for('resend_confirmation'))

        admin_user = AdminUser.query.filter_by(email=email).first_or_404()
        house_user = HouseUser.query.filter_by(email=email).first_or_404()
        collector_user = CollectorUser.query.filter_by(email=email).first_or_404()
        users = [(admin_user), (house_user), (collector_user)]
        for user in users:
            if user.confirmed:
                flash_message('Account already confirmed. Please log in.', 'success')
            else:
                user.confirmed = True
                db.session.commit()
                flash_message('You have confirmed your account. Thanks!', 'success')
        return redirect(url_for('admin_login'))
    
    # Re-send Confirmation Route
    @app.route('/resend_confirmation', methods=['GET', 'POST'])
    def resend_confirmation():
        form = ResendConfirmationForm()
        if form.validate_on_submit():
            email = form.email.data
            admin_user = AdminUser.query.filter_by(email=email).first()
            house_user = HouseUser.query.filter_by(email=email).first()
            collector_user = CollectorUser.query.filter_by(email=email).first()
            users = [(admin_user), (house_user), (collector_user)]
            for user in users:
                if user and not user.confirmed:
                    send_confirmation_email(user.email)
                    flash_message('A new confirmation email has been sent.', 'success')
                else:
                    flash_message('Email not found or already confirmed.', 'danger')
        return render_template('resend_confirmation.html', form=form)
    
    #Forgot Password Route
    @app.route('/forgot_password', methods=['GET', 'POST'])
    def forgot_password():
        form = ForgotPasswordForm()

        if form.validate_on_submit():
            email = form.email.data
            password = form.password.data

            user = HouseUser.query.filter_by(email=email).first()
            if user:
                user.password = password
                db.session.commit()
                flash_message('Password updated successfully.', 'success')
                return redirect(url_for('login'))
        return render_template('forgot.html', form=form)
    ########### Admin APIs##################################################
    # Admin Register route
    @app.route('/admin/register', methods=['GET', 'POST'])
    def admin_register():
        form = AdminRegisterForm()
        if form.validate_on_submit():
            companyname = form.companyname.data
            password = form.password.data
            email = form.email.data
            role="Admin"
            
            #Check if the user exists

            existing_user = AdminUser.query.filter((AdminUser.companyname == companyname) | (AdminUser.email == email)).first()
            if existing_user:
                flash_message('Company name or email already in use', 'danger')
                return redirect(url_for('admin_register'))
            else:
                new_user = AdminUser(companyname = companyname, email = email, password = password, role=role, confirmed = False)
                db.session.add(new_user)
                db.session.commit()
                flash_message('A confirmaton email has been sent to you email. Please confirm before you proceed to login,', 'success')
                print(f'{companyname} registered with role {role}')
                return redirect(url_for('admin_login'))
        return render_template('admin/register.html', form=form)
    
    # Admin Login Route
    @app.route('/admin/login', methods=['GET', 'POST'])
    def admin_login():
        form = AdminLoginForm()
        if form.validate_on_submit():
            companyname = form.companyname.data
            password = form.password.data

            # Check if the user credentials are correct
            user = AdminUser.query.filter_by(companyname=companyname).first()
            if user and user.password == password:
                # Check if the user is confirmed
                if not user.confirmed:
                    flash_message('Please confirm your email before you try to login.', 'warning')
                    return redirect(url_for('resend_confirmation'))
                else:
                    login_user(user)
                    flash_message('Login success.', 'success')
                    print(f'{user.companyname} has been logged in, redirecting to the dashboard')
                    return redirect(url_for('admin_dashboard'))
            else:
                flash_message('Company name or password is incorrect. Please try again', 'warning')
                return redirect(url_for('admin_login'))
        return render_template('admin/login.html', form=form)
    
    # Admin Dashboard Route
    @app.route('/admin/dashboard')
    @login_required
    def admin_dashboard():
        return render_template('admin/dashboard.html')
    
    ########### House APIs##################################################
    # House register route
    @app.route('/house/register', methods=['GET', 'POST'])
    def register():
        form = HouseRegisterForm()

        if form.validate_on_submit():

            firstname = form.firstname.data
            secondname = form.secondname.data
            username = form.username.data
            email = form.email.data
            password = form.password.data
            role = 'Household'

            #Check if the user exists
            existing_user = HouseUser.query.filter((HouseUser.username == username) | (HouseUser.email == email)).first()

            if existing_user:
                flash_message('Username or email already in use. Try again', 'danger')
                return render_template('register.html', form=form)
            else:
                new_user= HouseUser(firstname=firstname, secondname=secondname, username=username, email=email, role=role, password=password, confirmed=False)
                db.session.add(new_user)
                db.session.commit()
                send_confirmation_email(new_user.email)
                flash_message('A confirmation email has been sent via email. Please confirm your email to log in.', 'success')
                return redirect(url_for('login'))
            
        return render_template('house/register.html', form=form)

    # House Login Route
    @app.route('/house/login', methods=['GET', 'POST'])
    def login():
        form = HouseLoginForm()

        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data

            # Check if user credentials are correct
            user = HouseUser.query.filter_by(username=username).first()
            if user and user.password == password:
                if not user.confirmed:
                    flash_message('Please confirm your email address first.', 'warning')
                    return redirect(url_for('resend_confirmation'))
                else:
                    login_user(user, remember=True)
                    flash_message('User logged in successfully!', 'success') 

                    print(f"User {user.username} logged in with role: {user.role}")

                    # Redirect based on user role
                    if user.role == 'Household':
                        print("Redirecting to house_dashboard")
                        return redirect(url_for('house_dashboard'))
                    elif user.role == 'Collector':
                        print("Redirecting to collector_dashboard")
                        return redirect(url_for('collector_dashboard'))
                    else:
                        flash_message('Invalid role. Please try again.', 'danger')
                        return redirect(url_for('login'))
            else:
                flash_message('Invalid username, role, or password. Please try again.', 'danger')
                return render_template('login.html', form=form)
        return render_template('house/login.html', form=form)
    
    # House Dashboard Route
    @app.route('/house/dashboard')
    @login_required
    def house_dashboard():
        return render_template('house/dashboard.html')

    ####### Collector APIs##################################################
    
    #Collector Dashboard
    @app.route('/collector/dashboard')
    @login_required
    def collector_dashboard():
        return render_template('collector/dashboard.html')


