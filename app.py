from flask import Flask, render_template

app = Flask(__name__)

# Home
@app.route("/")
def home():
    return render_template("home.html")

# Post a Job
@app.route("/post-job")
def post_job():
    return render_template("post-job.html")

# Job Details
@app.route("/job-details")
def job_details():
    return render_template("job-details.html")

# Profile
@app.route("/profile")
def profile():
    return render_template("profile.html")

# Saved Jobs
@app.route("/saved-jobs")
def saved_jobs():
    return render_template("saved-jobs.html")

# Login
@app.route("/login")
def login():
    return render_template("login.html")

# Signup
@app.route("/signup")
def signup():
    return render_template("signup.html")

# About
@app.route("/about")
def about():
    return "<h1>About LinkJobs</h1><p>Connecting talent to opportunities across Africa.</p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
