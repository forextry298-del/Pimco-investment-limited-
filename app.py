from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3, os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("PIMCO_SECRET_KEY", "change-this-local-demo-secret")
DB = os.path.join(os.path.dirname(__file__), "pimco.db")

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
            phone TEXT UNIQUE NOT NULL, password TEXT NOT NULL,
            invite_code TEXT DEFAULT '', age INTEGER, disease TEXT,
            medical_done INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        con.execute("""CREATE TABLE IF NOT EXISTS transactions(
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            kind TEXT NOT NULL, amount INTEGER NOT NULL, channel TEXT,
            status TEXT DEFAULT 'Demo pending', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

@app.before_request
def setup():
    init_db()

def current_user():
    if "user_id" not in session:
        return None
    with db() as con:
        return con.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()

@app.route("/")
def index():
    user = current_user()
    if user:
        return redirect(url_for("home"))
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
    name = request.form.get("name","").strip()
    phone = request.form.get("phone","").strip()
    password = request.form.get("password","")
    invite = request.form.get("invite_code","").strip()
    if not name or not phone or len(password) < 6:
        flash("Enter your name, phone number and a password of at least 6 characters.")
        return redirect(url_for("index"))
    try:
        with db() as con:
            cur = con.execute("INSERT INTO users(name,phone,password,invite_code) VALUES(?,?,?,?)",
                (name, phone, generate_password_hash(password), invite))
            uid = cur.lastrowid
        session["user_id"] = uid
        return render_template("registered.html", name=name)
    except sqlite3.IntegrityError:
        flash("That phone number is already registered. Please log in.")
        return redirect(url_for("index"))

@app.route("/login", methods=["POST"])
def login():
    phone = request.form.get("phone","").strip()
    password = request.form.get("password","")
    with db() as con:
        user = con.execute("SELECT * FROM users WHERE phone=?", (phone,)).fetchone()
    if not user or not check_password_hash(user["password"], password):
        flash("Phone number or password is incorrect.")
        return redirect(url_for("index"))
    session["user_id"] = user["id"]
    return redirect(url_for("home"))

@app.route("/home")
def home():
    user = current_user()
    if not user: return redirect(url_for("index"))
    with db() as con:
        tx = con.execute("SELECT * FROM transactions WHERE user_id=? ORDER BY id DESC LIMIT 5", (user["id"],)).fetchall()
    return render_template("home.html", user=user, transactions=tx)

@app.route("/medical", methods=["GET","POST"])
def medical():
    user = current_user()
    if not user: return redirect(url_for("index"))
    if request.method == "POST":
        age = request.form.get("age","").strip()
        disease = request.form.get("disease","").strip()
        if not age.isdigit() or not 1 <= int(age) <= 120 or not disease:
            flash("Please enter a valid age and choose an answer.")
            return redirect(url_for("medical"))
        with db() as con:
            con.execute("UPDATE users SET age=?, disease=?, medical_done=1 WHERE id=?",
                        (int(age), disease, user["id"]))
        return redirect(url_for("home"))
    return render_template("medical.html", user=user)

@app.route("/transaction", methods=["POST"])
def transaction():
    user = current_user()
    if not user: return jsonify(ok=False, message="Please log in."), 401
    kind = request.form.get("kind","deposit")
    channel = request.form.get("channel","MTN Mobile Money")
    try: amount = int(request.form.get("amount","0"))
    except ValueError: amount = 0
    if kind not in ("deposit","withdrawal") or amount < 1000:
        return jsonify(ok=False, message="Enter a valid amount of at least UGX 1,000.")
    with db() as con:
        con.execute("INSERT INTO transactions(user_id,kind,amount,channel) VALUES(?,?,?,?)",
                    (user["id"],kind,amount,channel))
    return jsonify(ok=True, message=f"Demo {kind} request recorded: UGX {amount:,}. No money was moved.")

@app.route("/equipment")
def equipment():
    user=current_user()
    if not user: return redirect(url_for("index"))
    return render_template("equipment.html", user=user)

@app.route("/earning")
def earning():
    user=current_user()
    if not user: return redirect(url_for("index"))
    with db() as con:
        tx=con.execute("SELECT * FROM transactions WHERE user_id=? ORDER BY id DESC", (user["id"],)).fetchall()
    return render_template("earning.html", user=user, transactions=tx)

@app.route("/profile")
def profile():
    user=current_user()
    if not user: return redirect(url_for("index"))
    return render_template("profile.html", user=user)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
