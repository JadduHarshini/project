from flask import Flask,request,redirect,render_template,url_for,flash,session,send_file
from flaskext.mysql import MySQL
from flask_session import Session
from otp import genotp
from cmail import sendmail
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from tokenreset import token
import io
from io import BytesIO
import stripe
import os
import random
import cryptography
app=Flask(__name__)
app.secret_key='*#$harshaaaa'
app.config['SESSION_TYPE']='filesystem'
stripe.api_key='sk_test_51N13KRSGtFpV7higsDgxbb3dcjLx0ZGlM21LvQeHTXn4uLJTzL7p7Gs5sbwKOIoa1lmZow4OSoSmgNMhoUa0l3tI00AtC2YCP5'
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']='admin'
app.config['MYSQL_DATABASE_DB']='ECOMMERCE'
Session(app)
mysql=MySQL(app)
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/shome')
def home():
    return render_template('homepage.html')
@app.route('/homepage/<category>')
def homepage(category):
    cursor=mysql.get_db().cursor()
    cursor.execute("select * from additems where category=%s",[category])
    items=cursor.fetchall()
    print(items)
    return render_template('dashboard.html',items=items)
@app.route('/adminsignup',methods=['GET','POST'])
def adminsignup():
    if request.method=='POST':
        name=request.form['name']
        password=request.form['password']
        email=request.form['email']
        cursor=mysql.get_db().cursor()
        # check if the email already exists
        cursor.execute('SELECT COUNT(*) FROM admins WHERE email = %s', [email])
        count = cursor.fetchone()[0]
        if count > 0:
            flash('Email id already exists')
            return render_template('adminsignup.html')
        # insert the admin details
        else:
            cursor.execute('INSERT INTO admins VALUES (%s,%s,%s)',[name,password,email])
            mysql.get_db().commit()
            cursor.close()
            flash("Admin account created successfully")
            return render_template('adminsignup.html')
    return render_template('adminsignup.html')
@app.route('/adminlogin',methods=['GET','POST'])
def adminlogin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.get_db().cursor()
        cursor.execute('SELECT COUNT(*) FROM admins WHERE email = %s AND password = %s', [email, password])
        count = cursor.fetchone()[0]
        if count == 0:
            flash('Invalid email or password')
            return render_template('adminlogin.html')
        else:
            session['admin']=email
            return redirect(url_for('admindashboard'))
    return render_template('adminlogin.html')
@app.route('/adminforgot',methods=['GET','POST'])
def adminforget():
    if request.method=='POST':        
        email=request.form['email']
        cursor=mysql.get_db().cursor()
        cursor.execute('select email from admins')
        data=cursor.fetchall()
        if (email,) in data:
            cursor.execute('select email from admins where email=%s',[email])
            data=cursor.fetchone()[0]
            cursor.close()
            subject='Reset Password for FastShop Login'
            body=f'Reset the passwword using -{request.host+url_for("admincreatepassword",atoken=token(email,360))}'
            sendmail(data,subject,body)
            flash('Reset link sent to your mail')
            return redirect(url_for('adminlogin'))
        else:
            return 'Invalid user id' 
    return render_template('adminforgot.html')
@app.route('/admincreatepassword/<atoken>',methods=['GET','POST'])
def admincreatepassword(atoken):
    try:
        s=Serializer(app.config['SECRET_KEY'])
        email=s.loads(atoken)['user']
        if request.method=='POST':
            npass=request.form['npassword']
            cpass=request.form['cpassword']
            if npass==cpass:
                cursor=mysql.get_db().cursor(buffered=True)
                cursor.execute('update admin set password=%s where email=%s',[npass,email])
                mysql.get_db().commit()
                cursor.close()
                return 'Password canged successfully'
            else:
                return 'Written password was mismatched'
        return render_template('adminnewpassword.html')
    except:
        return 'Link expired start over again'
    else:
        return redirect(url_for('login'))
@app.route('/admindashboard')
def admindashboard():
    if session.get('admin'):
        return render_template('admindashboard.html')
    else:
        flash('Login to access dashboard')
        return redirect(url_for('adminlogin'))
@app.route('/adminlogout')
def adminlogout():
    if session.get('admin'):
        session.pop('admin')
        return redirect(url_for('adminlogin'))
    else:
        flash('already signed off!')
        return redirect(url_for('adminlogin'))
@app.route('/additems',methods=['GET','POST'])
def additems():
    if request.method=="POST":
        name=request.form['name']
        discription=request.form['desc']
        qty=request.form['qty']
        price=request.form['price']
        category=request.form['category']
        image=request.files['image']
        cursor=mysql.get_db().cursor()
        id=genotp()
        filename=id+'.jpg'
        cursor.execute('insert into additems(itemid,name,discription,qty,price,category) values(%s,%s,%s,%s,%s,%s)',[id,name,discription,qty,price,category])
        mysql.get_db().commit() 
        print(filename)
        path=r"C:\Users\lenovo\Desktop\project\static"
        image.save(os.path.join(path,filename))
        print('success')
    return render_template('additems.html')
@app.route('/itemstatus')
def itemstatus():
        cursor = mysql.get_db().cursor()
        cursor.execute('select itemid,name, discription,qty,category,price from additems')
        items = cursor.fetchall()
        print(items)
        return render_template('itemstatus.html',items=items)
@app.route('/signup',methods=['GET','POST']) 
def signup():
    if request.method=='POST':
        name=request.form['name']
        mobile=request.form['mobile']
        password=request.form['password']
        email=request.form['email']
        gender=request.form['gender']
        address=request.form['address']
        cursor=mysql.get_db().cursor()
        cursor.execute('select name from users')
        data=cursor.fetchall()
        cursor.execute('SELECT email from users')
        edata=cursor.fetchall()
        if (email,) in edata:
            flash('Email id already exists')
            return render_template('signup.html')
        cursor.close()
        otp=genotp()
        subject='Thanks for registering to the application'
        body=f'Use this otp to register {otp}'
        sendmail(email,subject,body)
        return render_template('otp.html',otp=otp,name=name,mobile=mobile,password=password,email=email,gender=gender,address=address)
    else:
        flash('Invalid email')
        return render_template('signup.html')
    return render_template('signup.html')
@app.route('/dashboard/')
def dashboard():
    cursor=mysql.get_db().cursor()
    cursor.execute("select * from additems")
    items=cursor.fetchall()
    print(items)
    return render_template('homepage.html',items=items)
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        print(request.form)
        name=request.form['name']
        password=request.form['password']
        cursor=mysql.get_db().cursor()
        cursor.execute('select count(*) from users where name=%s and password=%s',[name,password])
        count=cursor.fetchone()[0]
        if count==0:
            print(count)
            flash('Invalid Password')
            return render_template('login.html')
        else:
            session['user']=name
            if not session.get(session.get('user')):
                session[session.get('user')]={}
            return redirect(url_for('dashboard'))
    return render_template('login.html')
@app.route('/forgetpassword',methods=['GET','POST'])
def forget():
    if request.method=='POST':
        email=request.form['email']
        cursor=mysql.get_db().cursor()
        cursor.execute('select email from users')
        data=cursor.fetchall()
        if (email,) in data:
            cursor.execute('select email from users where email=%s',[email])
            data=cursor.fetchone()[0]
            cursor.close()
            subject='Reset Password for {data}'
            body=f'Reset the Password using-{request.host+url_for("createpassword",token=token(email,360))}'
            sendmail(data,subject,body)
            flash('Reset link sent to your mail')
            return redirect(url_for('login'))
        else:
            return 'Invalid user name'
    return render_template('forgot.html')
@app.route('/otp/<otp>/<name>/<mobile>/<password>/<email>/<gender>/<address>',methods=['GET','POST'])
def otp(otp,name,mobile,password,email,gender,address):
    if request.method=='POST':
        uotp=request.form['otp']
        if otp==uotp:
            cursor=mysql.get_db().cursor()
            lst=[name,mobile,password,email,gender,address]
            query='insert into users values(%s,%s,%s,%s,%s,%s)'
            cursor.execute(query,lst)
            mysql.get_db().commit()
            cursor.close()
            flash('Details Registered')
            return redirect(url_for('login'))
        else:
            flash('Wrong OTP')
            return render_template('otp.html',otp=otp,name=name,mobile=mobile,password=password,email=email,gender=gender,address=address)
    return redirect(url_for('homepage'))


@app.route('/logout')
def logout():
    if session.get('user'):
        session.pop('user')
        return render_template('index.html')

    else:
        flash('already logged out')        
        return redirect(url_for('login'))
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
                cursor.execute('update users set password=%s where mobile=%s',[npass,mobile])
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
@app.route('/updateitems/<itemid>', methods=['GET','POST'])
def updateitems(itemid):
    if session.get('admin'):
        cursor = mysql.get_db().cursor()
        cursor.execute('select name,discription,qty,price,category from additems where itemid=%s', [itemid])
        items = cursor.fetchone()
        cursor.close()
        if request.method == 'POST':
            name = request.form['name']
            discription = request.form['desc']
            qty = request.form['qty']
            price = request.form['price']
            category = request.form['category']
            cursor=mysql.get_db().cursor()
            cursor.execute('update additems set name=%s, discription=%s, qty=%s, price=%s, category=%s where itemid=%s', [name,discription,qty,price,category,itemid])
            mysql.get_db().commit()
            cursor.close()
            flash('Item updated successfully')
            return redirect(url_for('itemstatus'))
        return render_template('updateitems.html', items=items)
    else:
        return redirect(url_for('itemstatus'))
@app.route('/deleteitems/<itemid>')
def delete(itemid):
    cursor=mysql.get_db().cursor()
    cursor.execute('delete from additems where itemid=%s',[itemid])
    mysql.get_db().commit()
    cursor.close()
    flash('items deleted successfully')
    return redirect(url_for('itemstatus'))   
@app.route('/itemspage')
def itemspage():
    cursor=mysql.get_db().cursor()
    cursor.execute('select * from additems')
    items=cursor.fetchall()
    print(items)
    return render_template('itemspage.html',items=items)
@app.route('/cart/<itemid>/<name>/<price>')
def cart(itemid,name,price):
    if not session.get('user'):
        return redirect(url_for('login'))
    print(session.get('user'))
    if itemid not in session[session.get('user')]:
        session[session.get('user')][itemid]=[name,1,price]
        session.modified=True
        print(session[session.get('user')])
        flash('{name} added to cart')
        return redirect(url_for('viewcart'))
    session[session.get('user')][itemid][1]+=1
    flash('Item already in cart  quantity increased to +1')
    return redirect(url_for('viewcart'))
@app.route('/viewcart')
def viewcart():
    if not session.get('user'):
        return redirect(url_for('login'))
    items=session.get(session.get('user')) if session.get(session.get('user')) else 'empty'
    print(items)
    if items=='empty':
        return 'no products in cart'
    return render_template('cart.html',items=items)
@app.route('/remcart/<item>')
def rem(item):
    if session.get('user'):
        session[session.get('user')].pop(item)
        return redirect(url_for('viewcart'))
    return(redirect(url_for('login')))
@app.route('/itemdetails/<itemid>')
def itemdetails(itemid):
    cursor=mysql.get_db().cursor()
    cursor.execute('select * from additems where itemid=%s',[itemid])
    items=cursor.fetchall()
    print(items)
    return render_template('itemdetails.html',items=items)
@app.route('/pay/<itemid>/<name>/<int:price>',methods=['POST'])
def pay(itemid,name,price):
    if session.get('user'):
        q=int(request.form['qty'])
        name=session.get('user')
        total=price*q
        checkout_session=stripe.checkout.Session.create(
            success_url=url_for('success',itemid=itemid,name=name,q=q,total=total,_external=True),
            line_items=[
                {
                    'price_data': {
                        'product_data': {
                            'name': name,
                        },
                        'unit_amount': price*100,
                        'currency': 'inr',
                    },
                    'quantity': q,
                },
                ],
            mode="payment",)
        return redirect(checkout_session.url)
    else:
        return redirect(url_for('login'))
@app.route('/success/<itemid>/<name>/<q>/<total>')
def success(itemid,name,q,total):
    if session.get('user'):
        cursor=mysql.get_db().cursor()
        cursor.execute('insert into orders(itemid,name,qty,total_price,mobile) values(%s,%s,%s,%s,%s)',[itemid,name,q,total,session.get('user')])
        mysql.get_db().commit()
        return redirect(url_for('orders'))
    return redirect(url_for('login'))
@app.route('/orderplaced')
def orders():
    if session.get('user'):
        cursor=mysql.get_db().cursor()
        cursor.execute('select * from orders where name=%s', (session['user'],))
        order=cursor.fetchall()
        mysql.get_db().commit()
        cursor.close()
        return render_template('order.html', order=order)
@app.route('/review /<itemid>', methods=['GET', 'POST'])
def addreview(itemid):
    if session.get('user'):
        if request.method == 'POST':
            print(request.form)
            name = session.get('user')
            title = request.form['title']
            desc = request.form['review']
            rate = request.form['rating']
            cursor = mysql.get_db().cursor()
            cursor.execute('INSERT INTO reviews(name, itemid, title, review, rating) VALUES(%s, %s, %s, %s, %s)', [name, itemid, title, desc, rate])
            mysql.get_db().commit()
        return render_template('addreview.html')
    else:
        return redirect(url_for('login'))
@app.route('/readreview/<itemid>')
def readreview(itemid):
     cursor=mysql.get_db().cursor()
     cursor.execute('select * from reviews where itemid=%s',[itemid])
     reviews=cursor.fetchall()
     return render_template('readreview.html',reviews=reviews)
@app.route('/search', methods=['GET','POST'])
def search():
    if request.method == 'POST':
        name = request.form['search']
        cursor = mysql.get_db().cursor()
        cursor.execute('SELECT * from additems where name=%s',[name])
        data= cursor.fetchall()
        return render_template('dashboard.html',items=data)
@app.route('/contactus',methods=['GET','POST'])
def contactus():
    if request.method=="POST":
        print(request.form)
        name=request.form['name']
        emailid=request.form['emailid']
        message=request.form['message']
        cursor=mysql.get_db().cursor()
        cursor.execute('insert into contactus(name,emailid,message) values(%s,%s,%s)',[name,emailid,message])
        mysql.get_db().commit()
    return render_template('contactus.html')
@app.route('/readcontactus')
def readcontactus():
    cursor=mysql.get_db().cursor()
    cursor.execute("select * from contactus ")
    contact=cursor.fetchall()
    return render_template('readcontact.html',contact=contact)
app.run(debug=True, use_reloader=True)
