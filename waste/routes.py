from flask import *
from waste.forms import *
from waste.models import *
from flask_login import login_required, current_user, login_user, logout_user
from waste import *
from sqlalchemy import or_, and_
from waste.mailapi import *
from functools import wraps
import random
import string

def generate_random_admin(length=8):
    # Define the characters to use for generating the ID
    characters = string.ascii_letters + string.digits
    # Generate a random ID with the specified length
    random_id = ''.join(random.choices(characters, k=length))
    return random_id

def generate_random_collector(length=7):
    # Define the characters to use for generating the ID
    characters = string.ascii_letters + string.digits
    # Generate a random ID with the specified length
    random_id = ''.join(random.choices(characters, k=length))
    return random_id

def generate_random_house(length=9):
    # Define the characters to use for generating the ID
    characters = string.ascii_letters + string.digits
    # Generate a random ID with the specified length
    random_id = ''.join(random.choices(characters, k=length))
    return random_id

def generate_random_other(length=6):
    # Define the characters to use for generating the ID
    characters = string.ascii_letters + string.digits
    # Generate a random ID with the specified length
    random_id = ''.join(random.choices(characters, k=length))
    return random_id

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
    
    #Re-send Confirmation Email
    @app.route('/resend_confirmation', methods=['GET', 'POST'])
    def resend_confirmation():
        form = ResendConfirmationForm()
        if form.validate_on_submit():
            email = form.email.data
            admin_user = AdminUser.query.filter(adminemail=email).first()
            house_user = HouseUser.query.filter(houseemail=email).first()
            users = [admin_user, house_user]
            
            for user in users:
                if user and not user.confirmed:
                    if isinstance(user, AdminUser):
                        confirm_admin(user.adminemail)
                    elif isinstance(user, HouseUser):
                        confirm_house(user.houseemail)
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
            admin_id= generate_random_admin()
            
            #Check if the user exists

            existing_user = AdminUser.query.filter((AdminUser.companyname == companyname) | (AdminUser.adminemail == email)).first()
            if existing_user:
                flash_message('Company name or email already in use', 'danger')
                return redirect(url_for('admin_register'))
            else:
                new_user = AdminUser(admin_id = admin_id, companyname = companyname, adminemail = email, password = password, confirmed = False)
                db.session.add(new_user)
                db.session.commit()
                flash_message('A confirmaton email has been sent to you email. Please confirm before you proceed to login,', 'success')
                confirm_admin(email)
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
    
    # Email Confirmation Route
    @app.route('/admin/confirm/<token>')
    def confirm_email(token):
        try:
            email = confirm_token(token)
        except:
            flash_message('The confirmation link is invalid or has expired.', 'danger')
            return redirect(url_for('resend_confirmation'))

        user = AdminUser.query.filter(AdminUser.adminemail==email).first_or_404()
        if user.confirmed:
            flash_message('Account already confirmed. Please log in.', 'success')
        else:
            user.confirmed = True
            db.session.commit()
            flash_message('You have confirmed your account. Thanks!', 'success')
        return redirect(url_for('admin_login'))

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
    
    #Delete admin profile
    @app.route('/admin/profile/delete/<string:admin_id>', methods=['GET'])
    @login_required
    def delete_profile_admin(admin_id):
        admin = AdminUser.query.get(admin_id)
        if admin:
            # Delete all RouteAssignments associated with the admin
            RouteAssignment.query.filter_by(company_id=admin.admin_id).delete()

            # Delete all Routes associated with the admin
            Routes.query.filter_by(company_id=admin.admin_id).delete()

            # Delete all Collectors associated with the admin
            CollectorUser.query.filter_by(company_id=admin.admin_id).delete()

            # Delete the admin user
            db.session.delete(admin)
            db.session.commit()
            
            flash_message('Admin profile deleted successfully!', 'success')
            return redirect(url_for('home'))
        
        flash_message('Admin not found.', 'danger')
        return redirect(url_for('admin_dashboard'))

    #Update admin prifile
    @app.route('/admin/profile/update', methods=['GET', 'POST'])
    @login_required
    def update_profile_admin():
        admin_id=current_user.get_id()
        admin=AdminUser.query.get(admin_id)
        form=AdminRegisterForm(obj=admin)
        if form.validate_on_submit():
            admin.companyname=form.companyname.data
            admin.adminemail=form.email.data
            admin.password=form.password.data

            try:
                db.session.commit()
                flash_message('Profile updated successfully.', 'success')
            except Exception as e:
                db.session.rollback()
                flash_message(f'Error updating profile: {e}', 'danger')

            return redirect(url_for('admin_dashboard'))
        return render_template('/admin/updateProfile.html', form=form)
    
    # Register a route
    @app.route('/route/register', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def route_register():
        form = RoutesForm()
        if form.validate_on_submit():
        
            company_id = current_user.get_id()
            pickup_days = form.days.data
            district = form.district.data
            sector = form.sector.data
            frequency = form.frequency.data
            route_id = generate_random_other()

            route_name = f"{sector},{district}"

            print(f"Comany: {company_id} days: {pickup_days} route: {route_name} frequency: {frequency}")

            #Check whether the route exists
            existing_route = Routes.query.filter(Routes.route_name == route_name).first()

            if existing_route:
                flash_message('Route already exists', 'warning')
                return redirect(url_for('route_register'))
            else:
                new_route = Routes(route_id = route_id, company_id=company_id, pickup_days=pickup_days, route_name=route_name, frequency=frequency)
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
        assigned = db.session.query(RouteAssignment, Routes).join(
        Routes, RouteAssignment.route_id == Routes.route_id
    ).filter(RouteAssignment.company_id == admin_id).all()
        return render_template('/admin/viewRoutes.html', routes=routes, assigned=assigned)
    
    #View pair details
    @app.route('/pair/view', methods=['GET'])
    @login_required
    @admin_required
    def pair_details():
        admin_id = current_user.get_id()
        pair = RouteAssignment.query.filter(RouteAssignment.company_id==admin_id).all()
        return render_template('/admin/pairDetails.html', pair=pair)
    
    #View route details
    @app.route('/route/view/<string:route_id>', methods=['GET','POST'])
    @login_required
    def route_details(route_id):
        route = Routes.query.get_or_404(route_id)
        #Get the assigned collector
        collector= RouteAssignment.query.filter(route_id==RouteAssignment.route_id).first()
        return render_template('/admin/routeDetails.html', route=route, collector=collector)
    
    #Delete route
    @app.route('/route/delete/<string:route_id>', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def delete_route(route_id):
        route = Routes.query.get(route_id)
        
        if not route:
            flash_message('Route not found.', 'danger')
            return redirect(url_for('admin_dashboard'))

        # Check if there are any assignments linked to this route
        if route.assignments:
            flash_message('Cannot delete route. It has associated assignments.', 'danger')
            return redirect(url_for('admin_dashboard'))

        try:
            db.session.delete(route)
            db.session.commit()
            flash_message('Route deleted successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash_message(f'An error occurred: {e}', 'danger')
        
        return redirect(url_for('admin_dashboard'))
    
    #Delete route pair
    @app.route('/pair/delete/<string:pair_id>', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def delete_pair(pair_id):
        pair = RouteAssignment.query.get(pair_id)
        
        if not pair:
            flash_message('Pair not found.', 'danger')
            return redirect(url_for('admin_dashboard'))
        try:
            db.session.delete(pair)
            db.session.commit()
            flash_message('Pair deleted successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash_message(f'An error occurred: {e}', 'danger')
        
        return redirect(url_for('admin_dashboard'))

    #Update route
    @app.route('/route/update/<string:route_id>', methods=['GET','POST'])
    @login_required
    @admin_required
    def update_route(route_id):
        route = Routes.query.filter_by(route_id=route_id).first()

        if not route:
            flash_message('Route not found.', 'danger')
            return redirect(url_for('admin_dashboard'))
        
        form = UpdateRouteForm(obj=route)

        if form.validate_on_submit():
            route.pickup_days = form.pickup_days.data
            route.frequency = form.frequency.data

            try:
                db.session.commit()
                flash_message('Route updated successfully.', 'success')
            except Exception as e:
                db.session.rollback()
                flash_message(f'Error updating route: {e}', 'danger')

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
    @app.route('/admin/confirm_user/<string:user_id>', methods=['POST'])
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
    
    #Assign the route to a collector
    @app.route('/admin/assign', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def assign_collector():
        form = AssignmentForm()
        if form.validate_on_submit():
            company_id = current_user.get_id()
            collector = form.collector.data
            route = form.route.data
            pair_id = generate_random_other()

            #Check if the pair exists
            pair = RouteAssignment.query.filter((RouteAssignment.route_id == route)).first()
            if pair:
                flash_message('The route has already been assigned', 'danger')
                print('The route has already been assigned')
                return redirect(url_for('assign_collector'))
            else:
                new_pair = RouteAssignment(pair_id = pair_id, collector_id=collector, company_id=company_id, route_id=route)
                db.session.add(new_pair)
                db.session.commit()
                flash_message('The route has been assigned', 'success')
                print('The route has been assigned')
                return redirect(url_for('view_route'))
        return render_template('/admin/assignCollector.html', form=form)
    
    #Create a schedule
    @app.route('/admin/schedule/create', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def create_schedule():
        form=ScheduleForm()
        if form.validate_on_submit():
            collector_id=form.collector_id.data
            route_id=form.route_id.data
            company_id = current_user.get_id()
            house_clients = HouseClient.query.filter(HouseClient.company_id==company_id).all()
            schedule_id = generate_random_other()

            #Check schedule availability
            existing_schedule=Schedule.query.filter(Schedule.route_id==route_id).first()
            if existing_schedule:
                flash_message('Route already has a corresponding schedule.', 'danger')
                return redirect(url_for('admin_dashboard'))
            else:

                for house in house_clients:
                    new_schedule=Schedule(schedule_id = schedule_id, company_id=company_id, collector_id=collector_id, route_id=route_id, house_id=house.house_id)
                    db.session.add(new_schedule)
                    flash_message('Schedule created.', 'success')
                db.session.commit()
                return redirect(url_for('admin_dashboard'))
        return render_template('/admin/createSchedule.html', form=form)
    
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
            house_id = generate_random_house()

            #Check if the user exists
            existing_user = HouseUser.query.filter((HouseUser.username == username) | (HouseUser.houseemail == houseemail)).first()

            if existing_user:
                flash_message('Username or email already in use. Try again', 'danger')
                return render_template('house/register.html', form=form)
            else:
                new_user= HouseUser(house_id = house_id, firstname=firstname, secondname=secondname, username=username, houseemail=houseemail, password=password, confirmed=False)
                db.session.add(new_user)
                db.session.commit()
                confirm_house(new_user.houseemail)
                flash_message('A confirmation email has been sent via email. Please confirm your email to log in.', 'success')
                return redirect(url_for('login'))
            
        return render_template('house/register.html', form=form)

    # Email Confirmation Route
    @app.route('/house/confirm/<token>')
    def confirm_email_house(token):
        try:
            email = confirm_token(token)
        except:
            flash_message('The confirmation link is invalid or has expired.', 'danger')
            return redirect(url_for('resend_confirmation'))

        user = HouseUser.query.filter(HouseUser.houseemail==email).first_or_404()
        if user.confirmed:
            flash_message('Account already confirmed. Please log in.', 'success')
        else:
            user.confirmed = True
            db.session.commit()
            flash_message('You have confirmed your account. Thanks!', 'success')
        return redirect(url_for('login'))

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
    
    #Join a company
    @app.route('/house/join/<string:route_id>', methods=['GET'])
    @login_required
    def join_route(route_id):
        house_id=current_user.get_id()
        route=route_id
        company=Routes.query.filter(Routes.route_id==route).first()
        company_id=company.company_id
        client_id = generate_random_other()

        existing_client=HouseClient.query.filter_by(house_id=house_id).first()
        if existing_client:
            flash_message('You are already part of this company.', 'danger')
            return redirect(url_for('house_dashboard'))
        else:
            new_client=HouseClient(client_id = client_id, house_id=house_id, company_id=company_id, route_id=route)
            db.session.add(new_client)
            db.session.commit()
            flash_message('You have been registered to this route.', 'success')
        return redirect(url_for('view_provider'))
    
    #View the company you belong to
    @app.route('/house/my-provider', methods=['GET'])
    @login_required
    def view_provider():
        house_id=current_user.get_id()
        regcomp = HouseClient.query.filter(HouseClient.house_id==house_id).first()
        if regcomp:
            regcompany= HouseClient.query.filter_by(house_id=house_id).first()

            return render_template('house/myProvider.html', regcompany=regcompany)
        else:
            flash_message('You are not registered to any company, first register to one.', 'danger')
            company= AdminUser.query.all()
            routes= Routes.query.all()
            return render_template('house/seeCompanies.html', company=company, routes=routes)

    ####### Collector APIs##################################################
    
    #Collector Dashboard
    @app.route('/collector/dashboard')
    @login_required
    def collector_dashboard():
        collector_id=current_user.get_id()
        company = Schedule.query.filter_by(collector_id=collector_id).first()
        schedule=Schedule.query.filter_by(collector_id=collector_id).count()
        houses=HouseClient.query.filter_by(company_id=company.company_id).count()
        return render_template('collector/dashboard.html', schedule=schedule, houses=houses)
    
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
                    flash_message("Please wait for your admin to verify you.", 'warning')
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
            collector_id = generate_random_collector()

            #Check if the user already exits
            existing_user = CollectorUser.query.filter(CollectorUser.collectoremail==collectoremail, CollectorUser.company_id==company_id).first()

            if existing_user:
                flash_message('User already exists. Try again', 'danger')
                return redirect(url_for('collector_register'))
            else:
                new_user = CollectorUser(collector_id = collector_id, firstname=firstname, secondname=secondname, company_id=company_id, password=password, collectoremail=collectoremail)
                db.session.add(new_user)
                db.session.commit()
                flash_message('Registration successful.', 'success')
                flash_message('Please wait for admin to verify you.', 'warning')
                return redirect(url_for('home'))
        return render_template('/collector/register.html', form=form)
    
    #View assigned routes
    @app.route('/collector/routes', methods=['GET'])
    def collector_routes():
        collector_id = current_user.get_id()
        routess = RouteAssignment.query.filter(RouteAssignment.collector_id==collector_id).all()
        company = Routes.query.filter(Routes.company_id == CollectorUser.company_id).first()
        return render_template('/collector/myRoutes.html', routess=routess, company=company)
    
    #Collector profile
    @app.route('/collector/profile', methods=['GET'])
    def collector_profile():
        collector_id = current_user.get_id()
        collector = CollectorUser.query.filter(CollectorUser.collector_id==collector_id).first()
        company = AdminUser.query.filter(AdminUser.admin_id==collector.company_id).first()
        route_count = RouteAssignment.query.filter(RouteAssignment.collector_id==collector_id).count()
        return render_template('/collector/profile.html', collector=collector, company=company, route_count=route_count)
    
    #Collector profile update
    @app.route('/collector/profile/update', methods=['GET', 'POST'])
    def update_profile_collector():
        collector_id = current_user.get_id()
        collector = CollectorUser.query.filter(CollectorUser.collector_id==collector_id).first()
        form=CollectorProfileForm(obj=collector)

        if form.validate_on_submit():
            collector.collectoremail=form.collectoremail.data
            collector.password=form.password.data
            try:
                db.session.commit()
                flash_message('Profile updated successfully.', 'success')
                return redirect(url_for('collector_profile'))
            except Exception as e:
                db.session.rollback()
                flash_message(f'Error updating profile: {e}', 'danger')
            return redirect(url_for('collector_profile'))
        return render_template('/collector/update_profile.html', form=form)
    
    #Collector profile delete
    @app.route('/collector/profile/delete/<string:collector_id>', methods=['GET'])
    @login_required
    def delete_profile_collector(collector_id):
        collector = CollectorUser.query.get(collector_id)
        if collector:
            # Delete all RouteAssignments associated with the collector
            RouteAssignment.query.filter_by(collector_id=collector.collector_id).delete()
            
            # Delete the collector
            db.session.delete(collector)
            db.session.commit()
            
            flash_message('Collector profile deleted successfully!', 'success')
            return redirect(url_for('home'))
        
        flash_message('Collector not found.', 'danger')
        return redirect(url_for('collector_dashboard'))
