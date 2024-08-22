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
            flash('The confirmation link is invalid or has expired.', 'danger')
            return redirect(url_for('resend_confirmation'))

        # Check for the user in all user types
        admin_user = AdminUser.query.filter_by(adminemail=email).first()
        house_user = HouseUser.query.filter_by(houseemail=email).first()
        collector_user = CollectorUser.query.filter_by(collectoremail=email).first()
        users = [admin_user, house_user, collector_user]

        for user in users:
            if user:  # Check if user exists
                if user.confirmed:
                    flash('Account already confirmed. Please log in.', 'success')
                else:
                    user.confirmed = True
                    db.session.commit()
                    flash('You have confirmed your account. Thanks!', 'success')
                    if user == 'admin_user':
                        return redirect(url_for('admin_login'))
                    elif user=='house_user':
                        return redirect(url_for('login'))
                    else:
                        return redirect(url_for('collector_login'))
        
        flash('No account found for this email.', 'danger')
        return redirect(url_for('resend_confirmation'))
    
    # Re-send Confirmation Route
    @app.route('/resend_confirmation', methods=['GET', 'POST'])
    def resend_confirmation():
        form = ResendConfirmationForm()
        if form.validate_on_submit():
            email = form.email.data
            admin_user = AdminUser.query.filter_by(adminemail=email).first()
            house_user = HouseUser.query.filter_by(houseemail=email).first()
            collector_user = CollectorUser.query.filter_by(collectoremail=email).first()
            users = {'admin_user': admin_user, 'house_user': house_user, 'collector_user': collector_user}
            
            for role, user in users.items():
                if user and not user.confirmed:
                    if role == 'admin_user':
                        send_confirmation_email(user.adminemail)
                    elif role == 'house_user':
                        send_confirmation_email(user.houseemail)
                    else:
                        send_confirmation_email(user.collectoremail)
                    
                    flash('A new confirmation email has been sent.', 'success')
                    break
            else:
                flash('Email not found or already confirmed.', 'danger')
        
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

            existing_user = AdminUser.query.filter((AdminUser.companyname == companyname) | (AdminUser.adminemail == email)).first()
            if existing_user:
                flash_message('Company name or email already in use', 'danger')
                return redirect(url_for('admin_register'))
            else:
                new_user = AdminUser(companyname = companyname, adminemail = email, password = password, role=role, confirmed = False)
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

        # Get the admin_id of the currently logged-in admin
        admin_id = current_user.get_id()

        #Get the company routes and profile
        routes = Routes.query.filter_by(company_id=admin_id).all()
        company = AdminUser.query.filter_by(admin_id=admin_id).first()
        return render_template('admin/dashboard.html', routes=routes, company=company)
    
    # Register a route
    @app.route('/route/register', methods=['GET', 'POST'])
    @login_required
    def route_register():
        form = RoutesForm()
        if form.validate_on_submit():
        
            company_id = form.company.data
            pickup_days = form.days.data
            district = form.district.data
            sector = form.sector.data
            frequency = form.frequency.data

            route_name = f"{sector},{district}"

            print(f"Comany: {company_id} days: {pickup_days} route: {route_name} frequency {frequency}")

            #Check whether the route exists
            existing_route = Routes.query.filter(Routes.route_name == route_name).first()

            if existing_route:
                flash_message('Route already exists', 'warning')
                return redirect(url_for('route_register'))
            else:
                new_route = Routes(company_id=company_id, pickup_days=pickup_days, route_name=route_name, frequency=frequency)
                db.session.add(new_route)
                db.session.commit()
                flash_message('Route registered successfully,', 'success')
                print(f'{route_name} registered with to {company_id}')
                return redirect(url_for('admin_dashboard'))
        return render_template('admin/routes.html', form=form)
    ########### House APIs##################################################
    
    # House register route
    @app.route('/house/register', methods=['GET', 'POST'])
    def register():
        form = HouseRegisterForm()

        if form.validate_on_submit():

            firstname = form.firstname.data
            secondname = form.secondname.data
            username = form.username.data
            houseemail = form.email.data
            password = form.password.data
            role = 'Household'

            #Check if the user exists
            existing_user = HouseUser.query.filter((HouseUser.username == username) | (HouseUser.houseemail == houseemail)).first()

            if existing_user:
                flash_message('Username or email already in use. Try again', 'danger')
                return render_template('house/register.html', form=form)
            else:
                new_user= HouseUser(firstname=firstname, secondname=secondname, username=username, houseemail=houseemail, role=role, password=password, confirmed=False)
                db.session.add(new_user)
                db.session.commit()
                send_confirmation_email(new_user.houseemail)
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
                return render_template('house/login.html', form=form)
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
    
    #Collector Login
    @app.route('/collector/login')
    def collector_login():
        return "Collector Login"


