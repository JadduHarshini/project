from flask import Flask,flash,redirect,request,url_for,render_template,session,send_file
from flask_session import Session
from flask_mysqldb import MySQL
from otp import genotp
import random
from io import BytesIO
app=Flask(__name__)
app.secret_key='anisha@2003'
app.config['SESSION_TYPE']='filesystem'
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='admin'
app.config['MYSQL_DB']='ECOMMERCE'
Session(app)
mysql=MySQL(app)
@app.route('/')
def home():
    return render_template('home.html')
@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method=='POST':
        name=request.form['name']
        password=request.form['password']
        email=request.form['email']
        cursor=mysql.connection.cursor()
        cursor.execute('select name from admin')
        data=cursor.fetchall()
        cursor.execute('SELECT email from admin')
        edata=cursor.fetchall()            
        if (email,) in edata:
            flash('Email id already exists')
            return render_template('signup.html')
        cursor.close()
        otp=genotp()
        sendmail(email,otp)
        return render_template('otp.html',otp=otp,name=name,password=password,email=email)
        return otp
    else:
        flash('Invalid email')
        return render_template('signup.html')
    return render_template('signup.html')
@app.route('/login',methods=['GET','POST'])
def login():
    if session.get('user'):
        return redirect(url_for('home'))
    if request.method=='POST':
        print(request.form)
        name=request.form['name']
        password=request.form['password']
        cursor=mysql.connection.cursor()
        cursor.execute('select count(*) from admin where name=%s and password=%s',[name,password])
        count=cursor.fetchone()[0]
        if count==0:
            print(count)
            flash('Invalid username or password')
            return render_template('login.html')
        else:
            session['user']=name
            return redirect(url_for('home'))
    return render_template('login.html')
@app.route('/home')
def homepage():
    if session.get('user'):
        return render_template('homepage.html')
    else:
        return redirect(url_for('login'))
@app.route('/forgetpassword',methods=['GET','POST'])
def forget():
    if request.method=='POST':
        name=request.form['name']
        cursor=mysql.connection.cursor()
        cursor.execute('select name from admin')
        data=cursor.fetchall()
        cursor.close()
        if(name,) in data:
            cursor.execute('select email from admin where name=%s',[name])
            data=cursor.fetchone()[0]
            cursor.close()
            session['pass']=name
            send_mail(data,subject='Reset password',body=f'Reset the password here-{request.base_url+"/"+url_for("createpassword")}')
        else:
            return 'Invalid user name'
    return render_template('forgot.html')
@app.route('/otp/<otp>/<name>/<password>/<email>',methods=['GET','POST'])
def otp(otp,name,password,email):
    if request.method=='POST':
        uotp=request.form['otp']
        if otp==uotp:
            cursor=mysql.connection.cursor()
            lst=[name,password,email]
            query='insert into admin values(%s,%s,%s)'
            cursor.execute(query,lst)
            mysql.connection.commit()
            cursor.close()
            flash('Details Registered')
            return redirect(url_for('login'))
        else:
            flash('Wrong OTP')
            return render_template('otp.html',otp=otp,name=name,password=password,email=email)
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    if session.get('user'):
        session.pop('user')
        return render_template('index')
    else:
        flash('already logged out')        
        return redirect(url_for('login'))


app.run(debug=True,use_reloader=True)
