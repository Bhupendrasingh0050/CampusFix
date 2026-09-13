from flask import (
    Flask, render_template, request, redirect,url_for, session, flash, abort,
)

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from datetime import datetime
import os
import re

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv is optional; environment variables can also be set
    # directly on the system if it isn't installed.
    pass


# ============================================================
# APP CONFIGURATION
# ============================================================

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "campusfix-secret-key-change-this"
)

DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_NAME = os.environ.get("DB_NAME", "campus_fix")

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Upload configuration
app.config["UPLOAD_FOLDER"] = os.path.join("static", "uploads")
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB

#adding Sesson out after clicking logout
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("SESSION_COOKIE_SECURE", "0") == "1"

@app.after_request
def add_security_and_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0, private"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

ALLOWED_CATEGORIES = [
    "Internet/Wi-Fi",
    "Electricity",
    "Water",
    "Classroom",
    "Laboratory",
    "Furniture",
    "Cleanliness",
    "Other",
]

ALLOWED_PRIORITIES = ["Low", "Medium", "High", "Critical"]
ALLOWED_STATUSES = ["Pending", "In Progress", "Resolved", "Rejected"]

DEFAULT_ADMIN_EMAIL = "admin@campusfix.local"
DEFAULT_ADMIN_PASSWORD = "Admin@123"

db = SQLAlchemy(app)


# ============================================================
# DATABASE MODELS
# ============================================================

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    student_id = db.Column(db.String(30), unique=True, nullable=True)
    branch = db.Column(db.String(50), nullable=False)
    year = db.Column(db.String(20), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="student")
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    @property
    def initials(self):
        parts = self.full_name.split()
        letters = "".join(p[0] for p in parts[:2] if p)
        return letters.upper() or "U"


class Department(db.Model):
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class Complaint(db.Model):
    __tablename__ = "complaints"

    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.String(30), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    department_id = db.Column(
        db.Integer, db.ForeignKey("departments.id"), nullable=True
    )
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    room_number = db.Column(db.String(30), nullable=True)
    priority = db.Column(db.String(20), nullable=False, default="Medium")
    status = db.Column(db.String(30), nullable=False, default="Pending")
    image_path = db.Column(db.String(255), nullable=True)
    contact_pref = db.Column(db.String(30), nullable=False, default="Email")
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime, server_default=db.func.now(), onupdate=db.func.now()
    )

    user = db.relationship("User", backref=db.backref("complaints", lazy=True))
    department = db.relationship(
        "Department", backref=db.backref("complaints", lazy=True)
    )


class ComplaintUpdate(db.Model):
    __tablename__ = "complaint_updates"

    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(
        db.Integer, db.ForeignKey("complaints.id"), nullable=False
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(30), nullable=False)
    comment = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    complaint = db.relationship(
        "Complaint",
        backref=db.backref("updates", lazy=True, cascade="all, delete-orphan"),
    )
    user = db.relationship("User", backref=db.backref("complaint_updates", lazy=True))


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    complaint_id = db.Column(
        db.Integer, db.ForeignKey("complaints.id"), nullable=True
    )
    message = db.Column(db.String(500), nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship("User", backref=db.backref("notifications", lazy=True))
    complaint = db.relationship(
        "Complaint", backref=db.backref("notifications", lazy=True)
    )


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def is_valid_email(email):
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email) is not None


def generate_complaint_id():
    last_complaint = Complaint.query.order_by(Complaint.id.desc()).first()
    number = (last_complaint.id + 1050) if last_complaint else 1050
    return f"CF-{number}"


def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return db.session.get(User, user_id)


def student_required():
    """Any logged-in user (student or admin) may access."""
    return get_current_user()


def status_data_slug(status):
    """lowercase-dash slug used by the client-side filter JS."""
    return status.lower().replace(" ", "-")


def status_badge_class(status):
    """CSS badge suffix used in style.css (badge-pending / badge-progress / ...)."""
    mapping = {
        "pending": "pending",
        "in progress": "progress",
        "resolved": "resolved",
        "rejected": "rejected",
    }
    return mapping.get(status.lower(), status.lower().replace(" ", "-"))


def priority_badge_class(priority):
    return priority.lower()


# Make helpers available inside every Jinja template
app.jinja_env.globals.update(
    status_data_slug=status_data_slug,
    status_badge_class=status_badge_class,
    priority_badge_class=priority_badge_class,
)


@app.context_processor
def inject_globals():
    """Every template can use `current_user` and `unread_count` directly."""
    user = get_current_user()
    unread_count = 0
    if user:
        unread_count = Notification.query.filter_by(
            user_id=user.id, is_read=False
        ).count()
    return dict(current_user=user, unread_count=unread_count)


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():
    total_complaints = Complaint.query.count()
    resolved_complaints = Complaint.query.filter_by(status="Resolved").count()
    resolution_rate = (
        round((resolved_complaints / total_complaints) * 100)
        if total_complaints
        else 0
    )
    locations = db.session.query(Complaint.location).distinct().count()

    return render_template(
        "index.html",
        total_complaints=total_complaints,
        resolved_complaints=resolved_complaints,
        resolution_rate=resolution_rate,
        locations=locations,
    )


# ============================================================
# REGISTER
# ============================================================

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        student_id = request.form.get("student_id", "").strip()
        branch = request.form.get("branch", "").strip()
        year = request.form.get("year", "").strip()

        # Validation
        if not full_name or not email or not password or not branch or not year:
            flash("Please fill all required fields.", "error")
            return redirect(url_for("register"))

        if not is_valid_email(email):
            flash("Please enter a valid email address.", "error")
            return redirect(url_for("register"))

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "error")
            return redirect(url_for("register"))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered.", "error")
            return redirect(url_for("register"))

        if student_id:
            existing_student = User.query.filter_by(student_id=student_id).first()
            if existing_student:
                flash("Student ID already registered.", "error")
                return redirect(url_for("register"))

        user = User(
            full_name=full_name,
            email=email,
            password_hash=generate_password_hash(password),
            student_id=student_id if student_id else None,
            branch=branch,
            year=year,
            role="student",
        )

        db.session.add(user)
        db.session.commit()

        flash("Registration successful. Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


# ============================================================
# LOGIN
# ============================================================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            session["role"] = user.role

            flash(f"Welcome back, {user.full_name.split(' ')[0]}!", "success")

            if user.role == "admin":
                return redirect(url_for("admin_dashboard"))
            return redirect(url_for("student_dashboard"))

        flash("Invalid email or password.", "error")

    return render_template("login.html")


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))


# ============================================================
# STUDENT DASHBOARD
# ============================================================

@app.route("/student-dashboard")
def student_dashboard():
    user = student_required()
    if not user:
        return redirect(url_for("login"))

    complaints = (
        Complaint.query.filter_by(user_id=user.id)
        .order_by(Complaint.created_at.desc())
        .all()
    )

    total = len(complaints)
    pending = sum(1 for c in complaints if c.status == "Pending")
    in_progress = sum(1 for c in complaints if c.status == "In Progress")
    resolved = sum(1 for c in complaints if c.status == "Resolved")

    return render_template(
        "student-dashboard.html",
        user=user,
        complaints=complaints,
        recent_complaints=complaints[:4],
        total=total,
        pending=pending,
        in_progress=in_progress,
        resolved=resolved,
    )


# ============================================================
# REPORT COMPLAINT
# ============================================================

@app.route("/report", methods=["GET", "POST"])
def report():
    user = student_required()
    if not user:
        return redirect(url_for("login"))

    departments = Department.query.order_by(Department.name).all()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()
        location = request.form.get("location", "").strip()
        room_number = request.form.get("room_number", "").strip()
        priority = request.form.get("priority", "Medium").strip().title()
        contact_pref = request.form.get("contact_pref", "Email").strip().title()
        department_id = request.form.get("department_id")

        if not title or not description or not category or not location:
            flash("Please fill all required fields.", "error")
            return redirect(url_for("report"))

        if priority not in ALLOWED_PRIORITIES:
            priority = "Medium"

        # Image upload
        image_path = None
        file = request.files.get("image")

        if file and file.filename:
            if not allowed_file(file.filename):
                flash(
                    "Invalid image format. Only PNG, JPG, JPEG or WEBP allowed.",
                    "error",
                )
                return redirect(url_for("report"))

            filename = secure_filename(file.filename)
            unique_filename = (
                f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            )

            os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], unique_filename))
            image_path = "uploads/" + unique_filename

        complaint = Complaint(
            complaint_id=generate_complaint_id(),
            user_id=user.id,
            department_id=int(department_id) if department_id else None,
            title=title,
            description=description,
            category=category,
            location=location,
            room_number=room_number or None,
            priority=priority,
            status="Pending",
            image_path=image_path,
            contact_pref=contact_pref,
        )

        db.session.add(complaint)
        db.session.flush()  # get complaint.id before commit

        db.session.add(
            ComplaintUpdate(
                complaint_id=complaint.id,
                user_id=user.id,
                status="Pending",
                comment="Complaint submitted successfully.",
            )
        )

        db.session.add(
            Notification(
                user_id=user.id,
                complaint_id=complaint.id,
                message=f"Your complaint {complaint.complaint_id} has been submitted.",
            )
        )

        db.session.commit()

        flash(f"Complaint {complaint.complaint_id} submitted successfully.", "success")
        return redirect(url_for("complaint_details", complaint_id=complaint.id))

    return render_template("report-problem.html", user=user, departments=departments)


# ============================================================
# MY COMPLAINTS
# ============================================================

@app.route("/my-complaints")
def my_complaints():
    user = student_required()
    if not user:
        return redirect(url_for("login"))

    complaints = (
        Complaint.query.filter_by(user_id=user.id)
        .order_by(Complaint.created_at.desc())
        .all()
    )

    return render_template("my-complaints.html", user=user, complaints=complaints)


# ============================================================
# COMPLAINT DETAILS
# ============================================================

@app.route("/complaint/<int:complaint_id>")
def complaint_details(complaint_id):
    user = student_required()
    if not user:
        return redirect(url_for("login"))

    complaint = db.session.get(Complaint, complaint_id)

    if not complaint:
        flash("Complaint not found.", "error")
        return redirect(url_for("my_complaints"))

    if user.role != "admin" and complaint.user_id != user.id:
        flash("You are not allowed to view this complaint.", "error")
        return redirect(url_for("my_complaints"))

    updates = (
        ComplaintUpdate.query.filter_by(complaint_id=complaint.id)
        .order_by(ComplaintUpdate.created_at.asc())
        .all()
    )

    return render_template(
        "complaint-details.html", user=user, complaint=complaint, updates=updates
    )


# ============================================================
# PROFILE
# ============================================================

@app.route("/profile", methods=["GET", "POST"])
def profile():
    user = student_required()
    if not user:
        return redirect(url_for("login"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        branch = request.form.get("branch", "").strip()
        year = request.form.get("year", "").strip()

        if not full_name:
            flash("Full name cannot be empty.", "error")
            return redirect(url_for("profile"))

        user.full_name = full_name
        if branch:
            user.branch = branch
        if year:
            user.year = year

        db.session.commit()

        flash("Profile updated successfully.", "success")
        return redirect(url_for("profile"))

    return render_template("profile.html", user=user)


# ============================================================
# NOTIFICATIONS
# ============================================================

@app.route("/notifications")
def notifications():
    user = student_required()
    if not user:
        return redirect(url_for("login"))

    notification_list = (
        Notification.query.filter_by(user_id=user.id)
        .order_by(Notification.created_at.desc())
        .all()
    )

    return render_template(
        "notifications.html", user=user, notifications=notification_list
    )


@app.route("/notification/<int:notification_id>/read", methods=["POST"])
def mark_notification_read(notification_id):
    user = student_required()
    if not user:
        return redirect(url_for("login"))

    notification = db.session.get(Notification, notification_id)

    if notification and notification.user_id == user.id:
        notification.is_read = True
        db.session.commit()

    return redirect(request.referrer or url_for("notifications"))


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@app.route("/admin-dashboard")
def admin_dashboard():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))
    if user.role != "admin":
        flash("Admin access required.", "error")
        return redirect(url_for("student_dashboard"))

    complaints = Complaint.query.order_by(Complaint.created_at.desc()).all()

    total = len(complaints)
    pending = sum(1 for c in complaints if c.status == "Pending")
    in_progress = sum(1 for c in complaints if c.status == "In Progress")
    resolved = sum(1 for c in complaints if c.status == "Resolved")
    rejected = sum(1 for c in complaints if c.status == "Rejected")
    high_priority = sum(1 for c in complaints if c.priority in ("High", "Critical"))

    # Simple breakdowns for the dashboard charts (no external library used)
    def percentage_breakdown(items, key):
        counts = {}
        for item in items:
            value = getattr(item, key)
            counts[value] = counts.get(value, 0) + 1
        breakdown = []
        for value, count in sorted(counts.items(), key=lambda x: -x[1]):
            pct = round((count / total) * 100) if total else 0
            breakdown.append({"label": value, "count": count, "pct": pct})
        return breakdown

    by_category = percentage_breakdown(complaints, "category")
    by_location = percentage_breakdown(complaints, "location")

    priority_rank = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    priority_issues = sorted(
        [c for c in complaints if c.priority in ("Critical", "High")],
        key=lambda c: priority_rank.get(c.priority, 9),
    )[:5]

    return render_template(
        "admin-dashboard.html",
        user=user,
        complaints=complaints,
        total=total,
        pending=pending,
        in_progress=in_progress,
        resolved=resolved,
        rejected=rejected,
        high_priority=high_priority,
        by_category=by_category,
        by_location=by_location,
        priority_issues=priority_issues,
    )


# ============================================================
# ADMIN COMPLAINTS
# ============================================================

@app.route("/admin-complaints")
def admin_complaints():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))
    if user.role != "admin":
        return redirect(url_for("student_dashboard"))

    status_filter = request.args.get("status")
    priority_filter = request.args.get("priority")

    query = Complaint.query

    if status_filter:
        status_lookup = status_filter.replace("-", " ").title()
        query = query.filter(Complaint.status == status_lookup)

    if priority_filter:
        query = query.filter(Complaint.priority == priority_filter.title())

    complaints = query.order_by(Complaint.created_at.desc()).all()
    departments = Department.query.order_by(Department.name).all()

    return render_template(
        "admin-complaints.html",
        user=user,
        complaints=complaints,
        departments=departments,
    )


# ============================================================
# ADMIN COMPLAINT DETAILS
# ============================================================

@app.route("/admin-complaint/<int:complaint_id>")
def admin_complaint_details(complaint_id):
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))
    if user.role != "admin":
        return redirect(url_for("student_dashboard"))

    complaint = db.session.get(Complaint, complaint_id)

    if not complaint:
        flash("Complaint not found.", "error")
        return redirect(url_for("admin_complaints"))

    updates = (
        ComplaintUpdate.query.filter_by(complaint_id=complaint.id)
        .order_by(ComplaintUpdate.created_at.asc())
        .all()
    )

    departments = Department.query.order_by(Department.name).all()

    return render_template(
        "admin-complaint-details.html",
        user=user,
        complaint=complaint,
        updates=updates,
        departments=departments,
    )


# ============================================================
# ADMIN UPDATE COMPLAINT
# ============================================================

@app.route("/admin-complaint/<int:complaint_id>/update", methods=["POST"])
def update_complaint(complaint_id):
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))
    if user.role != "admin":
        flash("Admin access required.", "error")
        return redirect(url_for("student_dashboard"))

    complaint = db.session.get(Complaint, complaint_id)

    if not complaint:
        flash("Complaint not found.", "error")
        return redirect(url_for("admin_complaints"))

    new_status = request.form.get("status", complaint.status)
    new_priority = request.form.get("priority", complaint.priority)
    department_id = request.form.get("department_id")
    comment = request.form.get("comment", "").strip()

    if new_status not in ALLOWED_STATUSES:
        new_status = complaint.status
    if new_priority not in ALLOWED_PRIORITIES:
        new_priority = complaint.priority

    new_department_id = int(department_id) if department_id else None

    status_changed = new_status != complaint.status
    department_changed = new_department_id != complaint.department_id

    complaint.status = new_status
    complaint.priority = new_priority
    complaint.department_id = new_department_id
    complaint.updated_at = datetime.utcnow()

    # Only log a timeline entry when something actually changed
    if status_changed or department_changed or comment:
        if comment:
            update_comment = comment
        elif status_changed:
            update_comment = f"Complaint status changed to {new_status}."
        else:
            new_dept = db.session.get(Department, new_department_id) if new_department_id else None
            update_comment = (
                f"Complaint assigned to {new_dept.name}."
                if new_dept
                else "Complaint department unassigned."
            )

        db.session.add(
            ComplaintUpdate(
                complaint_id=complaint.id,
                user_id=user.id,
                status=new_status,
                comment=update_comment,
            )
        )

        db.session.add(
            Notification(
                user_id=complaint.user_id,
                complaint_id=complaint.id,
                message=(
                    f"Complaint {complaint.complaint_id} status updated to {new_status}."
                    if status_changed
                    else f"New update on complaint {complaint.complaint_id}."
                ),
            )
        )
    else:
        flash("No changes were made to the complaint.", "info")

    db.session.commit()

    flash("Complaint updated successfully.", "success")
    return redirect(url_for("admin_complaint_details", complaint_id=complaint.id))


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(413)
def file_too_large(error):
    flash("File is too large. Maximum upload size is 5 MB.", "error")
    return redirect(request.referrer or url_for("home")), 413


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template("errors/500.html"), 500


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def initialize_database():
    db.create_all()

    departments = [
        ("IT Support", "Computer, Wi-Fi, software and technical problems."),
        ("Electrical Maintenance", "Lights, fans, switches and electrical problems."),
        ("Plumbing & Water", "Water supply, taps, washrooms and plumbing problems."),
        ("Housekeeping", "Cleanliness and sanitation related problems."),
        ("Classroom Maintenance", "Desks, boards, doors, windows and classroom problems."),
        ("Laboratory Maintenance", "Laboratory equipment and infrastructure problems."),
    ]

    for name, description in departments:
        existing = Department.query.filter_by(name=name).first()
        if not existing:
            db.session.add(Department(name=name, description=description))

    db.session.commit()

    # Create a default admin account (development only)
    existing_admin = User.query.filter_by(email=DEFAULT_ADMIN_EMAIL).first()
    if not existing_admin:
        admin = User(
            full_name="Campus Admin",
            email=DEFAULT_ADMIN_EMAIL,
            password_hash=generate_password_hash(DEFAULT_ADMIN_PASSWORD),
            student_id=None,
            branch="Administration",
            year="N/A",
            role="admin",
        )
        db.session.add(admin)
        db.session.commit()
        print(
            "Created default admin account -> "
            f"email: {DEFAULT_ADMIN_EMAIL} / password: {DEFAULT_ADMIN_PASSWORD} "
            "(DEVELOPMENT ONLY — change this before production)"
        )


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    with app.app_context():
        initialize_database()

    app.run(debug=True)
