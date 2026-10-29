import os
import secrets
from datetime import datetime, timedelta
from functools import wraps


import mysql.connector
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
from ml_recommender import rank_internships

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("INTERNHUB_SECRET_KEY", "change-this-secret-before-deployment")

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "internhub"),
}


def connect_db():
    return mysql.connector.connect(**DB_CONFIG)


def query_db(sql, values=(), one=False, commit=False):
    connection = connect_db()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(sql, values)
    result = cursor.fetchone() if one else cursor.fetchall()
    if commit:
        connection.commit()
        result = cursor.lastrowid
    cursor.close()
    connection.close()
    return result


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "error")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        user = query_db("SELECT is_admin FROM users WHERE id=%s", (session["user_id"],), one=True)
        if not user or not user["is_admin"]:
            abort(403)
        return view(*args, **kwargs)
    return wrapped


SECURITY_QUESTIONS = [
    "What is the nickname your friends call you?",
    "Which subject did you enjoy most in school?",
    "What is the name of your favourite childhood cartoon?",
]


def ensure_security_columns():
    """Add recovery-answer columns to older InternHub databases when needed."""
    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute("SHOW COLUMNS FROM users")
    existing = {row[0] for row in cursor.fetchall()}
    for column in ("security_answer_1", "security_answer_2", "security_answer_3"):
        if column not in existing:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {column} VARCHAR(255) NULL")
    connection.commit()
    cursor.close()
    connection.close()


def current_user():
    if "user_id" not in session:
        return None
    return query_db("SELECT id, name, email, education_status, study_year, field_of_interest, is_admin FROM users WHERE id=%s", (session["user_id"],), one=True)


@app.context_processor
def inject_user():
    return {"current_user": current_user()}


@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    total = query_db("SELECT COUNT(*) AS count FROM internships WHERE is_active=1", one=True)["count"]
    return render_template("index.html", total=total)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        education = request.form.get("education_status", "Currently studying")
        year = request.form.get("study_year", "") or None
        field = request.form.get("field_of_interest", "Any field")
        answers = [request.form.get(f"security_answer_{i}", "").strip().casefold() for i in range(1, 4)]
        if not name or not email or not password or not all(answers):
            flash("Please complete all required fields.", "error")
        elif password != confirm:
            flash("The passwords do not match.", "error")
        elif len(password) < 8:
            flash("Use a password with at least 8 characters.", "error")
        elif query_db("SELECT id FROM users WHERE email=%s", (email,), one=True):
            flash("An account with this email already exists. Please log in.", "error")
        else:
            ensure_security_columns()
            answer_hashes = [generate_password_hash(answer) for answer in answers]
            query_db("INSERT INTO users (name,email,password_hash,education_status,study_year,field_of_interest,security_answer_1,security_answer_2,security_answer_3) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                     (name, email, generate_password_hash(password), education, year, field, *answer_hashes), commit=True)
            user = query_db("SELECT id,name FROM users WHERE email=%s", (email,), one=True)
            session.clear()
            session["user_id"] = user["id"]
            session["name"] = user["name"]
            flash("Your account is ready.", "success")
            return redirect(url_for("dashboard"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = query_db("SELECT id,name,password_hash FROM users WHERE email=%s", (email,), one=True)
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["name"] = user["name"]
            return redirect(url_for("dashboard"))
        flash("Email or password is incorrect.", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have logged out.", "success")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]
    user = current_user()
    skills = query_db("SELECT skill FROM user_skills WHERE user_id=%s ORDER BY skill", (user_id,))
    saved_count = query_db("SELECT COUNT(*) AS count FROM saved_internships WHERE user_id=%s", (user_id,), one=True)["count"]
    application_count = query_db("SELECT COUNT(*) AS count FROM applications WHERE user_id=%s", (user_id,), one=True)["count"]
    internships = query_db("SELECT * FROM internships WHERE is_active=1 ORDER BY created_at DESC LIMIT 6")
    saved_ids = {row["internship_id"] for row in query_db("SELECT internship_id FROM saved_internships WHERE user_id=%s", (user_id,))}
    return render_template("dashboard.html", user=user, skills=[s["skill"] for s in skills], saved_count=saved_count,
                           application_count=application_count, internships=internships, saved_ids=saved_ids)


@app.route("/internships")
@login_required
def internships():
    search = request.args.get("q", "").strip()
    field = request.args.get("field", "")
    work_mode = request.args.get("work_mode", "")
    pay = request.args.get("pay", "")
    beginner = request.args.get("beginner", "")
    sql = "SELECT * FROM internships WHERE is_active=1"
    values = []
    if search:
        sql += " AND (title LIKE %s OR company LIKE %s OR skills LIKE %s OR description LIKE %s)"
        values += [f"%{search}%"] * 4
    if field:
        sql += " AND field=%s"; values.append(field)
    if work_mode:
        sql += " AND work_mode=%s"; values.append(work_mode)
    if pay:
        sql += " AND pay_type=%s"; values.append(pay)
    if beginner == "yes":
        sql += " AND beginner_friendly=1"
    sql += " ORDER BY created_at DESC"
    rows = query_db(sql, tuple(values))
    fields = query_db("SELECT DISTINCT field FROM internships WHERE is_active=1 ORDER BY field")
    saved_ids = {row["internship_id"] for row in query_db("SELECT internship_id FROM saved_internships WHERE user_id=%s", (session["user_id"],))}
    return render_template("internships.html", internships=rows, fields=fields, filters=request.args, saved_ids=saved_ids)


@app.route("/internship/<int:internship_id>")
@login_required
def internship_details(internship_id):
    internship = query_db("SELECT * FROM internships WHERE id=%s AND is_active=1", (internship_id,), one=True)
    if not internship:
        abort(404)
    user_id = session["user_id"]
    saved = query_db("SELECT id FROM saved_internships WHERE user_id=%s AND internship_id=%s", (user_id, internship_id), one=True)
    return render_template("internship_details.html", internship=internship, saved=bool(saved))


@app.route("/save/<int:internship_id>", methods=["POST"])
@login_required
def save_internship(internship_id):
    user_id = session["user_id"]
    action = request.form.get("action", "save")
    exists = query_db("SELECT id FROM saved_internships WHERE user_id=%s AND internship_id=%s", (user_id, internship_id), one=True)

    if action == "remove":
        if exists:
            query_db("DELETE FROM saved_internships WHERE id=%s", (exists["id"],), commit=True)
        flash("Internship removed from saved items.", "success")
    elif not exists:
        query_db("INSERT INTO saved_internships (user_id, internship_id) VALUES (%s,%s)", (user_id, internship_id), commit=True)
        flash("Internship saved.", "success")
    else:
        flash("This internship is already saved.", "success")

    return redirect(request.referrer or url_for("internships"))


@app.route("/saved")
@login_required
def saved():
    rows = query_db("SELECT i.* FROM internships i JOIN saved_internships s ON s.internship_id=i.id WHERE s.user_id=%s ORDER BY s.created_at DESC", (session["user_id"],))
    saved_ids = {row["id"] for row in rows}
    return render_template("saved.html", internships=rows, saved_ids=saved_ids)


@app.route("/skills", methods=["GET", "POST"])
@login_required
def skills():
    user_id = session["user_id"]
    if request.method == "POST":
        items = {item.strip() for item in request.form.get("skills", "").split(",") if item.strip()}
        query_db("DELETE FROM user_skills WHERE user_id=%s", (user_id,), commit=True)
        for item in sorted(items):
            query_db("INSERT INTO user_skills (user_id, skill) VALUES (%s,%s)", (user_id, item[:60]), commit=True)
        flash("Your skills have been updated.", "success")
        return redirect(url_for("recommendations"))
    current = query_db("SELECT skill FROM user_skills WHERE user_id=%s ORDER BY skill", (user_id,))
    suggested = ["Python", "Java", "HTML", "CSS", "JavaScript", "SQL", "Excel", "Communication", "Figma", "Data Analysis", "Marketing", "Writing"]
    return render_template("skills.html", skills=[x["skill"] for x in current], suggested=suggested)


def match_score(user_skills, internship):
    required = {x.strip().lower() for x in (internship.get("skills") or "").split(",") if x.strip()}
    if not required:
        return 25, []
    matched = required.intersection({x.lower() for x in user_skills})
    score = round(100 * len(matched) / len(required))
    return score, sorted(required - {x.lower() for x in user_skills})


@app.route("/recommendations")
@login_required
def recommendations():
    user_id = session["user_id"]
    skills = [x["skill"] for x in query_db("SELECT skill FROM user_skills WHERE user_id=%s", (user_id,))]
    user = current_user()
    rows = query_db("SELECT * FROM internships WHERE is_active=1 ORDER BY beginner_friendly DESC, created_at DESC")
    results = []
    ml_scores = rank_internships(skills, rows)
    for index, row in enumerate(rows):
        score, missing = match_score(skills, row)
        if not skills and not row["beginner_friendly"]:
            continue
        row["match_score"] = score
        row["ml_similarity"] = ml_scores[index]
        row["missing_skills"] = missing[:5]
        results.append(row)
    results.sort(key=lambda x: (x["ml_similarity"], x["match_score"], x["beginner_friendly"]), reverse=True)
    saved_ids = {row["internship_id"] for row in query_db("SELECT internship_id FROM saved_internships WHERE user_id=%s", (user_id,))}
    return render_template("recommendations.html", internships=results[:30], skills=skills, saved_ids=saved_ids)


@app.route("/compare", methods=["GET", "POST"])
@login_required
def compare():
    selected = request.form.getlist("internship_ids") if request.method == "POST" else request.args.getlist("id", type=int)
    selected = list(dict.fromkeys(int(x) for x in selected if str(x).isdigit()))[:3]
    rows = []
    if selected:
        marks = ",".join(["%s"] * len(selected))
        found = query_db(f"SELECT * FROM internships WHERE id IN ({marks}) AND is_active=1", tuple(selected))
        by_id = {row["id"]: row for row in found}
        rows = [by_id[item_id] for item_id in selected if item_id in by_id]
    available = query_db("SELECT id,title,company,field FROM internships WHERE is_active=1 ORDER BY company,title")
    return render_template("compare.html", selected=rows, available=available)


@app.route("/applications", methods=["GET", "POST"])
@login_required
def applications():
    user_id = session["user_id"]
    if request.method == "POST":
        internship_id = request.form.get("internship_id", type=int)
        status = request.form.get("status", "Applied")
        allowed = ["Interested", "Applied", "Assessment", "Interview", "Selected", "Rejected", "Withdrawn"]
        if internship_id and status in allowed:
            query_db("INSERT INTO applications (user_id, internship_id, status) VALUES (%s,%s,%s) ON DUPLICATE KEY UPDATE status=VALUES(status)",
                     (user_id, internship_id, status), commit=True)
            flash("Application tracker updated.", "success")
        return redirect(url_for("applications"))
    rows = query_db("SELECT a.id,a.status,a.updated_at,i.title,i.company,i.application_url,i.id AS internship_id FROM applications a JOIN internships i ON i.id=a.internship_id WHERE a.user_id=%s ORDER BY a.updated_at DESC", (user_id,))
    available = query_db("SELECT id,title,company,field FROM internships WHERE is_active=1 ORDER BY company,title")
    return render_template("applications.html", applications=rows, available=available)


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user_id = session["user_id"]
    if request.method == "POST":
        query_db("UPDATE users SET name=%s,education_status=%s,study_year=%s,field_of_interest=%s WHERE id=%s",
                 (request.form.get("name", "").strip(), request.form.get("education_status", "Currently studying"), request.form.get("study_year") or None,
                  request.form.get("field_of_interest", "Any field"), user_id), commit=True)
        session["name"] = request.form.get("name", "").strip()
        flash("Profile updated.", "success")
        return redirect(url_for("profile"))
    user = current_user()
    return render_template("profile.html", user=user)


@app.route("/admin", methods=["GET", "POST"])
@admin_required
def admin():
    if request.method == "POST":
        internship_id = request.form.get("internship_id", type=int)
        data = (request.form.get("title", "").strip(), request.form.get("company", "").strip(), request.form.get("field", "Other"),
                request.form.get("description", "").strip(), request.form.get("skills", "").strip(), request.form.get("eligibility", "Open to students"),
                request.form.get("pay_type", "Unspecified"), request.form.get("stipend", "Not specified"), request.form.get("work_mode", "Remote"),
                request.form.get("location", "Not specified"), request.form.get("duration", "Not specified"), request.form.get("application_url", "").strip(),
                request.form.get("deadline") or None, 1 if request.form.get("beginner_friendly") else 0)
        if not data[0] or not data[1] or not data[11].startswith(("https://", "http://")):
            flash("Enter a title, company, and valid application URL.", "error")
        elif internship_id:
            query_db("UPDATE internships SET title=%s,company=%s,field=%s,description=%s,skills=%s,eligibility=%s,pay_type=%s,stipend=%s,work_mode=%s,location=%s,duration=%s,application_url=%s,deadline=%s,beginner_friendly=%s WHERE id=%s", data + (internship_id,), commit=True)
            flash("Internship updated.", "success")
        else:
            query_db("INSERT INTO internships (title,company,field,description,skills,eligibility,pay_type,stipend,work_mode,location,duration,application_url,deadline,beginner_friendly) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", data, commit=True)
            flash("Internship added.", "success")
        return redirect(url_for("admin"))
    rows = query_db("SELECT * FROM internships ORDER BY created_at DESC")
    editing = query_db("SELECT * FROM internships WHERE id=%s", (request.args.get("edit", type=int),), one=True) if request.args.get("edit", type=int) else None
    return render_template("admin.html", internships=rows, editing=editing)


@app.route("/admin/delete/<int:internship_id>", methods=["POST"])
@admin_required
def delete_internship(internship_id):
    query_db("UPDATE internships SET is_active=0 WHERE id=%s", (internship_id,), commit=True)
    flash("Internship listing hidden.", "success")
    return redirect(url_for("admin"))


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    stage = "email"
    email = ""
    if request.method == "POST":
        action = request.form.get("action", "find_account")
        email = request.form.get("email", "").strip().lower()

        if action == "find_account":
            ensure_security_columns()
            user = query_db(
                "SELECT id FROM users WHERE email=%s AND security_answer_1 IS NOT NULL AND security_answer_2 IS NOT NULL AND security_answer_3 IS NOT NULL",
                (email,), one=True)
            if user:
                stage = "questions"
            else:
                flash("We couldn't find an account with saved security questions for that email.", "error")

        elif action == "verify_answers":
            ensure_security_columns()
            user = query_db("SELECT id,security_answer_1,security_answer_2,security_answer_3 FROM users WHERE email=%s", (email,), one=True)
            answers = [request.form.get(f"security_answer_{i}", "").strip().casefold() for i in range(1, 4)]
            if user and all(answers) and all(
                check_password_hash(user[f"security_answer_{i}"], answers[i - 1])
                for i in range(1, 4) if user[f"security_answer_{i}"]
            ) and all(user[f"security_answer_{i}"] for i in range(1, 4)):
                session["password_reset_user_id"] = user["id"]
                session["password_reset_verified"] = True
                stage = "reset"
            else:
                flash("The answers don't match. Please try again.", "error")
                stage = "questions" if user else "email"

        elif action == "reset_password":
            reset_user_id = session.get("password_reset_user_id")
            password = request.form.get("password", "")
            confirm = request.form.get("confirm_password", "")
            if not session.get("password_reset_verified") or not reset_user_id:
                session.pop("password_reset_user_id", None)
                session.pop("password_reset_verified", None)
                flash("Please verify your security answers first.", "error")
            elif len(password) < 8:
                flash("Use a password with at least 8 characters.", "error")
                stage = "reset"
            elif password != confirm:
                flash("The passwords do not match.", "error")
                stage = "reset"
            else:
                query_db("UPDATE users SET password_hash=%s WHERE id=%s", (generate_password_hash(password), reset_user_id), commit=True)
                session.pop("password_reset_user_id", None)
                session.pop("password_reset_verified", None)
                flash("Your password has been reset. Please log in.", "success")
                return redirect(url_for("login"))

    return render_template("forgot_password.html", stage=stage, email=email, questions=SECURITY_QUESTIONS)


@app.errorhandler(403)
def forbidden(error):
    return render_template("message.html", title="Access denied", message="This page is only available to an administrator."), 403


@app.errorhandler(404)
def not_found(error):
    return render_template("message.html", title="Page not found", message="The page or internship could not be found."), 404


if __name__ == "__main__":
    app.run(debug=True)
