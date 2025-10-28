from flask import Flask, render_template, redirect, url_for, request, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

# =====================================
# App Configuration
# =====================================
app = Flask(__name__)
app.secret_key = "supersecretkey"  # change this later to something secure
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///career_site.db'
app.config['UPLOAD_FOLDER'] = 'uploads'  # Folder for CV and images
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # Max 5MB

# =====================================
# Initialize Database and Login Manager
# =====================================
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# =====================================
# User Model
# =====================================
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(50))
    qualification = db.Column(db.String(200))
    image = db.Column(db.String(200), default='default.png')
    cv_filename = db.Column(db.String(200))
    role = db.Column(db.String(50), default='user')  # user or admin
    saved_jobs = db.relationship('Job', secondary='saved_jobs', backref='saved_by_users')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# =====================================
# Job Model
# =====================================
class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    company = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    experience = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)
    posted_by = db.Column(db.Integer, db.ForeignKey('user.id'))  # link to admin user

# =====================================
# Saved Jobs Association Table
# =====================================
saved_jobs_table = db.Table('saved_jobs',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('job_id', db.Integer, db.ForeignKey('job.id'))
)

# =====================================
# User Loader
# =====================================
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# =====================================
# Routes
# =====================================
@app.route("/")
def home():
    jobs = Job.query.order_by(Job.id.desc()).all()
    return render_template("home.html", jobs=jobs)

@app.route("/about")
def about():
    return "<h1>About LinkJobs</h1><p>Connecting talent to opportunities across Africa.</p>"

# ---------- AUTH ----------
@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        password = request.form['password']
        admin_code = request.form.get('admin_code', '')

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "warning")
            return redirect(url_for('signup'))

        role = 'admin' if admin_code == "MY_SECRET_ADMIN_CODE" else 'user'
        new_user = User(fullname=fullname, email=email, role=role)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        # Automatically log in the user after signup
        login_user(new_user)
        flash(f"Account created successfully! Logged in as {role}.", "success")
        return redirect(url_for('profile'))

    return render_template("signup.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for('profile'))
        else:
            flash("Invalid email or password.", "danger")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))

# ---------- PROFILE ----------
@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.phone = request.form['phone']
        current_user.qualification = request.form['qualification']

        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '':
                image_filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
                current_user.image = image_filename

        if 'cv' in request.files:
            cv = request.files['cv']
            if cv.filename != '':
                cv_filename = secure_filename(cv.filename)
                cv.save(os.path.join(app.config['UPLOAD_FOLDER'], cv_filename))
                current_user.cv_filename = cv_filename

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('profile'))

    return render_template("profile.html", user=current_user)

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ---------- POST JOB ----------
@app.route("/post-job", methods=['GET', 'POST'])
@login_required
def post_job():
    if current_user.role != 'admin':
        flash("Only admins can post jobs.", "danger")
        return redirect(url_for('home'))

    if request.method == 'POST':
        title = request.form['title']
        company = request.form['company']
        location = request.form['location']
        type_ = request.form['type']
        experience = request.form.get('experience', 0)
        description = request.form['description']

        new_job = Job(
            title=title,
            company=company,
            location=location,
            type=type_,
            experience=int(experience),
            description=description,
            posted_by=current_user.id
        )

        db.session.add(new_job)
        db.session.commit()
        flash("Job posted successfully!", "success")
        return redirect(url_for('post_job'))

    return render_template("post-job.html")

# ---------- JOB DETAILS ----------
@app.route("/job-details/<int:job_id>")
def job_details(job_id):
    job = Job.query.get_or_404(job_id)
    return render_template("job-details.html", job=job)

# ---------- SAVE / UNSAVE JOB ----------
@app.route("/save-job/<int:job_id>")
@login_required
def save_job(job_id):
    job = Job.query.get_or_404(job_id)
    if job not in current_user.saved_jobs:
        current_user.saved_jobs.append(job)
        db.session.commit()
        flash("Job saved successfully!", "success")
    else:
        flash("Job already saved.", "info")
    return redirect(url_for('home'))

@app.route("/unsave-job/<int:job_id>")
@login_required
def unsave_job(job_id):
    job = Job.query.get_or_404(job_id)
    if job in current_user.saved_jobs:
        current_user.saved_jobs.remove(job)
        db.session.commit()
        flash("Job removed from saved jobs.", "success")
    return redirect(url_for('saved_jobs'))

# ---------- SAVED JOBS PAGE ----------
@app.route("/saved-jobs")
@login_required
def saved_jobs():
    return render_template("saved-jobs.html", jobs=current_user.saved_jobs)

# =====================================
# Run Server
# =====================================
if __name__ == "__main__":
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", debug=True)
