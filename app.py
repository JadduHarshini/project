from flask import Flask, request, redirect, render_template, url_for, flash, session, send_file
import mysql.connector
from flask_session import Session
from otp import genotp
from cmail import sendmail
from otp import genotp
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from tokenreset import token
import io
from io import BytesIO
import os
app = Flask(__name__)
app.secret_key = '#$harshaaa'
app.config['SESSION_TYPE'] = 'filesystem'
db = os.environ['RDS_DB_NAME']
user = os.environ['RDS_USERNAME']
password = os.environ['RDS_PASSWORD']
host = os.environ['RDS_HOSTNAME']
mydb = mysql.connector.connect(host=host, user=user, password=password, db=db)
# mydb = mysql.connector.connect(host='localhost', user='root', password='admin', db='main_sample')
with mysql.connector.connect(host=host, user=user, password=password, db=db) as conn:
    cursor = conn.cursor()
    cursor.execute('create table if not exists items(item_id int primary key auto_increment,item_name char(30),qty int,status text,price int,category varchar(50))')
    cursor.execute('create table if not exists users(mobile_number varchar(10) primary key,username char(30),password varchar(16),email varchar(70) unique,address text,gender char(6))')
    cursor.execute('create table if not exists orders(ord_id int primary key auto_increment,mobile_number varchar(10),item_id int,qty int,price int,foreign key(mobile_number) references users(mobile_number),foreign key(item_id) references items(item_id))')
    cursor.execute('create table if not exists admin(username char(30),email varchar(70),password varchar(16),passcode int)')
Session(app)
@app.route('/')
def home():
    cursor=mydb.cursor()
    cursor.execute("select * from items")
    items=cursor.fetchall()
    return render_template('homepage.html',items=items)
@app.route('/admindashboard')
def admindashboard():
    return render_template('admindashboard.html')
@app.route('/adminsignup',methods=['GET','POST'])
def adminsignuop():
    if request.method=='POST':
        username=request.form['name']
        email=request.form['email']
        password=request.form['password']
        passcode=request.form['passcode']
        upasscode='52555'
        cursor=mydb.cursor(buffered=True)
        # check if the email already exists
        cursor.execute('SELECT COUNT(*) FROM admins WHERE email = %s', [email])
        count = cursor.fetchone()[0]
        if count > 0:
            flash('Email id already exists')
            return render_template('adminsignup.html')
        # check if the passcode matches
        elif upasscode != passcode:
            flash('Invalid passcode')
            return render_template('adminsignup.html')
        # insert the admin details
        else:
            cursor.execute('INSERT INTO admin VALUES (%s,%s,%s,%s)',[uname,email,password,passcode])
            mydb.commit()
            cursor.close()
            flash("Admin account created successfully")
            return render_template('adminsignup.html')
    return render_template('adminsignup.html')
@app.route('/adminlogin',methods=['GET','POST'])
def adminlogin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor = mydb.cursor(buffered=True)
        cursor.execute('SELECT COUNT(*) FROM admin WHERE email = %s AND password = %s', [email, password])
        count = cursor.fetchone()[0]
        if count == 0:
            flash('Invalid email or password')
            return render_template('login.html')
        else:
            session['user'] = email
            return redirect(url_for('admindash'))
    return render_template('adminlogin.html')
@app.route('/adminlogout')
def adminlogout():
    if session.get('user'):
        session.pop('user')
        return redirect(url_for('login'))
    else:
        flash('already signed off!')
        return redirect(url_for('adminlogin'))
@app.route('/additems',methods=['GET','POST'])
def additems():
    if request.method=="POST":
        name=request.form['name']
        discription=request.form['desc']
        quantity=request.form['qty']
        category=request.form['category']
        price=request.form['price']
        image=request.files['image']
        cursor=mydb.cursor()
        id1=genotp()
        filename=id1+'.jpg'
        cursor.execute('insert into additems(itemid,name,discription,qty,category,price) values(%s,%s,%s,%s,%s,%s)',[id1,name,discription,quantity,category,price])
        mydb.commit()
        
        print(filename)
        path=r"C:\Users\MY PC\Desktop\SPM\static"
        image.save(os.path.join(path,filename))
        print('success')
    return render_template('additems.html')
@app.route('/homepage/')
def homepage():
    cursor=mydb.get_db.cursor()
    cursor.execute("select * from additems")
    items=cursor.fetchall()
    return render_template('homepage.html',items=items)

        
        print(filename)
        path=r"C:\Users\mnsva\OneDrive\Desktop\mainproject\static"
        image.save(os.path.join(path,filename))
        print('success')
    return render_template('additems.html')
@app.route('/usignup', methods=['GET', 'POST'])
def Signup():
    if request.method == 'POST':
        name = request.form['name']
        mobile = request.form['mobile']
        password = request.form['password']
        email = request.form['email']
        gender = request.form['gender']
        address = request.form['useraddress']
        otp = genotp()
        session['mobile'] = mobile
            # Send OTP to user's email 
        subject='Thanks for registering to our onlinshopping FastShop'
        body=f'Use this otp to register {otp}'
        sendmail(email,subject,body)
            # insert into database
        cursor = mydb.cursor(buffered=True)
        cursor.execute('insert into users values(%s,%s,%s,%s,%s,%s)', ( name,mobile, password, email,gender,address))
        mydb.commit()
        cursor.close()
        flash('OTP sent successfully. Please enter the OTP to complete the registration process.')
        return redirect(url_for('otp'))
    return render_template('signup.html')
@app.route('/otp/<otp>/<name>/<password>/<email>',methods=['GET','POST'])
def otp(otp,name,password,email):
    if request.method=='POST':
        uotp=request.form['otp']
        if otp==uotp:
            cursor=mysql.get_db().cursor()
            lst=[name,password,email]
            query='insert into users values(%s,%s,%s,%s,%s)'
            cursor.execute(query,lst)
            mysql.get_db().commit()
            cursor.close()
            flash('Details Registered')
            return redirect(url_for('signup'))
        else:
            flash('Wrong OTP')
            return render_template('otp.html',otp=otp,name=name,password=password,email=email,gender=gender,address=address)
    return redirect(url_for('login'))
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        mobile = request.form['mobile']
        password = request.form['password']
        cursor = mydb.cursor(buffered=True)
        cursor.execute('SELECT COUNT(*) FROM users WHERE mobile_number = %s AND password = %s', [mobile, password])
        count = cursor.fetchone()[0]
        if count == 0:
            flash('Invalid mobile number or password')
            return render_template('login.html')
        else:
            session['user'] = mobile
            return render_template('homepage.html')
    return render_template('login.html')
@app.route('/logout')
def logout():
    if session.get('user'):
        session.pop('user')
        return redirect(url_for('login'))
    else:
        flash('already signed off!')
        return redirect(url_for('login'))
@app.route('/forgotpassword',methods=['GET','POST'])
def forget():
    if request.method=='POST':        
        mobile=request.form['mobile']
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select mobile_number from users')
        data=cursor.fetchall()
        if (mobile,) in data:
            cursor.execute('select email from users where mobile_number=%s',[mobile])
            data=cursor.fetchone()[0]
            cursor.close()
            subject='Reset Password for SmartShop Login'
            body=f'Reset the passwword using -{request.host+url_for("createpassword",token=token(mobile,120))}'
            sendmail(data,subject,body)
            flash('Reset link sent to your mail')
            return redirect(url_for('login'))
        else:
            return 'Invalid user id' 
    return render_template('forgotp.html')
@app.route('/createpassword/<token>',methods=['GET','POST'])
def createpassword(token):
    try:
        s=Serializer(app.config['SECRET_KEY'])
        mobile=s.loads(token)['user']
        if request.method=='POST':
            npass=request.form['npassword']
            cpass=request.form['cpassword']
            if npass==cpass:
                cursor=mydb.cursor(buffered=True)
                cursor.execute('update users set password=%s where mobile_number=%s',[npass,mobile])
                mydb.commit()
                cursor.close()
                return 'Password changed successfully'
            else:
                return 'Written password was mismatched'
        return render_template('newpassword.html')
    except:
        return 'Link expired start over again'
    else:
        return redirect(url_for('login'))
if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
