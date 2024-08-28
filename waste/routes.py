from flask import *
from waste.forms import *
from waste.models import *
from flask_login import login_required, current_user, login_user, logout_user
from waste import *
from sqlalchemy import or_, and_
from waste.mailapi import *
from functools import wraps

def flash_message(message, category):
    flash(message, category)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        elif not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            if current_user.is_house:
                return redirect(url_for('house_dashboard'))
            elif current_user.is_collector:
                return redirect(url_for('collector_dashboard'))
            else:
                return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

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

        # Check for the user in all user types
        admin_user = AdminUser.query.filter_by(adminemail=email).first()
        house_user = HouseUser.query.filter_by(houseemail=email).first()
        users = [admin_user, house_user]

        for user in users:
            if user:  # Check if user exists
                if user.confirmed:
                    flash_message('Account already confirmed. Please log in.', 'success')
                else:
                    user.confirmed = True
                db.session.commit()
                flash_message('You have confirmed your account. Thanks!', 'success')
                if isinstance(user, AdminUser):
                    return redirect(url_for('admin_login'))
                elif isinstance(user, HouseUser):
                    return redirect(url_for('login'))
                else:
                    flash_message('Invalid account type', 'danger')
        flash_message('No account found for this email.', 'danger')
        return redirect(url_for('resend_confirmation'))
    
    #Re-send Confirmation Email
    @app.route('/resend_confirmation', methods=['GET', 'POST'])
    def resend_confirmation():
        form = ResendConfirmationForm()
        if form.validate_on_submit():
            email = form.email.data
            admin_user = AdminUser.query.filter_by(adminemail=email).first()
            house_user = HouseUser.query.filter_by(houseemail=email).first()
            users = [admin_user, house_user]
            
            for user in users:
                if user and not user.confirmed:
                    if isinstance(user, AdminUser):
                        send_confirmation_email(user.adminemail)
                    elif isinstance(user, HouseUser):
                        send_confirmation_email(user.houseemail)
                    else:
                        flash_message('Invalid account type', 'danger')
                    
                    flash_message('A new confirmation email has been sent.', 'success')
                    break
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
    
    #Logout Route
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash_message('Logged out successfully!', 'success')
        return redirect(url_for('home'))
    
    ########### Admin APIs##################################################
    # Admin Register route
    @app.route('/admin/register', methods=['GET', 'POST'])
    def admin_register():
        form = AdminRegisterForm()
        if form.validate_on_submit():
            companyname = form.companyname.data
            password = form.password.data
            email = form.email.data
            
            #Check if the user exists

            existing_user = AdminUser.query.filter((AdminUser.companyname == companyname) | (AdminUser.adminemail == email)).first()
            if existing_user:
                flash_message('Company name or email already in use', 'danger')
                return redirect(url_for('admin_register'))
            else:
                new_user = AdminUser(companyname = companyname, adminemail = email, password = password, confirmed = False)
                db.session.add(new_user)
                db.session.commit()
                flash_message('A confirmaton email has been sent to you email. Please confirm before you proceed to login,', 'success')
                send_confirmation_email(email)
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
    @admin_required
    def admin_dashboard():

        # Get the admin_id of the currently logged-in admin
        admin_id = current_user.get_id()

        #Get the company routes and profile
        routes = Routes.query.filter_by(company_id=admin_id).limit(5).all()
        company = AdminUser.query.filter_by(admin_id=admin_id).first()
        return render_template('admin/dashboard.html', routes=routes, company=company)
    
    # Register a route
    @app.route('/route/register', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def route_register():
        form = RoutesForm()
        if form.validate_on_submit():
        
            company_id = form.company.data
            pickup_days = form.days.data
            district = form.district.data
            sector = form.sector.data
            frequency = form.frequency.data

            route_name = f"{sector},{district}"

            print(f"Comany: {company_id} days: {pickup_days} route: {route_name} frequency: {frequency}")

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
    
    # View Routes
    @app.route('/route/view')
    @login_required
    def view_route():
        # Get the admin_id of the currently logged-in admin
        admin_id = current_user.get_id()
        #Get the company routes and profile
        routes = Routes.query.filter_by(company_id=admin_id).all()
        return render_template('/admin/viewRoutes.html', routes=routes)
    
    #View route details
    @app.route('/route/view/<int:route_id>', methods=['GET','POST'])
    @login_required
    def route_details(route_id):
        route = Routes.query.get_or_404(route_id)
        return render_template('/admin/routeDetails.html', route=route)
    
    #Delete route
    @app.route('/route/delete/<int:route_id>', methods=['GET','POST'])
    @login_required
    @admin_required
    def delete_route(route_id):
        route = Routes.query.get_or_404(route_id)
        db.session.delete(route)
        db.session.commit()
        flash_message('Route deleted successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    #Update route
    @app.route('/route/update/<int:route_id>', methods=['GET','POST'])
    @login_required
    @admin_required
    def update_route(route_id):
        route = Routes.query.filter_by(route_id=route_id).first()

        if not route:
            flash('Route not found.', 'danger')
            return redirect(url_for('admin_dashboard'))
        
        form = UpdateRouteForm(obj=route)

        if form.validate_on_submit():
            route.pickup_days = form.pickup_days.data
            route.frequency = form.frequency.data

            try:
                db.session.commit()
                flash('Route updated successfully.', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating route: {e}', 'danger')

            return redirect(url_for('admin_dashboard'))
        return render_template('/admin/updateRoute.html', form=form, route=route)
    
    #See company collectors
    @app.route('/admin/collectors', methods=['GET'])
    @login_required
    @admin_required
    def company_collectors():
        company_id = current_user.admin_id

        users = CollectorUser.query.filter_by(confirmed=False, company_id=company_id).all()
        confirmed_users = CollectorUser.query.filter_by(confirmed=True, company_id=company_id).all()
        return render_template('/admin/collectors.html', users=users, confirmed_users=confirmed_users)
    
    #Confirm collector users
    @app.route('/admin/confirm_user/<int:user_id>', methods=['POST'])
    @login_required
    @admin_required
    def confirm_user(user_id):
        user = CollectorUser.query.get_or_404(user_id)
        user.confirmed = True
        db.session.commit()
        confirmed_user(user.collectoremail)
        flash_message('User confirmed successfully.', 'success')
        return redirect(url_for('company_collectors'))
    
    #View Company Profile
    @app.route('/admin/profile', methods=['GET'])
    @login_required
    @admin_required
    def admin_profile():
        company_id = current_user.admin_id
        company = AdminUser.query.filter_by(admin_id=current_user.admin_id).first()
        collector_count = CollectorUser.query.filter_by(company_id=company_id).count()
        routes = Routes.query.filter_by(company_id=current_user.admin_id).count()

        return render_template('/admin/profile.html', company=company, collector_count=collector_count, routes=routes)

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

            #Check if the user exists
            existing_user = HouseUser.query.filter((HouseUser.username == username) | (HouseUser.houseemail == houseemail)).first()

            if existing_user:
                flash_message('Username or email already in use. Try again', 'danger')
                return render_template('house/register.html', form=form)
            else:
                new_user= HouseUser(firstname=firstname, secondname=secondname, username=username, houseemail=houseemail, password=password, confirmed=False)
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
                    print("Redirecting to house_dashboard")
                    return redirect(url_for('house_dashboard'))

            else:
                flash_message('Invalid username, or password. Please try again.', 'danger')
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
    @app.route('/collector/login', methods=['GET', 'POST'])
    def collector_login():
        form=CollectorLoginForm()

        if form.validate_on_submit():
            collectoremail = form.collectoremail.data
            password = form.password.data

            user = CollectorUser.query.filter_by(collectoremail=collectoremail).first()

            if user and user.password==password:
                if not user.confirmed:
                    flash_message("Please wait for your admin to verify you.", 'Warning')
                    return redirect(url_for('home'))
                else:
                    login_user(user)
                    flash_message('Login Successful.', 'success')
                    return redirect(url_for('collector_dashboard'))
            else:
                flash_message('The credentials entered are not accurate.', 'danger')
                return redirect(url_for('collector_login'))
        return render_template('/collector/login.html', form=form)
    
    #Collector Register
    @app.route('/collector/register', methods=['GET', 'POST'])
    def collector_register():
        form=CollectorRegisterForm()

        if form.validate_on_submit():
            firstname=form.firstname.data
            secondname=form.secondname.data
            company_id=form.company_id.data
            password=form.password.data
            collectoremail=form.collectoremail.data

            #Check if the user already exits
            existing_user = CollectorUser.query.filter(CollectorUser.collectoremail==collectoremail, CollectorUser.company_id==company_id).first()

            if existing_user:
                flash_message('User already exists. Try again', 'danger')
                return redirect(url_for('collector_register'))
            else:
                new_user = CollectorUser(firstname=firstname, secondname=secondname, company_id=company_id, password=password, collectoremail=collectoremail)
                db.session.add(new_user)
                db.session.commit()
                flash_message('Registration successful.', 'success')
                flash_message('Please wait for admin to verify you.', 'warning')
                return redirect(url_for('home'))
        return render_template('/collector/register.html', form=form)


    @app.route('/test_roles')
    @login_required
    def test_roles():
        return f"Admin: {current_user.is_admin}, Collector: {current_user.is_collector}, House: {current_user.is_house}"

