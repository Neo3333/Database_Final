from flask import Flask, render_template,request,session,url_for,redirect
import pymysql
import hashlib
from datetime import date
from datetime import timedelta

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='airsystem',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#Search for flights
@app.route('/searchUpcomingFlights', methods=['GET', 'POST'])
def searchUpcomingFlights():
	dept_airport = request.form['dept_airport']
	dept_city = request.form['dept_city']
	arr_airport = request.form['arr_airport']
	arr_city = request.form['arr_city']
	date = str(request.form['date'])
	cursor = conn.cursor()
	control_list=[]	
	if dept_airport!='':
		control_list.append("flight.departure_airport = '%s'"%(dept_airport))
	if arr_airport!='':
		control_list.append("flight.arrival_airport = '%s'"%(arr_airport))
	if date!='':
		control_list.append("DATE(flight.departure_time) = '%s'"%(date))
	if dept_city!='':
		control_list.append("dept.airport_city = '%s'"%(dept_city))
	if arr_city!='':
		control_list.append("arr.airport_city = '%s'"%(arr_city))
	
	if len(control_list)==0:
		query = "SELECT * \
				FROM (flight, airport as dept, airport as arr)\
				WHERE flight.departure_airport=dept.airport_name and flight.arrival_airport=arr.airport_name AND flight.status = 'upcoming'"
	else:
		query = "SELECT * \
				FROM (flight, airport as dept, airport as arr) \
				WHERE flight.departure_airport=dept.airport_name and flight.arrival_airport=arr.airport_name AND flight.status = 'upcoming' AND " + " AND ".join(control_list);
	cursor.execute(query)
	data = cursor.fetchall()
	error = None
	conn.commit()
	cursor.close()
	try:
		username=session['username'];
		usertype=session['type'];
		print(username, usertype)
		return render_template('search_results.html',result = data, type = 'buy')
	except:
		return render_template('search_results.html', result=data);
	
@app.route('/backToIndex')
def backToIndex():
	try:
		return render_template('index.html', username=session['username'], usertype=session['type']);
	except:
		return render_template('index.html');

@app.route('/searchFlightStatus', methods=['GET', 'POST'])
def searchFlightStatus():
	flight_num = request.form['flight_num']
	departure_date = str(request.form['departure_date'])
	arrival_date = str(request.form
	['arrival_date'])
	control_list=[]
	if flight_num!='':
		control_list.append("flight_num='%d'"%(int(flight_num)))
	if departure_date != '':
		control_list.append("DATE(departure_time) = '%s'"%(departure_date))
	if arrival_date != '':
		control_list.append("DATE(arrival_time) = '%s'"%(arrival_date))
	if len(control_list) == 0:
		query = "SELECT * FROM flight"
	else:
		query = "SELECT * FROM flight WHERE " + " AND ".join(control_list)
	cursor=conn.cursor()
	cursor.execute(query)
	data=cursor.fetchall()
	error = None
	conn.commit()
	cursor.close()
	return render_template('search_results.html',result = data)

@app.route('/register')
def register():
	return render_template('register.html')
	
@app.route('/registerCustomer', methods=['GET', 'POST'])
def registerCustomer():
	username = request.form['username']
	password = request.form['password']
	name = request.form['name']
	building_number = request.form['building_number']
	street = request.form['street']
	city = request.form['city']
	state = request.form['state']
	phone = request.form['phone']
	passport_number = request.form['passport_number']
	passport_expiration = request.form['passport_expiration']
	passport_country = request.form['passport_country']
	date_of_birth = str(request.form['date_of_birth'])
	cursor = conn.cursor()
	query = 'SELECT * FROM customer WHERE email = %s'
	cursor.execute(query, (username))
	data = cursor.fetchone()
	if(data):
		error = "This user already exists"
		return render_template('register.html', error = error)
	else:
		ins = 'INSERT INTO customer VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
		cursor.execute(ins,(username,name,password,building_number,street,city,state,phone,passport_number,passport_expiration,passport_country,date_of_birth))
		conn.commit()
		cursor.close()
		return render_template('index.html')
	
@app.route('/registerStaff', methods=['GET', 'POST'])
def registerStaff():
	username = request.form['username']
	password = request.form['password']
	first_name = request.form['first_name']
	last_name = request.form['last_name']
	date_of_birth = str(request.form['date_of_birth'])
	airline_name = request.form['airline_name']
	
	cursor = conn.cursor()
	query = 'SELECT * FROM airline_staff WHERE username = %s'
	query2 = 'SELECT * FROM airline WHERE airline_name = %s'
	cursor.execute(query, (username))
	data = cursor.fetchone()
	cursor.execute(query2,(airline_name))
	data1 = cursor.fetchone()
	if (data1 == None):
		error = "This airline doesn't exist"
		return render_template('register.html', error = error)
	if (data):
		error = "This staff already exists"
		return render_template('register.html', error = error)
	else:
		ins = 'INSERT INTO airline_staff VALUES(%s,%s,%s,%s,%s,%s)'
		cursor.execute(ins,(username,password,first_name,last_name,date_of_birth,airline_name))
		conn.commit()
		cursor.close()
		return render_template('index.html')
		
@app.route('/registerAgent', methods=['GET', 'POST'])
def registerAgent():
	username = request.form['username']
	password = request.form['password']
	booking_agent_id = request.form['booking_agent_id']
	
	cursor = conn.cursor()
	query = 'SELECT * FROM booking_agent WHERE email = %s'
	cursor.execute(query, (username))
	data = cursor.fetchone()
	
	if (data):
		error = "This agent already exists"
		return render_template('register.html', error = error)
	else:
		ins = 'INSERT INTO booking_agent VALUES(%s,%s,%s)'
		cursor.execute(ins,(username,password,booking_agent_id))
		conn.commit()
		cursor.close()
		return render_template('index.html')
		
@app.route('/login')
def login():
	return render_template('login.html')
	
@app.route('/loginCustomer', methods=['GET', 'POST'])
def loginCustomer():
	username = request.form['username']
	password = request.form['password']
	cursor = conn.cursor()
	query = 'SELECT * FROM customer WHERE email = %s and password = %s'
	cursor.execute(query, (username, password))
	data = cursor.fetchone()
	
	if (data):
		session['username'] = username
		session['type'] = 'customer'
		return redirect(url_for('hello'))
	else:
		error = "Invalid username or incorrect password"
		return render_template('login.html', error=error)

@app.route('/loginStaff', methods=['GET', 'POST'])
def loginStaff():
	username = request.form['username']
	password = request.form['password']
	cursor = conn.cursor()
	query = 'SELECT * FROM airline_staff WHERE username = %s and password = %s'
	cursor.execute(query, (username, password))
	data = cursor.fetchone()
	
	if (data):
		session['username'] = username
		session['type'] = 'airline_staff'
		return redirect(url_for('hello'))
	else:
		error = "Invalid username or incorrect password"
		return render_template('login.html', error=error)
		
@app.route('/loginAgent', methods=['GET', 'POST'])
def loginAgent():
	username = request.form['username']
	password = request.form['password']
	cursor = conn.cursor()
	query = 'SELECT * FROM booking_agent WHERE email = %s and password = %s'
	cursor.execute(query, (username, password))
	data = cursor.fetchone()
	
	if (data):
		session['username'] = username
		session['type'] = 'booking_agent'
		return redirect(url_for('hello'))
	else:
		error = "Invalid username or incorrect password"
		return render_template('login.html', error=error)

@app.route('/', methods=['GET', 'POST'])
def hello():
	try:
		username = session['username']
		usertype = session['type']
		return render_template('index.html', username=username, usertype=usertype)
	except:
		return render_template('index.html');

@app.route('/viewMyFlight', methods=['GET', 'POST'])
def viewMyFlight():
	dept_airport = request.form['dept_airport']
	arr_airport = request.form['arr_airport']
	start_date = str(request.form['start_date'])
	end_date = str(request.form['end_date'])
	username = session['username']
	control_list=[]
	if dept_airport!='':
		control_list.append("departure_airport = '%s'"%(dept_airport))
	if arr_airport!='':
		control_list.append("arrival_airport = '%s'"%(arr_airport))
	if start_date!='':
		control_list.append("DATE(departure_time) > '%s'"%(start_date))
	if end_date!='':
		control_list.append("DATE(arrival_time) < '%s'"%(end_date))
	
	if len(control_list) == 0:
		query = "SELECT * FROM flight NATURAL JOIN ticket NATURAL JOIN purchases \
                WHERE status = 'upcoming' AND customer_email = %s"%(username)
	else:
		query = "SELECT * FROM flight NATURAL JOIN ticket NATURAL JOIN purchases \
                WHERE customer_email = %s AND "%(username) + " AND ".join(control_list)

	print(query)
	cursor = conn.cursor()
	cursor.execute(query)
	data = cursor.fetchall()
	conn.commit()
	cursor.close()
	error = None
	return render_template('search_results.html',result = data);

@app.route('/purchaseC2/<airline_name>/<flight_num>',methods=['GET','POST'])
def purchaseC2(airline_name,flight_num):
    #ticket_id = request.form['ticket_id']
    username = session['username']
    cursor=conn.cursor()
    message = None
    query_0 = 'SELECT seats_left FROM flight WHERE airline_name = %s AND flight_num = %s'
    cursor.execute(query_0,(airline_name,flight_num))
    data_0 = cursor.fetchone()
    seats_left = int(data_0['seats_left'])
    if (seats_left > 0):
        query_1 = 'SELECT MAX(ticket_id) FROM ticket'
        cursor.execute(query_1)
        data_1 = cursor.fetchone()
        max = data_1['MAX(ticket_id)']
        if (max == None):
            new_id = 1;
        else:
            new_id = int(max) + 1
        query_2 = 'INSERT INTO ticket VALUES(%s,%s,%s)'
        cursor.execute(query_2,(str(new_id),airline_name,flight_num))
        query_3 = 'INSERT INTO purchases VALUES(%s,%s,NULL,CURDATE())'
        cursor.execute(query_3,(str(new_id),username))
        query_4 = 'UPDATE flight SET seats_left = seats_left - 1 WHERE flight.airline_name=%s AND flight_num = %s'
        cursor.execute(query_4,(airline_name,flight_num))
        conn.commit()
        cursor.close()
        message='Purchase Complete'
        return render_template('purchase.html',message=message)
    else:
        message = 'Purchase Failure. No more seats for this flight'
        return render_template('purchase.html',message=message)

@app.route('/checkSpending', methods=['GET', 'POST'])
def checkSpending():
	username=session['username']
	cursor=conn.cursor()
	try:
		start_date=str(request.form['start_date'])+"-01"
		end_date=str(request.form['end_date'])+"-01"
	except:
		start_date = date.today().isoformat()[:-3]+"-01"
		end_date = (date.today()-timedelta(days=365)).isoformat()[:-3]+"-01"
	cursor = conn.cursor()
	query = 'SELECT sum(price)\
			FROM purchases NATURAL JOIN ticket NATURAL JOIN flight\
			WHERE custor_email = %s and purchase_date>=start_date\
			and purchase_date<DATE_ADD(end_date, INTERVAL 1 MONTH)'
	cursor.execute(query, username)
	total_spending = cursor.fetchone()
	cur_y=int(start_date[4:])
	cur_m=int(start_date[5:7])
	end_y=int(end_date[4:])
	end_m=int(end_date[5:7])
	end_m+=1;
	if end_m>12:
		end_m=1;
		end_y+=1;
	data=[]
	while (cur_y!=end_y or cur_m!=end_m):
		start_date = date(cur_y, cur_m, 1).isoformat()
		end_date = date(cur_y, cur_m, 1).isoformat()
		query = 'SELECT sum(price)\
				FROM purchases NATURAL JOIN ticket NATURAL JOIN flight\
				WHERE custor_email = %s and purchase_date>=start_date\
				and purchase_date<DATE_ADD(end_date, INTERVAL 1 MONTH)'
		cursor.execute(query, username)
		cur_spending = cursor.fetchone()
		if cur_spending==None:
			cur_spending=0;
		data.append([start_date[:-3], cur_spending])
		cur_m+=1
		if cur_m>12:
			cur_m=1
			cur_y+=1
	print(start_month, end_month)
	return render_template('chart.html', total_spending=total_spending, data=data)

@app.route('/logout')
def logout():
	session.pop('username')
	session.pop('type')
	return redirect('/')

app.secret_key = 'some key that you will never guess'

if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)
