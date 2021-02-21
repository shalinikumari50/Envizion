from flask import Flask, session, redirect, url_for, request, render_template
import os
import pyrebase
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

'''
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import 
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin
'''

# flask
app = Flask(__name__)
app.secret_key = os.urandom(24)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///<table_name>.sqlite3'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#db = SQLAlchemy(app)


# pyrebase
firebaseConfig = {
  "apiKey": "AIzaSyDe8avmHiNkm4oOH9Ng3aNmjrU1_TAv4ts",
  "authDomain": "pearlhacks2021-envizion.firebaseapp.com",
  "databaseURL": "https://pearlhacks2021-envizion-default-rtdb.firebaseio.com",
  "projectId": "pearlhacks2021-envizion",
  "storageBucket": "pearlhacks2021-envizion.appspot.com",
  "messagingSenderId": "1060421957904",
  "appId": "1:1060421957904:web:13e79ec795b159a0dd0d95",
  "measurementId": "G-6TKLZLLKL6"
};
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
#db = firebase.database()
storage = firebase.storage()


# Cassandra Astra
cloud_config= {
        'secure_connect_bundle': 'secure-connect-PearlHacks2021-EnvizionDB.zip'
}
auth_provider = PlainTextAuthProvider('ardelysti', 'Ardelysti2021')
cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
cloud_sesh = cluster.connect()


@app.route('/login',methods=['GET','POST'])
def login():
    message = ""
    try:
        # check if user logged in
        user = session['user']
        return redirect(url_for('home'))
    except KeyError:
        # user not logged in/token expired
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['pass']
            try:
                user = auth.sign_in_with_email_and_password(email,password)
                user = auth.refresh(user['refreshToken'])
                user_id = user['idToken']
                session['user'] = user_id
                return redirect(url_for('home'))
                #return render_template('index.html',message=message)
            except:
                message = "Incorrect Password!"
        return render_template('index.html',message=message)

@app.route('/signup',methods=['GET','POST'])
def signup():
    successful = "Sign up Succes! Please login"
    unsuccessful = "Failed! Please try again"
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['pass']
        try:
            auth.create_user_with_email_and_password(email,password)
            return render_template('index.html',s=successful)
        except:
            return render_template('signup.html',us=unsuccessful)
    return render_template('signup.html')

@app.route('/user')
def user():
    try:
        print(session['user'])
        row = cloud_sesh.execute("select release_version from system.local").one()
        if row:
            return render_template('user.html',data=row[0])
        else:
            return render_template('user.html',data="Error occurred")
    except KeyError:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect(url_for('login'))

''' For Shalini's Stuff html '''

@app.route('/home')
def home():
    return render_template('home.html')

# @app.route('/index')
# def index():
#     return render_template('index.html')

@app.route('/post')
def post():
    return render_template('post.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/shop')
def shop():
    return render_template('shop.html')

@app.route('/askforhelp')
def askforhelp():
    return render_template('askforhelp.html')

if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))