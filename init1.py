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

	try:
		username=session['username'];
		usertype=session['type'];
		print(username, usertype)
		return render_template('search_results.html',result = data, type = usertype)
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
	arrival_date = str(request.form['arrival_date'])
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
	
	cursor = conn.cursor()
	query = 'SELECT * FROM booking_agent WHERE email = %s'
	cursor.execute(query, (username))
	data = cursor.fetchone()
	
	query_1 = 'SELECT MAX(booking_agent_id) FROM booking_agent'
	cursor.execute(query_1)
	data_1 = cursor.fetchone()
	if data_1==None:
		max_id=1
	else:
		max_id = data_1['MAX(booking_agent_id)']
	if (data):
		error = "This agent already exists"
		return render_template('register.html', error = error)
	else:
		ins = 'INSERT INTO booking_agent VALUES(%s,%s,%s)'
		cursor.execute(ins,(username,password,max_id))
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
                WHERE status = 'upcoming' AND customer_email = '%s'"%(username)
	else:
		query = "SELECT * FROM flight NATURAL JOIN ticket NATURAL JOIN purchases \
                WHERE customer_email = '%s' AND "%(username) + " AND ".join(control_list)

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
		end_date = date.today().isoformat()[:-3]+"-01"
		start_date = (date.today()-timedelta(days=365)).isoformat()[:-3]+"-01"
	if end_date<start_date:
		error = 'Invalid Input'
		return render_template('chart.html', error = error)
	cursor = conn.cursor()
	query = 'SELECT sum(price) as tot\
			FROM purchases NATURAL JOIN ticket NATURAL JOIN flight\
			WHERE customer_email = %s and purchase_date>=%s\
			and purchase_date<DATE_ADD(%s, INTERVAL 1 MONTH)'
	print(query%(username, start_date, end_date))
	cursor.execute(query, (username, start_date, end_date))
	total_spending = cursor.fetchone()
	total_spending = total_spending['tot']
	if total_spending==None:
		total_spending=0
	else:
		total_spending=int(total_spending)
	cur_y=int(start_date[:4])
	cur_m=int(start_date[5:7])
	end_y=int(end_date[:4])
	end_m=int(end_date[5:7])
	end_m+=1;
	if end_m>12:
		end_m=1;
		end_y+=1;
	data=[]
	label=[]
	while not (cur_y==end_y and cur_m==end_m):
		start_date = date(cur_y, cur_m, 1).isoformat()
		end_date = date(cur_y, cur_m, 1).isoformat()
		print(start_date, end_date)
		query = 'SELECT sum(price) as tot\
				FROM purchases NATURAL JOIN ticket NATURAL JOIN flight\
				WHERE customer_email = %s and purchase_date>=%s\
				and purchase_date<DATE_ADD(%s, INTERVAL 1 MONTH)'
		print(query%(username, start_date, end_date))
		cursor.execute(query, (username, start_date, end_date))
		cur_spending = cursor.fetchone()
		cur_spending = cur_spending['tot']
		if cur_spending==None:
			cur_spending=0;
		label.append(start_date[:7])
		data.append(int(cur_spending))
		cur_m+=1
		if cur_m>12:
			cur_m=1
			cur_y+=1
	print(total_spending, data)
	return render_template('chart.html', total_spending=total_spending, data=data, label=label, act='Spending')

@app.route('/purchaseA1/<airline_name>/<flight_num>',methods=['GET','POST'])
def purchaseA1(airline_name,flight_num):
	session['airline_name'] = airline_name
	session['flight_num'] = flight_num
	return render_template('purchase_agent.html')

@app.route('/purchaseA2',methods=['GET','POST'])
def purchaseA2():
	username_b = session['username']
	username_c = request.form['username']
	airline_name_1 = session['airline_name']
	flight_num_1 = session['flight_num']
	query_0 = 'SELECT email FROM customer WHERE email = %s'
	cursor = conn.cursor()
	cursor.execute(query_0,(username_c))
	data_0 = cursor.fetchone()
	if data_0 == None:
		error = 'Please provide valid information'
		return render_template('purchase_agent.html', error = error)
	query_1 = 'SELECT seats_left FROM flight WHERE airline_name = %s AND flight_num = %s'
	cursor.execute(query_1,(airline_name_1,flight_num_1))
	data_1 = cursor.fetchone()
	seats_left = int(data_1['seats_left'])
	if (seats_left < 1):
		message = 'Purchase Failure. No more seats for this flight'
		return render_template('purchase.html',message = message)
	query_2 = 'SELECT MAX(ticket_id) FROM ticket'
	cursor.execute(query_2)
	data_2 = cursor.fetchone()
	max = data_2['MAX(ticket_id)']
	if (max == None):
		new_id = 1
	else:
		new_id = int(max) + 1
	query_3 = 'INSERT INTO ticket VALUES(%s,%s,%s)'
	cursor.execute(query_3,(str(new_id),airline_name_1,flight_num_1))
	query_4 = 'SELECT booking_agent_id FROM booking_agent WHERE email = %s'
	cursor.execute(query_4,(username_b))
	data_4 = cursor.fetchone()
	b_id = str(data_4['booking_agent_id'])
	query_5 = 'INSERT INTO purchases VALUES(%s,%s,%s,CURDATE())'
	cursor.execute(query_5,(str(new_id),username_c,b_id))
	query_6 = 'UPDATE flight SET seats_left = seats_left - 1 WHERE airline_name =%s AND flight_num=%s'
	cursor.execute(query_6,(airline_name_1,flight_num_1))
	conn.commit()
	cursor.close()
	message = 'Purchase Complete'
	session.pop('airline_name')
	session.pop('flight_num')
	return render_template('purchase.html',message=message)

@app.route('/viewMyFlightAgent', methods=['GET', 'POST'])
def viewMyFlightAgent():
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
        control_list.append("DATE(departure_time)>'%s'"%(start_date))
    if end_date!='':
        control_list.append("DATE(arrival_time)<'%s'"%(end_date))
    cursor = conn.cursor()
    query_0 = 'SELECT booking_agent_id FROM booking_agent WHERE email = %s'
    cursor.execute(query_0,(username))
    data_0 = cursor.fetchone()
    booking_agent_id = data_0['booking_agent_id']

    if len(control_list) == 0:
        query_1 = "SELECT * FROM flight NATURAL JOIN ticket NATURAL JOIN purchases \
        WHERE status = 'upcoming' AND booking_agent_id = '%s'"%(booking_agent_id)
    else:
        query_1 ="SELECT * FROM flight NATURAL JOIN ticket NATURAL JOIN purchases \
        WHERE booking_agent_id = '%s' AND "%(booking_agent_id) + " AND ".join(control_list)
    cursor.execute(query_1)
    data_1 = cursor.fetchall()
    conn.commit()
    cursor.close()
    return render_template('search_results.html',result = data_1)

@app.route('/checkTop5', methods=['GET', 'POST'])
def checkTop5():
    username=session['username']
    cursor = conn.cursor()
    query_0 = 'SELECT booking_agent_id FROM booking_agent WHERE email = %s'
    cursor.execute(query_0,(username))
    data_0 = cursor.fetchone()
    b_id = data_0['booking_agent_id']
    end_date = date.today().isoformat()[:-3]+"-01"
    cur_y = date.today().year
    cur_m = date.today().month
    cur_m = cur_m - 5
    if (cur_m < 1):
        cur_y = cur_y - 1
        cur_m = cur_m + 12
    start_date = date(cur_y,cur_m,1).isoformat()
    query_1 = 'SELECT customer_email,COUNT(DISTINCT ticket_id) AS count FROM ticket NATURAL JOIN purchases \
            WHERE booking_agent_id = %s AND purchase_date >%s AND purchase_date < DATE_ADD(%s, INTERVAL 1 MONTH) \
            GROUP BY customer_email ORDER BY count DESC'
    cursor.execute(query_1,(str(b_id),start_date,end_date))
    data_1 = cursor.fetchall()[:5]
    data1=[]
    label1=[]
    for i in range(len(data_1)):
        data1.append(data_1[i]['count'])
        label1.append(data_1[i]['customer_email'])
    query_2 = 'SELECT customer_email, SUM(price)*0.1 AS commission FROM purchases NATURAL JOIN ticket NATURAL JOIN flight \
            WHERE booking_agent_id = %s AND purchase_date > %s AND purchase_date < DATE_ADD(%s, INTERVAL 1 MONTH) \
            GROUP BY customer_email ORDER BY commission DESC'
    cursor.execute(query_2,(str(b_id),start_date,end_date))
    data_2 = cursor.fetchall()[:5]
    data2=[]
    label2=[]
    for i in range(len(data_2)):
        data2.append(int(data_2[i]['commission']))
        label2.append(data_2[i]['customer_email'])
    print(data1)
    print(label1)
    print(data2)
    print(label2)
    return render_template('chartagent.html',data1 = data1, data2 = data2, label1 = label1, label2 = label2)

@app.route('/viewCommission', methods=['GET','POST'])
def viewCommission():
	username=session['username']
	cursor = conn.cursor()
	query_0 = 'SELECT booking_agent_id FROM booking_agent WHERE email = %s'
	cursor.execute(query_0,(username))
	data_0 = cursor.fetchone()
	b_id = data_0['booking_agent_id']
	try:
		start_date=str(request.form['start_date'])
		end_date=str(request.form['end_date'])
		if start_date>end_date:
			return render_template('commission.html', message=['wrong start or end date']);
		query = 'select sum(price)*0.1 as tot_commission\
				from purchases natural join ticket natural join flight\
				where booking_agent_id=%s and purchase_date>=%s and purchase_date<=%s';
		cursor.execute(query, (b_id, start_date, end_date))
		data = cursor.fetchone()
		commission = data['tot_commission']
		if commission==None:
			commission=0;
		query = 'select count(ticket_id) as tot_ticket\
				from purchases natural join ticket natural join flight\
				where booking_agent_id=%s and purchase_date>=%s and purchase_date<=%s';
		cursor.execute(query, (b_id, start_date, end_date))
		data = cursor.fetchone()
		ticket = data['tot_ticket']
		ans = ['Your total commission of this time period is %d'%(commission),
			   'Your total ticket sold of this time period is %d'%(ticket)];
		return render_template('commission.html', message=ans)
	except:
		start_date = (date.today()-timedelta(days=30)).isoformat()
		end_date = date.today().isoformat()
		print(start_date)
		print(end_date)
		query = 'select sum(price)*0.1 as tot_commission\
				from purchases natural join ticket natural join flight\
				where booking_agent_id=%s and purchase_date>=%s and purchase_date<=%s';
		cursor.execute(query, (b_id, start_date, end_date))
		data = cursor.fetchone()
		commission = data['tot_commission']
		if commission==None:
			commission=0;
		query = 'select count(ticket_id) as tot_ticket\
				from purchases natural join ticket natural join flight\
				where booking_agent_id=%s and purchase_date>=%s and purchase_date<=%s';
		cursor.execute(query, (b_id, start_date, end_date))
		data = cursor.fetchone()
		ticket = data['tot_ticket']
		if ticket!=0:
			commission = commission / ticket;
		ans = ['Your average commission per ticket of past 30 days is %.2f'%(commission),
			   'Your total ticket sold of past 30 days is %d'%(ticket)];
		return render_template('commission.html', message=ans)

@app.route('/viewMyFlightStaff', methods=['GET','POST'])
def viewMyFlightStaff():
    
    dept_airport = request.form['dept_airport']
    arr_airport = request.form['arr_airport']
    start_date = str(request.form['start_date'])
    end_date = str(request.form['end_date'])
    username = session['username']
    query_0 = 'SELECT airline_name FROM airline_staff WHERE username = %s'
    cursor = conn.cursor()
    cursor.execute(query_0,(username))
    data_0 = cursor.fetchone()
    airline_name = data_0['airline_name']
    control_list = []
    if dept_airport!='':
        control_list.append("departure_airport = '%s'"%(dept_airport))
    if arr_airport!='':
        control_list.append("arrival_airport = '%s'"%(arr_airport))
    if start_date!='':
        control_list.append("DATE(departure_time)>'%s'"%(start_date))
    if end_date!='':
        control_list.append("DATE(arrival_time)<'%s'"%(end_date))
    if len(control_list) == 0:
        query_1 = "SELECT * From flight WHERE airline_name = '%s' AND \
         DATE(departure_time) > CURDATE() AND \
         DATE(departure_time) < DATE_ADD(CURDATE(), INTERVAL 1 MONTH)"%(airline_name)
    else:
        query_1 = "SELECT * FROM flight WHERE airline_name = '%s' AND "%(airline_name) + " AND ".join(control_list)
    cursor.execute(query_1)
    data_1 = cursor.fetchall()
    conn.commit()
    cursor.close()
    return render_template('search_results.html',result = data_1)

@app.route('/createFlight' , methods=['GET','POST'])
def createFlight():

    dept_airport = request.form['dept_airport']
    arr_airport = request.form['arr_airport']
    dept_time_1 = request.form['dept_time_1']
    arr_time_1 = request.form['arr_time_1']
    flight_num = request.form['flight_num']
    price = request.form['price']
    airplane_id = request.form['airplane_id']
    if (dept_airport==''or arr_airport=='' or dept_time_1=='' or arr_time_1=='' or price=='' or airplane_id=='' or flight_num==''):
        message = 'Please provide all the information'
        return render_template('purchase.html',message = message)
    
    dept_time = dept_time_1[:10] + ' ' + dept_time_1[11:]
    dept_y = int(dept_time_1[:4])
    dept_m = int(dept_time_1[5:7])
    dept_d = int(dept_time_1[8:10])
    dept_date = date(dept_y,dept_m,dept_d)
    if (dept_date <= date.today()):
        message = 'Please Provide valid information'
        return render_template('purchase.html',message=message)
    arr_time = arr_time_1[:10] + ' ' + arr_time_1[11:]
    username = session['username']
    cursor = conn.cursor()
    query_0 = 'SELECT airline_name FROM airline_staff WHERE username = %s'
    cursor.execute(query_0,(username))
    data_0 = cursor.fetchone()
    airline_name =str(data_0['airline_name'])
    query_1 = 'SELECT seats FROM airplane WHERE airplane_id = %s AND airline_name = %s'
    cursor.execute(query_1,(airplane_id,airline_name))
    data_1 = cursor.fetchone()
    if data_1 == None:
        message = 'Please provide valid information'
        return render_template('purchase.html', message = message)
    seats_left = data_1['seats']
    query_2 = 'INSERT INTO flight VALUES(%s,%s,%s,%s,%s,%s,%s,"upcoming",%s,%s)'
    cursor.execute(query_2,(airline_name,flight_num,dept_airport,dept_time,arr_airport,arr_time,price,airplane_id,seats_left))
    conn.commit()
    cursor.close()
    message = 'Creation complete'
    return render_template('purchase.html',message = message)

@app.route('/logout')
def logout():
	session.pop('username')
	session.pop('type')
	return redirect('/')

app.secret_key = 'some key that you will never guess'

if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)
