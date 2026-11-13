# 🚗 Rent Your Dream – Car Rental Management System

**Rent Your Dream** is a Flask-based web application that allows users to browse available cars, book vehicles, manage reservations, and make payments. It also provides an admin dashboard to manage cars, customers, bookings, and monitor rental business analytics.

## ✨ Features

### 👤 User Features
- User Registration and Login
- Browse available rental cars
- View car details and rental prices
- Book cars by selecting pickup and return dates
- Calculate total rental costs automatically
- Make payments using available demo payment options
- View booking history
- Cancel pending bookings

### 🔐 Admin Features
- Admin Login and Dashboard
- Analytics and Revenue Overview
- Add, Edit, and Manage Cars
- Enable or Disable Car Availability
- Manage Customer Accounts
- View and Manage Bookings
- Confirm or Cancel Reservations
- Track Payment Records
- Admin Activity Tracking

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend Programming |
| Flask | Web Framework |
| SQLite | Database |
| HTML5 | Web Structure |
| CSS3 | Styling |
| JavaScript | Frontend Functionality |
| Bootstrap | Responsive UI |

## 📂 Project Structure

```text
Rent Your Dream/
│
├── backend.db
│
└── flask_pro/
    ├── app.py
    ├── db.py
    │
    ├── static/
    │   ├── css/
    │   ├── js/
    │   └── images/
    │
    └── templates/
        ├── home.html
        ├── login.html
        ├── reg.html
        ├── cars.html
        ├── booking.html
        ├── payment.html
        ├── my_bookings.html
        ├── admin.html
        ├── admin_cars.html
        └── admin_customers.html
```

## ⚙️ Installation and Setup

**1. Clone the repository**

```bash
git clone https://github.com/your-username/your-repository.git
```

**2. Open the project folder**

```bash
cd "Rent Your Dream/flask_pro"
```

**3. Install Flask**

```bash
pip install Flask
```

**4. Run the application**

```bash
python app.py
```

**5. Open in your browser**

```text
http://127.0.0.1:2612/
```

## 🔑 Admin Login

- Username: `admin`
- Password: `admin@123`

*Change the default credentials before deploying the project.*

## 💳 Payment Information

The project includes demonstration payment options such as UPI, Card, and Cash on Pickup. Online payment options simulate transactions locally and do not process real payments.

## 🎯 Project Objective

The main objective of Rent Your Dream is to simplify the car rental process by providing an easy-to-use platform for customers and an efficient management system for administrators.

## 👨‍💻 Developer

**Hitesh Sonavane**

Developed using Python, Flask, SQLite, HTML, CSS, and JavaScript.

---

⭐ If you like this project, don't forget to give it a star!
