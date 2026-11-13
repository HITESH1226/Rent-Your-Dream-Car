import sqlite3 as sq
con=sq.connect("backend.db")

cur=con.cursor()

# cur.execute("create table register(id INTEGER PRIMARY KEY AUTOINCREMENT, fullname varchar(50), email varchar(25), password varchar(15), contact int, city varchar(20))")
# cur.execute("insert into register(id,fullname,email,password,contact,city)values(?,?,?,?,?,?)",(1,"Hitesh Sonavane","hitesh@gmail.com",'123456','0987456321',"Dhule"))
# cur.execute("drop table register")
# cur.execute("create table IF NOT EXISTS register (id INTEGER PRIMARY KEY AUTOINCREMENT,fullname varchar(50),email varchar(20),password varchar(10),contact int,city varchar(20))")

# cur.execute("CREATE TABLE IF NOT EXISTS bookings (booking_id INTEGER PRIMARY KEY AUTOINCREMENT,customer_name TEXT NOT NULL,customer_email TEXT NOT NULL,car_name TEXT NOT NULL,price_per_day INTEGER NOT NULL,pickup_date TEXT NOT NULL,return_date TEXT NOT NULL,total_days INTEGER NOT NULL,total_price INTEGER NOT NULL,status TEXT DEFAULT 'Pending')")

con.commit()
con.close()