from flask import Blueprint, render_template, redirect, request, flash, url_for
from flask_login import login_user, logout_user, current_user
from models.models import db, User
from werkzeug.security import check_password_hash, generate_password_hash
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if current_user.is_authenticated:
        return redirect(url_for('home'))  # CHANGED: match.match_page → home
    
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            
            if not username:
                flash('❌ Username is required', 'error')
                return render_template('login.html')
            
            if not password:
                flash('❌ Password is required', 'error')
                return render_template('login.html')
            
            logger.info(f"🔐 Login attempt for user: {username}")
            
            try:
                # TRY TO QUERY USER
                user = User.query.filter_by(username=username).first()
                
                if not user:
                    logger.warning(f"⚠️ Login failed: User '{username}' not found")
                    flash('❌ Invalid username or password', 'error')
                    return render_template('login.html')
                
                # CHECK PASSWORD
                if not user.check_password(password):
                    logger.warning(f"⚠️ Login failed: Wrong password for user '{username}'")
                    flash('❌ Invalid username or password', 'error')
                    return render_template('login.html')
                
                # CHECK IF ACTIVE
                if not user.is_active:
                    logger.warning(f"⚠️ Login blocked: Account inactive for user '{username}'")
                    flash('❌ Your account has been disabled', 'error')
                    return render_template('login.html')
                
                # LOGIN SUCCESSFUL
                login_user(user, remember=True)
                user.last_seen = __import__('datetime').datetime.utcnow()
                db.session.commit()
                
                logger.info(f"✅ Login successful for user: {username}")
                flash(f'✅ Welcome back, {user.full_name or user.username}!', 'success')
                
                next_page = request.args.get('next')
                if next_page and next_page.startswith('/'):
                    return redirect(next_page)
                return redirect(url_for('home'))  # FIXED: Removed the '/' from url_for()
            
            except Exception as e:
                # ROLLBACK ON ANY DATABASE ERROR
                db.session.rollback()
                logger.error(f"❌ Database error during login: {str(e)}", exc_info=True)
                flash(f'❌ Database error: {str(e)}', 'error')
                return render_template('login.html')
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Login error: {str(e)}", exc_info=True)
            flash(f'❌ An error occurred: {str(e)}', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration"""
    if current_user.is_authenticated:
        return redirect(url_for('home'))  # CHANGED: match.match_page → home
    
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            full_name = request.form.get('full_name', '').strip()
            mobile = request.form.get('mobile', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            logger.info(f"📝 Registration attempt for user: {username}")
            
            # VALIDATION
            if not all([username, full_name, mobile, email, password, confirm_password]):
                flash('❌ All fields are required', 'error')
                return render_template('register.html')

            # Name validation (Characters only)
            import re
            if not re.match(r"^[A-Za-z\s]+$", full_name):
                flash('❌ Full Name should only contain letters and spaces', 'error')
                return render_template('register.html')
            
            # Mobile validation (10 digits)
            if not re.match(r"^\d{10}$", mobile):
                flash('❌ Mobile Number must be exactly 10 digits', 'error')
                return render_template('register.html')
            
            if len(username) < 3:
                flash('❌ Username must be at least 3 characters', 'error')
                return render_template('register.html')
            
            if password != confirm_password:
                flash('❌ Passwords do not match', 'error')
                return render_template('register.html')
            
            if len(password) < 6:
                flash('❌ Password must be at least 6 characters', 'error')
                return render_template('register.html')
            
            try:
                # CHECK DATABASE
                existing_user = User.query.filter_by(username=username).first()
                if existing_user:
                    logger.warning(f"⚠️ Registration failed: Username '{username}' exists")
                    flash('❌ Username already taken', 'error')
                    return render_template('register.html')
                
                existing_email = User.query.filter_by(email=email).first()
                if existing_email:
                    logger.warning(f"⚠️ Registration failed: Email '{email}' exists")
                    flash('❌ Email already registered', 'error')
                    return render_template('register.html')
                
                # CREATE USER
                user = User(username=username, full_name=full_name, mobile=mobile, email=email, is_active=True)
                user.set_password(password)
                
                db.session.add(user)
                db.session.commit()
                
                logger.info(f"✅ Registration successful for user: {username}")
                flash('✅ Account created successfully! Please log in.', 'success')
                return redirect(url_for('auth.login'))
            
            except Exception as e:
                db.session.rollback()
                logger.error(f"❌ Database error during registration: {str(e)}", exc_info=True)
                flash(f'❌ Database error: {str(e)}', 'error')
                return render_template('register.html')
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Registration error: {str(e)}", exc_info=True)
            flash(f'❌ An error occurred: {str(e)}', 'error')
            return render_template('register.html')
    
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    """Handle user logout"""
    try:
        username = current_user.username if current_user.is_authenticated else 'Unknown'
        logout_user()
        logger.info(f"✅ Logout successful for user: {username}")
        flash('✅ You have been logged out', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Logout error: {str(e)}", exc_info=True)
        flash('❌ An error occurred during logout', 'error')
    
    return redirect(url_for('auth.login'))