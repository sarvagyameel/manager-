from builtins import str
#import flask
from flask import Flask,render_template,request,redirect,url_for,flash,session
#import psycopg2 as psql
#import mail
import pandas as pd
import numpy as np
from forms import RegistrationForm,LoginForm
import os
from flask_wtf.file import FileField,FileAllowed
from passlib.hash import pbkdf2_sha256
#import sms
import random
from datetime import date
import pickle
import numpy as np
import shutil
import datetime





app = Flask(__name__)

app.config['SECRET_KEY'] = 'f5f907b5a9c962dd62e896f08c13a609'

#-------------------------------------------------
def dataret(email):
    cursor=conn.cursor()
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='userinfo'")
    list1 = [a[0] for a in cursor.fetchall()]
    cursor.execute(f"SELECT * FROM userinfo where email='{email}'")
    dict1 = dict(zip(tuple(list1), cursor.fetchone()))
    return dict1
#====================================================



posts = [
    {
        'author': 'Corey Schafer',
        'title': 'project 1',
        'content': 'First post content',
        'date_posted': 'April 20, 2018'
    },
    {
        'author': 'Jane Doe',
        'title': 'project 2',
        'content': 'Second post content',
        'date_posted': 'April 21, 2018'
    }
]


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route('/register',methods=['GET','POST'])
def register():
    session.pop('logged-in',False)
    session.pop('phone', False)
    form=RegistrationForm()
    if request.method=='POST':
        if form.validate_on_submit():
            cursor=conn.cursor()
            result=request.form.to_dict()
            result['email']=form.data['email'].lower()

            regdata=[]
            for key,value in result.items():
                if(key=='submit' or key=='cpassword' or key=='csrf_token'):
                    continue
                elif (key=='password'):
                    regdata.append(pbkdf2_sha256.hash(value))
                elif(key!='type'):
                    regdata.append(value)
                else:
                    if(value=='1'):
                        regdata.append(f"A-{result['email']}")
                    else:
                        regdata.append(f"E-{result['email']}")
            print(f"INSERT INTO USERINFO VALUES {tuple(regdata)}")

            try:
                print(f"INSERT INTO USERINFO VALUES {tuple(regdata)}")
                cursor.execute(f"INSERT INTO USERINFO VALUES {tuple(regdata)}")
                conn.commit()
            except psql.Error as e:

                flash(f"{e.diag.message_detail}","danger")
                cursor.execute("rollback;")
                return redirect(url_for('register'))
            else:
                form.image.data.save( os.path.join(os.getcwd(), 'static/media/profile_image', form.data['email'].lower()))
                if(result['type']=='2'):
                    return redirect(url_for('login'))
                else :

                    return redirect(url_for('choosedepartment',email=result['email']))     
        else:
            session['onetime']=True
            return render_template('register.html',form=form)
    else:
        return render_template('register.html', form=form)


@app.route('/department',methods=['GET','POST'])
def choosedepartment():
    if (not request.args.get('email')):
        return redirect(url_for('home'))
    if((not session['username'][0]=='E')  or session.get(onetime)==False):
        flash('URL NOT FOUND','danger')
        return redirect(url_for('profile'))
    email=request.args.get('email')
    if request.method=='POST':
         result=request.form.to_dict()
         department=result['department']
         cursor.execute(f"INSERT INTO dept VALUES {email},'d{int(department)}'")
         conn.commit()
         return redirect(url_for('login'))
        

    else:
        return render_template('dept.html',form=departmentForm())





@app.route('/login',methods=['GET','POST'])
def login():
    session.pop('logged-in',False)
    session.pop('phone',False)
    form=LoginForm()
    if(request.method == 'POST'):
        cursor=conn.cursor()
        result=form.data
        cursor.execute(f"Select passwordd from userinfo where lower(email)='{result['email'].lower()}'")
        a=cursor.fetchone()
        if a is None:
            flash(f"NO ACCOUNT EXISTS WITH THIS USERNAME",'danger')
            return redirect(url_for('register'))
        else:
            dict1 = dataret(result['email'].lower())
            if pbkdf2_sha256.verify(result['password'], a[0]):
                session['email']=result['email'].lower()
                session['logged-in']=True
                session['phone']=dict1['phone']
                session['list']=None
                session['state']=None
                session['up']=1


                session['username']=dict1['username']
                filt=session['username'][0].lower()
                srt=f"{filt}"+"home"
                return redirect(url_for(srt))

            else:
                flash("Incorrect Password!","danger")
                return render_template("login.html",form=form)
    else:

        return render_template('login.html',form=form)



if __name__ == '__main__':
    app.run(debug=True)