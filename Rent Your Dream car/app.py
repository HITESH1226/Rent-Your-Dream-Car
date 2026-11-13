from flask import *
import sqlite3 as sq
from datetime import datetime
import os
import uuid
app=Flask(__name__)

app.secret_key = "My_key2612"
DATABASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend.db")

CAR_SEEDS = [
    ("Maruti Fronx 24-25", 3000, "SUV", "https://revvselfdrivecar.s3.us-west-2.amazonaws.com/Fronx_ST.png"),
    ("Maruti Swift 24-25", 3400, "Hatchback", "https://revvselfdrivecar.s3.us-west-2.amazonaws.com/st_feb24/Swift_ST.png"),
    ("Maruti Swift Dzire", 3401, "Sedan", "https://s3-us-west-2.amazonaws.com/revvselfdrivecar/carImages/white_images/dzire.png"),
    ("Maruti Baleno", 3350, "Hatchback", "https://s3-us-west-2.amazonaws.com/revvselfdrivecar/carImages/white_images/baleno.png"),
    ("Hyundai Aura 24-25", 3300, "Sedan", "https://revvselfdrivecar.s3.us-west-2.amazonaws.com/WhatsApp+Image+2024-12-09+at+19.23.30.jpeg"),
    ("Tata Punch 24-25", 3500, "SUV", "https://revvselfdrivecar.s3.us-west-2.amazonaws.com/WhatsApp+Image+2025-08-08+at+21.29.27.jpeg"),
]

def connect_db():
    con = sq.connect(DATABASE)
    con.row_factory = sq.Row
    return con

def init_admin_features():
    """Create admin-managed fleet fields safely for existing project databases."""
    con = connect_db()
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS cars (car_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, price_per_day INTEGER NOT NULL CHECK(price_per_day >= 0), category TEXT NOT NULL DEFAULT 'Other', image_url TEXT NOT NULL DEFAULT '', is_active INTEGER NOT NULL DEFAULT 1)")
    cur.execute("CREATE TABLE IF NOT EXISTS admin_activity (activity_id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT NOT NULL, details TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")
    cols = [row[1] for row in cur.execute("PRAGMA table_info(register)").fetchall()]
    if "is_active" not in cols:
        cur.execute("ALTER TABLE register ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1")
    cur.executemany("INSERT OR IGNORE INTO cars (name, price_per_day, category, image_url) VALUES (?, ?, ?, ?)", CAR_SEEDS)
    cur.execute("""CREATE TABLE IF NOT EXISTS payments (
        payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id INTEGER NOT NULL UNIQUE,
        customer_email TEXT NOT NULL,
        amount INTEGER NOT NULL,
        payment_method TEXT NOT NULL,
        payment_status TEXT NOT NULL DEFAULT 'Pending',
        transaction_ref TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""")
    con.commit()
    con.close()


def log_admin(action, details):
    con = connect_db()
    con.execute("INSERT INTO admin_activity (action, details) VALUES (?, ?)", (action, details))
    con.commit()
    con.close()

init_admin_features()

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin@123"

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/reg")
def reg():
    return render_template("reg.html")

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/gallery")
def gallery():
    return render_template("gallery.html")

@app.route("/cars")
def cars():
    con = connect_db()
    fleet = con.execute("SELECT * FROM cars WHERE is_active=1 ORDER BY car_id").fetchall()
    con.close()
    return render_template("cars.html", fleet=fleet)

@app.route("/contactus")
def contactus():
    return render_template("contactus.html")

@app.route("/formsave",methods=["GET","POST"])
def formsave():

    if request.method == "POST":
        fn=request.form["fullname"]
        em=request.form["email"]
        ps=request.form["password"]
        cn=request.form["contact"]
        ct=request.form["city"]

        con=sq.connect(DATABASE)
        cur=con.cursor()
        cur.execute("insert into register(fullname,email,password,contact,city)values(?,?,?,?,?)",(fn,em,ps,cn,ct))

        con.commit()    
        con.close()

        return redirect(url_for("viewdata"))

    else:
        return "Failed"

@app.route("/viewdata")
def viewdata():

    con=sq.connect(DATABASE)
    cur=con.cursor()

    cur.execute("select * from register order by id DESC")
    data1=cur.fetchall()

    con.commit()
    con.close()
    return render_template("viewdata.html",data=data1)

@app.route("/logincheck", methods=["GET", "POST"])
def logincheck():
    if request.method == "POST":
        em = request.form["email"].strip()
        ps = request.form["password"]

        con = sq.connect(DATABASE)
        cur = con.cursor()

        cur.execute(
            "SELECT * FROM register WHERE email = ? AND password = ? AND is_active = 1",
            (em, ps)
        )
        data = cur.fetchone()
        con.close()

        if data:
            session["username"] = data[1] 
            session["user_email"] = data[2] 
            return redirect(url_for("home"))

        return render_template("login.html",error="Invalid email or password")

    return redirect(url_for("login"))


@app.route("/book_car", methods=["GET", "POST"])
def book_car():

    if "user_email" not in session:
        return redirect(url_for("login"))

    car_name = request.args.get("car_name", "").strip()
    con = connect_db()
    car = con.execute("SELECT name, price_per_day FROM cars WHERE name = ? AND is_active = 1", (car_name,)).fetchone()
    con.close()
    if not car:
        return "This car is unavailable or the selected car is invalid.", 400
    price = car["price_per_day"]

    # Get customer details from the login session
    name = session["username"]
    email = session["user_email"]

    if request.method == "POST":

        pickup = request.form.get("pickup_date", "")
        return_date = request.form.get("return_date", "")

        if not pickup or not return_date:
            return "Please select pickup and return dates.", 400

        try:
            pickup_date = datetime.strptime(
                pickup, "%Y-%m-%d"
            ).date()

            drop_date = datetime.strptime(
                return_date, "%Y-%m-%d"
            ).date()

        except ValueError:
            return "Invalid date format", 400

        if pickup_date < datetime.today().date():
            return "Pickup date cannot be in the past", 400

        if drop_date <= pickup_date:
            return "Return date must be after pickup date", 400

        total_days = (drop_date - pickup_date).days
        total_price = total_days * price

        con = sq.connect(DATABASE)
        cur = con.cursor()

        cur.execute("SELECT booking_id FROM bookings WHERE car_name = ? AND status != 'Cancelled' AND pickup_date < ? AND return_date > ? LIMIT 1", (car_name, return_date, pickup))

        existing_booking = cur.fetchone()

        if existing_booking:
            con.close()
            return ('This car is already booked for these dates.' "Please choose different dates.",409)

        cur.execute("INSERT INTO bookings (customer_name,customer_email,car_name,price_per_day,pickup_date,return_date,total_days,total_price,status)VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (name,email,car_name,price,pickup,return_date,total_days,total_price,"Pending"))

        con.commit()
        booking_id = cur.lastrowid
        con.close()

        return render_template("booking_success.html",booking_id=booking_id,name=name,car_name=car_name,pickup=pickup,return_date=return_date,total_days=total_days,price=price,total_price=total_price)

    return render_template("booking.html",car_name=car_name,price=price)
 


@app.route("/payment/<int:booking_id>", methods=["GET", "POST"])
def payment_page(booking_id):

    if "user_email" not in session:
        return redirect(url_for("login"))

    email = session["user_email"]
    con = connect_db()
    booking = con.execute(
        "SELECT * FROM bookings WHERE booking_id=? AND customer_email=?",
        (booking_id, email)
    ).fetchone()
    if not booking:
        con.close()
        return "Booking not found.", 404
    if booking["status"] == "Cancelled":
        con.close()
        return "Payment is unavailable for a cancelled booking.", 400

    existing = con.execute(
        "SELECT * FROM payments WHERE booking_id=?", (booking_id,)
    ).fetchone()

    if request.method == "POST":
        method = request.form.get("payment_method", "")
        if method not in ("UPI (Demo)", "Card (Demo)", "Cash on pickup"):
            con.close()
            return "Please choose a valid payment method.", 400

        if existing and existing["payment_status"] in ("Paid (Demo)", "Pending - Cash on pickup"):
            con.close()
            return redirect(url_for("payment_page", booking_id=booking_id))

        if method == "Cash on pickup":
            status = "Pending - Cash on pickup"
            reference = None
        else:
            # This is a local demonstration only; no gateway or real charge is used.
            status = "Paid"
            reference = "DEMO-" + uuid.uuid4().hex[:10].upper()

        con.execute("""INSERT INTO payments
            (booking_id, customer_email, amount, payment_method, payment_status, transaction_ref)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(booking_id) DO UPDATE SET
                amount=excluded.amount, payment_method=excluded.payment_method,
                payment_status=excluded.payment_status, transaction_ref=excluded.transaction_ref,
                created_at=CURRENT_TIMESTAMP""",
            (booking_id, email, booking["total_price"], method, status, reference))
        con.commit()
        con.close()
        return redirect(url_for("payment_page", booking_id=booking_id, result=1))

    con.close()
    return render_template("payment.html", booking=booking, payment=existing,
                           result=request.args.get("result"))


@app.route("/my_bookings")
def my_bookings():

    if "user_email" not in session:
        return redirect(url_for("login"))

    email = session["user_email"]

    con = sq.connect(DATABASE)
    con.row_factory = sq.Row
    cur = con.cursor()

    cur.execute("""SELECT b.booking_id, b.car_name, b.pickup_date, b.return_date,
        b.total_days, b.total_price, b.status,
        COALESCE(p.payment_status, 'Not paid') AS payment_status,
        p.payment_method, p.transaction_ref
        FROM bookings b LEFT JOIN payments p ON p.booking_id=b.booking_id
        WHERE b.customer_email = ? ORDER BY b.booking_id DESC""", (email,))

    bookings = cur.fetchall()
    con.close()

    return render_template("my_bookings.html",bookings=bookings,email=email,cancelled=request.args.get("cancelled"))


@app.route("/cancel_booking", methods=["POST"])
def cancel_booking():

    if "user_email" not in session:
        return redirect(url_for("login"))

    booking_id = request.form.get("booking_id", type=int)
    email = session["user_email"]

    if not booking_id:
        return "Invalid booking ID", 400

    con = sq.connect(DATABASE)
    cur = con.cursor()

    cur.execute("UPDATE bookings SET status = 'Cancelled' WHERE booking_id = ? AND customer_email = ? AND status = 'Pending'", (booking_id, email))

    updated = cur.rowcount
    con.commit()
    con.close()

    if updated == 0:
        return "Booking not found or already cancelled.", 400

    return redirect(url_for("my_bookings", cancelled=1))


@app.route("/admin")
def admin():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))
    con = connect_db()
    bookings = con.execute("""SELECT b.*, COALESCE(p.payment_status, 'Not paid') AS payment_status,
        p.payment_method, p.transaction_ref
        FROM bookings b LEFT JOIN payments p ON p.booking_id=b.booking_id
        ORDER BY b.booking_id DESC""").fetchall()
    stats = {
        "total_bookings": con.execute("SELECT COUNT(*) FROM bookings").fetchone()[0],
        "pending": con.execute("SELECT COUNT(*) FROM bookings WHERE status='Pending'").fetchone()[0],
        "confirmed": con.execute("SELECT COUNT(*) FROM bookings WHERE status='Confirmed'").fetchone()[0],
        "cancelled": con.execute("SELECT COUNT(*) FROM bookings WHERE status='Cancelled'").fetchone()[0],
        "revenue": con.execute("SELECT COALESCE(SUM(total_price),0) FROM bookings WHERE status='Confirmed'").fetchone()[0],
        "customers": con.execute("SELECT COUNT(*) FROM register").fetchone()[0],
        "active_cars": con.execute("SELECT COUNT(*) FROM cars WHERE is_active=1").fetchone()[0],
        "total_cars": con.execute("SELECT COUNT(*) FROM cars").fetchone()[0],
    }
    monthly = con.execute("SELECT substr(pickup_date,1,7) AS month, COALESCE(SUM(total_price),0) AS revenue FROM bookings WHERE status='Confirmed' GROUP BY substr(pickup_date,1,7) ORDER BY month DESC LIMIT 6").fetchall()
    con.close()
    monthly = list(reversed(monthly))
    return render_template("admin.html", bookings=bookings, stats=stats, monthly=monthly)


@app.route("/admin/cars", methods=["GET", "POST"])
def admin_cars():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))
    con = connect_db()
    if request.method == "POST":
        action = request.form.get("action", "save")
        if action == "toggle":
            car_id = request.form.get("car_id", type=int)
            con.execute("UPDATE cars SET is_active = CASE WHEN is_active=1 THEN 0 ELSE 1 END WHERE car_id=?", (car_id,))
            con.commit()
            con.close()
            log_admin("Car availability changed", f"Car ID {car_id}")
            flash("Car availability updated.", "success")
            return redirect(url_for("admin_cars"))
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "Other").strip() or "Other"
        image_url = request.form.get("image_url", "").strip()
        price = request.form.get("price_per_day", type=int)
        car_id = request.form.get("car_id", type=int)
        if not name or price is None or price < 0:
            flash("Enter a car name and a valid non-negative daily price.", "error")
        else:
            try:
                if car_id:
                    con.execute("UPDATE cars SET name=?, price_per_day=?, category=?, image_url=? WHERE car_id=?", (name, price, category, image_url, car_id))
                    detail = f"Updated {name}"
                else:
                    con.execute("INSERT INTO cars (name, price_per_day, category, image_url) VALUES (?, ?, ?, ?)", (name, price, category, image_url))
                    detail = f"Added {name}"
                con.commit()
                con.close()
                log_admin("Fleet updated", detail)
                flash(detail + " successfully.", "success")
                return redirect(url_for("admin_cars"))
            except sq.IntegrityError:
                flash("A car with this name already exists.", "error")
    edit_id = request.args.get("edit", type=int)
    edit_car = con.execute("SELECT * FROM cars WHERE car_id=?", (edit_id,)).fetchone() if edit_id else None
    cars = con.execute("SELECT * FROM cars ORDER BY is_active DESC, name COLLATE NOCASE").fetchall()
    con.close()
    return render_template("admin_cars.html", cars=cars, edit_car=edit_car)


@app.route("/admin/customers")
def admin_customers():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))
    con = connect_db()
    customers = con.execute("SELECT r.id, r.fullname, r.email, r.contact, r.city, r.is_active, COUNT(b.booking_id) AS booking_count, COALESCE(SUM(CASE WHEN b.status='Confirmed' THEN b.total_price ELSE 0 END),0) AS confirmed_spend FROM register r LEFT JOIN bookings b ON b.customer_email=r.email GROUP BY r.id ORDER BY r.id DESC").fetchall()
    con.close()
    return render_template("admin_customers.html", customers=customers)


@app.route("/admin/customer_status", methods=["POST"])
def admin_customer_status():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))
    customer_id = request.form.get("customer_id", type=int)
    con = connect_db()
    row = con.execute("SELECT fullname, is_active FROM register WHERE id=?", (customer_id,)).fetchone()
    if not row:
        con.close()
        flash("Customer not found.", "error")
        return redirect(url_for("admin_customers"))
    new_status = 0 if row["is_active"] else 1
    con.execute("UPDATE register SET is_active=? WHERE id=?", (new_status, customer_id))
    con.commit()
    con.close()
    log_admin("Customer access changed", f"{row['fullname']}: {'active' if new_status else 'disabled'}")
    flash(f"Customer account {'enabled' if new_status else 'disabled'}.", "success")
    return redirect(url_for("admin_customers"))


@app.route("/booking_status", methods=["GET","POST"])
def booking_status():

    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))
    booking_id = request.form.get("booking_id")
    status = request.form.get("status")

    if status not in ["Confirmed", "Cancelled"]:
        return "Invalid booking status", 400

    con = sq.connect(DATABASE)
    cur = con.cursor()

    cur.execute("UPDATE bookings SET status = ? WHERE booking_id = ? AND status = 'Pending'", (status, booking_id))

    con.commit()
    con.close()
    log_admin("Booking status changed", f"Booking #{booking_id}: {status}")

    return redirect(url_for("admin"))

@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["is_admin"] = True
            return redirect(url_for("admin"))

        return render_template(
            "admin_login.html",
            error="Invalid username or password"
        )

    return render_template("admin_login.html")

@app.route("/admin_logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("admin_login"))


@app.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("user_email", None)
    return redirect(url_for("login"))
    
if (__name__) == ("__main__"):
    app.run(debug=True,port=2612)