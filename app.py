"""
MiniVulnLab - a small, intentionally vulnerable Flask app for security training.

DO NOT deploy this anywhere reachable from the internet. Run it only on
localhost / an isolated lab network. Every vulnerability here is planted
on purpose and documented in README.md and docs/*.md.
"""

import sqlite3
import subprocess
from flask import Flask, request, render_template, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "lab-only-not-a-real-secret"
DB_PATH = "lab.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            bio TEXT
        );
        """
    )
    conn.execute("DELETE FROM users")
    conn.executemany(
        "INSERT INTO users (username, password, bio) VALUES (?, ?, ?)",
        [
            ("admin", "S3cureAdminPass!", "Site administrator. Full access."),
            ("alice", "alice123", "Marketing lead."),
            ("bob", "bobpassword", "Backend engineer."),
        ],
    )
    conn.commit()
    conn.close()


@app.route("/")
def index():
    return render_template("index.html")


# ---------------------------------------------------------------------------
# CHALLENGE 1: SQL injection login bypass
#
# The login query is built with raw string formatting instead of a
# parameterized query, so user input is concatenated directly into SQL.
# See docs/01-sqli-login-bypass.md for the exploit and the fix.
# ---------------------------------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        # VULNERABLE: raw string formatting into a SQL query.
        query = (
            f"SELECT * FROM users WHERE username = '{username}' "
            f"AND password = '{password}'"
        )
        conn = get_db()
        try:
            row = conn.execute(query).fetchone()
        except sqlite3.OperationalError:
            row = None
        conn.close()

        if row:
            session["user"] = row["username"]
            session["uid"] = row["id"]
            return redirect(url_for("profile", id=row["id"]))
        error = "Invalid credentials."
    return render_template("login.html", error=error)


# ---------------------------------------------------------------------------
# CHALLENGE 2: IDOR (Insecure Direct Object Reference)
#
# Any logged-in user can view any other user's profile by changing the
# `id` query parameter - there's no check that the requested id belongs
# to the logged-in session. See docs/02-idor-profile.md.
# ---------------------------------------------------------------------------
@app.route("/profile")
def profile():
    if "user" not in session:
        return redirect(url_for("login"))

    user_id = request.args.get("id", session.get("uid"))
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    if not row:
        return "No such user", 404
    return render_template("profile.html", profile=row, me=session["user"])


# ---------------------------------------------------------------------------
# CHALLENGE 3: OS command injection in a "network diagnostic" tool
#
# A classic pattern: a host field is passed straight into a shell command.
# See docs/03-command-injection-ping.md.
# ---------------------------------------------------------------------------
@app.route("/diagnostics", methods=["GET", "POST"])
def diagnostics():
    if "user" not in session:
        return redirect(url_for("login"))

    output = None
    if request.method == "POST":
        host = request.form.get("host", "")
        # VULNERABLE: shell=True with unsanitized user input.
        cmd = f"ping -c 1 {host}"
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=5
            )
            output = result.stdout + result.stderr
        except Exception as e:
            output = str(e)
    return render_template("diagnostics.html", output=output)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=True)
