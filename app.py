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
        existing = {row["name"] for row in con.execute("PRAGMA table_info(users)").fetchall()}
        medical_columns = {
            "date_of_birth":"TEXT","gender":"TEXT","email":"TEXT",
            "address":"TEXT","emergency_contact":"TEXT",
            "medical_history":"TEXT","medications":"TEXT",
            "allergies":"TEXT","surgeries":"TEXT","symptoms":"TEXT",
            "additional_info":"TEXT","medical_consent":"INTEGER DEFAULT 0"
        }
        for column, definition in medical_columns.items():
            if column not in existing:
                con.execute(f"ALTER TABLE users ADD COLUMN {column} {definition}")

        con.execute("""CREATE TABLE IF NOT EXISTS transactions(
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            kind TEXT NOT NULL, amount INTEGER NOT NULL, channel TEXT,
            status TEXT DEFAULT 'Demo pending', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

        con.execute("""CREATE TABLE IF NOT EXISTS wallets(
            user_id INTEGER PRIMARY KEY,
            available_balance INTEGER NOT NULL DEFAULT 0,
            earnings_balance INTEGER NOT NULL DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""")

        con.execute("""CREATE TABLE IF NOT EXISTS wallet_ledger(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            entry_type TEXT NOT NULL,
            amount INTEGER NOT NULL,
            reference TEXT UNIQUE NOT NULL,
            description TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""")

        con.execute("""CREATE TABLE IF NOT EXISTS purchases(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            product_price INTEGER NOT NULL,
            daily_income INTEGER NOT NULL,
            duration_days INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""")

        con.execute("""CREATE TABLE IF NOT EXISTS earning_credits(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            purchase_id INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            credit_date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending_funding',
            reference TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(purchase_id) REFERENCES purchases(id)
        )""")

        con.execute("""CREATE TABLE IF NOT EXISTS business_revenue(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount INTEGER NOT NULL,
            verified INTEGER NOT NULL DEFAULT 0,
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

        con.execute("""CREATE TABLE IF NOT EXISTS bonus_claims(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            amount INTEGER NOT NULL,
            reference TEXT UNIQUE NOT NULL,
            claimed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""")

        con.execute("CREATE INDEX IF NOT EXISTS idx_purchases_user ON purchases(user_id)")
        con.execute("CREATE INDEX IF NOT EXISTS idx_credits_user ON earning_credits(user_id)")


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
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    password = request.form.get("password", "")
    invite = request.form.get("invite_code", "").strip()

    if not name or not phone or len(password) < 6:
        flash("Please enter your full name, phone number and a password of at least 6 characters.", "error")
        return redirect(url_for("index"))

    try:
        with db() as con:
            con.execute(
                "INSERT INTO users(name,phone,password,invite_code) VALUES(?,?,?,?)",
                (name, phone, generate_password_hash(password), invite)
            )
        flash("Registration successful. Please log in with your phone number and password.", "success")
        return redirect(url_for("index", tab="login"))
    except sqlite3.IntegrityError:
        flash("That phone number is already registered. Please log in.", "error")
        return redirect(url_for("index", tab="login"))

@app.route("/login", methods=["POST"])
def login():
    phone = request.form.get("phone", "").strip()
    password = request.form.get("password", "")
    with db() as con:
        user = con.execute("SELECT * FROM users WHERE phone=?", (phone,)).fetchone()

    if not user or not check_password_hash(user["password"], password):
        flash("Login failed: incorrect phone number or password.", "error")
        return redirect(url_for("index", tab="login"))

    session["user_id"] = user["id"]
    flash("Login successful.", "success")
    return redirect(url_for("home"))

@app.route("/home")
def home():
    user = current_user()
    if not user:
        return redirect(url_for("index"))
    with db() as con:
        con.execute("INSERT OR IGNORE INTO wallets(user_id) VALUES(?)", (user["id"],))
        wallet = con.execute(
            "SELECT * FROM wallets WHERE user_id=?",
            (user["id"],)
        ).fetchone()
        tx = con.execute(
            "SELECT * FROM transactions WHERE user_id=? ORDER BY id DESC LIMIT 5",
            (user["id"],)
        ).fetchall()

        bonus_claimed = con.execute(
            "SELECT 1 FROM bonus_claims WHERE user_id=?",
            (user["id"],)
        ).fetchone() is not None

    return render_template(
        "home.html",
        user=user,
        transactions=tx,
        wallet=wallet,
        bonus_claimed=bonus_claimed
    )


@app.route("/medical", methods=["GET", "POST"])
def medical():
    user = current_user()
    if not user:
        return redirect(url_for("index"))

    if request.method == "POST":
        age = request.form.get("age", "").strip()
        gender = request.form.get("gender", "").strip()
        emergency_contact = request.form.get("emergency_contact", "").strip()
        symptoms = request.form.get("symptoms", "").strip()
        consent = request.form.get("medical_consent") == "yes"

        if not age.isdigit() or not 1 <= int(age) <= 120:
            flash("Please enter a valid age between 1 and 120.", "error")
            return redirect(url_for("medical"))

        if not gender or not emergency_contact or not symptoms or not consent:
            flash("Please complete the required fields and confirm the declaration.", "error")
            return redirect(url_for("medical"))

        values = (
            int(age),
            request.form.get("date_of_birth", "").strip(),
            gender,
            request.form.get("email", "").strip(),
            request.form.get("address", "").strip(),
            emergency_contact,
            request.form.get("medical_history", "").strip(),
            request.form.get("medications", "").strip(),
            request.form.get("allergies", "").strip(),
            request.form.get("surgeries", "").strip(),
            symptoms,
            request.form.get("additional_info", "").strip(),
            1,
            user["id"]
        )

        with db() as con:
            con.execute("""
                UPDATE users SET age=?, date_of_birth=?, gender=?, email=?,
                address=?, emergency_contact=?, medical_history=?, medications=?,
                allergies=?, surgeries=?, symptoms=?, additional_info=?,
                medical_consent=?, medical_done=1 WHERE id=?
            """, values)

        flash("Medical information submitted successfully.", "success")
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


INVESTMENT_PRODUCTS = [
    {"id":1,"price":18000,"daily":2500,"days":13},
    {"id":2,"price":30000,"daily":7500,"days":30},
    {"id":3,"price":47000,"daily":12000,"days":7},
    {"id":4,"price":50000,"daily":14300,"days":20},
    {"id":5,"price":76000,"daily":21000,"days":7},
    {"id":6,"price":100000,"daily":30000,"days":10},
    {"id":7,"price":140000,"daily":40010,"days":20},
    {"id":8,"price":190000,"daily":60000,"days":10},
    {"id":9,"price":200000,"daily":65000,"days":10},
    {"id":10,"price":240000,"daily":73000,"days":27},
    {"id":11,"price":360000,"daily":100000,"days":12},
    {"id":12,"price":450000,"daily":180000,"days":24},
    {"id":13,"price":500000,"daily":200000,"days":5},
    {"id":14,"price":570000,"daily":207000,"days":8},
    {"id":15,"price":600000,"daily":250000,"days":10},
    {"id":16,"price":900000,"daily":350000,"days":11},
    {"id":17,"price":1000000,"daily":400000,"days":10},
    {"id":18,"price":1200000,"daily":500000,"days":5},
    {"id":19,"price":5000000,"daily":1300000,"days":19},
    {"id":20,"price":75000000,"daily":4000000,"days":50},
]

@app.route("/purchase/<int:product_id>", methods=["POST"])
def purchase(product_id):
    user = current_user()
    if not user:
        return redirect(url_for("index"))

    product = next((x for x in INVESTMENT_PRODUCTS if x["id"] == product_id), None)
    if not product:
        flash("Product not found.", "error")
        return redirect(url_for("equipment"))

    try:
        with db() as con:
            con.execute("BEGIN IMMEDIATE")
            con.execute("INSERT OR IGNORE INTO wallets(user_id) VALUES(?)", (user["id"],))
            wallet = con.execute(
                "SELECT available_balance FROM wallets WHERE user_id=?",
                (user["id"],)
            ).fetchone()

            if wallet["available_balance"] < product["price"]:
                con.rollback()
                flash("Purchase Failed: insufficient available wallet balance.", "error")
                return redirect(url_for("equipment"))

            con.execute(
                "UPDATE wallets SET available_balance=available_balance-?, updated_at=CURRENT_TIMESTAMP WHERE user_id=?",
                (product["price"], user["id"])
            )
            cur = con.execute(
                """INSERT INTO purchases(user_id,product_id,product_price,daily_income,duration_days)
                   VALUES(?,?,?,?,?)""",
                (user["id"], product_id, product["price"], product["daily"], product["days"])
            )
            con.execute(
                """INSERT INTO wallet_ledger(user_id,entry_type,amount,reference,description)
                   VALUES(?,?,?,?,?)""",
                (user["id"], "purchase", -product["price"],
                 f"purchase:{cur.lastrowid}", f"Investment plan #{product_id}")
            )

        flash("Purchase recorded successfully.", "success")
    except Exception:
        app.logger.exception("Purchase processing failed")
        flash("Purchase could not be completed.", "error")

    return redirect(url_for("equipment"))

@app.route("/equipment")
def equipment():
    user = current_user()
    if not user:
        return redirect(url_for("index"))

    with db() as con:
        con.execute("INSERT OR IGNORE INTO wallets(user_id) VALUES(?)", (user["id"],))
        wallet = con.execute(
            "SELECT available_balance FROM wallets WHERE user_id=?",
            (user["id"],)
        ).fetchone()

    return render_template(
        "equipment.html",
        user=user,
        products=INVESTMENT_PRODUCTS,
        wallet_balance=wallet["available_balance"]
    )



def record_business_revenue(amount, notes=""):
    """Record business revenue as unverified until independently confirmed."""
    amount = int(amount)
    if amount <= 0:
        raise ValueError("Revenue must be greater than zero.")

    with db() as con:
        cur = con.execute(
            "INSERT INTO business_revenue(amount,verified,notes) VALUES(?,0,?)",
            (amount, notes.strip())
        )
        return cur.lastrowid



def allocate_verified_revenue():
    """Fund pending credits only from verified, unallocated business revenue."""
    with db() as con:
        con.execute("BEGIN IMMEDIATE")

        revenue = con.execute("""
            SELECT COALESCE(SUM(amount),0)
            FROM business_revenue
            WHERE verified=1
        """).fetchone()[0]

        earning_allocated = con.execute("""
            SELECT COALESCE(SUM(amount),0)
            FROM earning_credits
            WHERE status='credited'
        """).fetchone()[0]

        bonus_allocated = con.execute("""
            SELECT COALESCE(SUM(amount),0)
            FROM bonus_claims
        """).fetchone()[0]

        already_allocated = earning_allocated + bonus_allocated
        available = max(0, revenue - already_allocated)

        pending = con.execute("""
            SELECT id,user_id,amount,reference
            FROM earning_credits
            WHERE status='pending_funding'
            ORDER BY credit_date,id
        """).fetchall()

        funded = 0
        for credit in pending:
            if credit["amount"] > available:
                break

            con.execute("""
                INSERT OR IGNORE INTO wallets(user_id) VALUES(?)
            """, (credit["user_id"],))

            con.execute("""
                UPDATE wallets
                SET earnings_balance=earnings_balance+?,
                    updated_at=CURRENT_TIMESTAMP
                WHERE user_id=?
            """, (credit["amount"], credit["user_id"]))

            con.execute("""
                INSERT INTO wallet_ledger(
                    user_id,entry_type,amount,reference,description
                ) VALUES(?,?,?,?,?)
            """, (
                credit["user_id"], "earning",
                credit["amount"], credit["reference"],
                "Funded from verified business revenue"
            ))

            con.execute("""
                UPDATE earning_credits
                SET status='credited'
                WHERE id=?
            """, (credit["id"],))

            available -= credit["amount"]
            funded += credit["amount"]

        return funded



def generate_daily_earning_credits(credit_date=None):
    """Create pending daily credits for active purchases, once per date."""
    from datetime import date

    credit_date = credit_date or date.today().isoformat()
    created = 0

    with db() as con:
        con.execute("BEGIN IMMEDIATE")

        purchases = con.execute("""
            SELECT id,user_id,daily_income,duration_days,purchased_at
            FROM purchases
            WHERE status='active'
        """).fetchall()

        for purchase in purchases:
            purchase_day = str(purchase["purchased_at"])[:10]
            elapsed = (date.fromisoformat(credit_date) -
                       date.fromisoformat(purchase_day)).days

            if elapsed < 1 or elapsed > purchase["duration_days"]:
                continue

            reference = f"daily-earning:{purchase['id']}:{credit_date}"

            cur = con.execute("""
                INSERT OR IGNORE INTO earning_credits(
                    user_id,purchase_id,amount,credit_date,status,reference
                ) VALUES(?,?,?,?,?,?)
            """, (
                purchase["user_id"], purchase["id"],
                purchase["daily_income"], credit_date,
                "pending_funding", reference
            ))

            created += cur.rowcount

    return created



@app.route("/admin/process-daily-earnings", methods=["POST"])
def admin_process_daily_earnings():
    supplied_key = request.headers.get("X-Admin-Key", "")
    expected_key = os.environ.get("PIMCO_ADMIN_KEY", "")

    if not expected_key or supplied_key != expected_key:
        return jsonify(ok=False, message="Unauthorized."), 401

    created = generate_daily_earning_credits()
    funded = allocate_verified_revenue()

    return jsonify(
        ok=True,
        pending_credits_created=created,
        revenue_funded_amount=funded
    )




@app.route("/claim-bonus", methods=["POST"])
def claim_bonus():
    user = current_user()
    if not user:
        return redirect(url_for("index"))

    amount = 4000
    reference = f"bonus:{user['id']}"

    try:
        with db() as con:
            con.execute("BEGIN IMMEDIATE")

            existing = con.execute(
                "SELECT 1 FROM bonus_claims WHERE user_id=?",
                (user["id"],)
            ).fetchone()

            if existing:
                flash("UNREPEATABLE", "error")
                return redirect(url_for("home"))

            revenue = con.execute(
                "SELECT COALESCE(SUM(amount),0) FROM business_revenue WHERE verified=1"
            ).fetchone()[0]

            earnings_used = con.execute(
                "SELECT COALESCE(SUM(amount),0) FROM earning_credits WHERE status='credited'"
            ).fetchone()[0]

            bonuses_used = con.execute(
                "SELECT COALESCE(SUM(amount),0) FROM bonus_claims"
            ).fetchone()[0]

            if revenue - earnings_used - bonuses_used < amount:
                flash("Bonus funding is not yet available.", "error")
                return redirect(url_for("home"))

            con.execute(
                "INSERT OR IGNORE INTO wallets(user_id) VALUES(?)",
                (user["id"],)
            )

            con.execute(
                "INSERT INTO bonus_claims(user_id,amount,reference) VALUES(?,?,?)",
                (user["id"], amount, reference)
            )

            con.execute("""
                UPDATE wallets
                SET earnings_balance=earnings_balance+?,
                    updated_at=CURRENT_TIMESTAMP
                WHERE user_id=?
            """, (amount, user["id"]))

            con.execute("""
                INSERT INTO wallet_ledger(
                    user_id,entry_type,amount,reference,description
                ) VALUES(?,?,?,?,?)
            """, (
                user["id"], "bonus", amount, reference,
                "One-time UGX 4,000 bonus"
            ))

        flash("Your one-time bonus of UGX 4,000 has been credited to your withdrawable balance.", "success")

    except Exception:
        app.logger.exception("Bonus claim failed")
        flash("Bonus claim could not be completed.", "error")

    return redirect(url_for("home"))

@app.route("/earning")
def earning():
    user = current_user()
    if not user:
        return redirect(url_for("index"))

    with db() as con:
        tx = con.execute(
            "SELECT * FROM transactions WHERE user_id=? ORDER BY id DESC",
            (user["id"],)
        ).fetchall()

        purchases = con.execute(
            "SELECT * FROM purchases WHERE user_id=? ORDER BY id DESC",
            (user["id"],)
        ).fetchall()

        wallet = con.execute(
            "SELECT * FROM wallets WHERE user_id=?",
            (user["id"],)
        ).fetchone()

        total_income = sum(
            item["daily_income"] * item["duration_days"]
            for item in purchases
        )

    return render_template(
        "earning.html",
        user=user,
        transactions=tx,
        purchases=purchases,
        wallet=wallet,
        total_income=total_income
    )


@app.route("/profile")
def profile():
    user=current_user()
    if not user: return redirect(url_for("index"))
    return render_template("profile.html", user=user)


@app.route("/change-password", methods=["GET", "POST"])
def change_password():
    user = current_user()
    if not user:
        return redirect(url_for("index"))

    if request.method == "POST":
        current = request.form.get("current_password", "")
        new = request.form.get("new_password", "")
        confirm = request.form.get("confirm_password", "")

        if not check_password_hash(user["password"], current):
            flash("Current password is incorrect.", "error")
        elif len(new) < 6:
            flash("New password must contain at least 6 characters.", "error")
        elif new != confirm:
            flash("New passwords do not match.", "error")
        else:
            with db() as con:
                con.execute(
                    "UPDATE users SET password=? WHERE id=?",
                    (generate_password_hash(new), user["id"])
                )
            flash("Password changed successfully.", "success")
            return redirect(url_for("profile"))

    return render_template("change_password.html", user=user)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# === SEASONAL OFFERS UPDATE ===
from datetime import datetime, timedelta, timezone
from flask import request, flash, redirect

KAMPALA_TZ = timezone(timedelta(hours=3))

SEASONAL_PRODUCTS = [
    {"id": 21, "name": "Christmas Premium", "price": 1000000, "daily": 750000, "days": 2, "active_hours": 8, "starts_at": "2026-11-25T00:00:00+03:00", "season": "Christmas"},
    {"id": 22, "name": "Christmas Mini", "price": 1000, "daily": 400, "days": 4, "active_hours": 4, "starts_at": "2026-11-25T00:00:00+03:00", "season": "Christmas"},
    {"id": 23, "name": "Christmas Gift", "price": 50000, "daily": 25000, "days": 4, "active_hours": 0.5, "starts_at": "2026-11-25T00:00:00+03:00", "season": "Christmas"},
    {"id": 24, "name": "Christmas Box", "price": 5000, "daily": 3000, "days": 3, "active_hours": 24, "starts_at": "2026-11-25T00:00:00+03:00", "season": "Christmas"},
    {"id": 25, "name": "Christmas Family", "price": 20000, "daily": 7500, "days": 4, "active_hours": 72, "starts_at": "2026-11-25T00:00:00+03:00", "season": "Christmas"},
    {"id": 26, "name": "Black November Hen", "price": 4000, "daily": 3000, "days": 2, "active_hours": 7, "starts_at": "2026-12-26T00:00:00+03:00", "season": "Black November"},
    {"id": 27, "name": "Black November Mini", "price": 500, "daily": 300, "days": 4, "active_hours": 4, "starts_at": "2026-12-26T00:00:00+03:00", "season": "Black November"},
    {"id": 28, "name": "Black November Premium", "price": 100000, "daily": 70000, "days": 10, "active_hours": 24, "starts_at": "2026-12-26T00:00:00+03:00", "season": "Black November"},
    {"id": 29, "name": "Black November Matooke", "price": 49000, "daily": 26000, "days": 25, "active_hours": 216, "starts_at": "2026-12-26T00:00:00+03:00", "season": "Black November"},
]

existing_ids = {item.get("id") for item in INVESTMENT_PRODUCTS}
INVESTMENT_PRODUCTS.extend(
    item.copy() for item in SEASONAL_PRODUCTS
    if item["id"] not in existing_ids
)

@app.before_request
def validate_seasonal_purchase_window():
    if request.endpoint != "purchase":
        return None

    product_id = request.view_args.get("product_id") if request.view_args else None
    offer = next((p for p in SEASONAL_PRODUCTS if p["id"] == product_id), None)
    if not offer:
        return None

    now = datetime.now(KAMPALA_TZ)
    start = datetime.fromisoformat(offer["starts_at"])
    end = start + timedelta(hours=offer["active_hours"])

    if now < start:
        flash("This seasonal offer has not started yet.", "warning")
        return redirect(request.referrer or "/")

    if now >= end:
        flash("Expired. Please try again later.", "warning")
        return redirect(request.referrer or "/")

    return None
# === END SEASONAL OFFERS UPDATE ===


if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
