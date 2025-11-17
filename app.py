from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, Enquiry, Admin
from config import Config
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
# Add session configuration
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
app.config['SESSION_TYPE'] = 'filesystem'
db.init_app(app)

# Initialize database and create admin
with app.app_context():
    db.create_all()
    # Create admin user if not exists
    if not Admin.query.filter_by(username='admin').first():
        admin = Admin(username='sr38238', password='Santhu@8632')
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created: admin / admin123")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        try:
            enquiry = Enquiry(
                name=request.form['name'],
                college=request.form['college'],
                email=request.form['email'],
                contact_no=request.form['contact_no'],
                domain=request.form['domain'],
                project_description=request.form['project_description']
            )
            db.session.add(enquiry)
            db.session.commit()
            flash('✅ Your enquiry has been submitted successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('❌ Error submitting enquiry. Please try again.', 'error')
        return redirect(url_for('contact'))
    
    return render_template('contact.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        admin = Admin.query.filter_by(username=username, password=password).first()
        if admin:
            session['admin_logged_in'] = True
            session['admin_username'] = username
            session.permanent = True  # Make session permanent
            flash('✅ Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('❌ Invalid username or password!', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        flash('🔒 Please login to access admin panel', 'error')
        return redirect(url_for('admin_login'))
    
    enquiries = Enquiry.query.order_by(Enquiry.created_at.desc()).all()
    return render_template('admin_dashboard.html', enquiries=enquiries)

@app.route('/admin/delete_enquiry/<int:enquiry_id>')
def delete_enquiry(enquiry_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    enquiry = Enquiry.query.get_or_404(enquiry_id)
    db.session.delete(enquiry)
    db.session.commit()
    flash('✅ Enquiry deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    flash('🔒 Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/debug')
def debug():
    admin_exists = Admin.query.filter_by(username='admin').first() is not None
    total_enquiries = Enquiry.query.count()
    
    return f"""
    <h1>Debug Information</h1>
    <p>Admin exists: {admin_exists}</p>
    <p>Total enquiries: {total_enquiries}</p>
    <p>Logged in: {session.get('admin_logged_in', False)}</p>
    <p>Username: {session.get('admin_username', 'None')}</p>
    <p><a href="/admin/login">Go to Admin Login</a></p>
    <p><a href="/admin/dashboard">Go to Admin Dashboard</a></p>
    <p><a href="/">Go to Home</a></p>
    """

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
