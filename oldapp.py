# Main application file
# app.py

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
from flask_bcrypt import Bcrypt
from config import AzureSQLConfig
from utils.db_utils import *
from utils.storage_utils import *
from utils.email_utils import sendOtpEmail
import re, os
import random

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(AzureSQLConfig)

# Initialize bcrypt for password hashing
bcrypt = Bcrypt(app)


# Home route
@app.route('/')
def index():
    if 'user' in session:
        session['credits'],session['tokens'] = getUserCreditsTokens(session['email'])
        allBids = loadAllBids()
        print(allBids)
        return render_template("index.html", user=session['user'], userEmail=session['email'], credits=session['credits'], tokens=session['tokens'], allBids=allBids)
    
    return redirect(url_for('login'))


# User Authentication
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        hashedPassword = bcrypt.generate_password_hash(password).decode('utf-8')

        if getUserByEmail(email):
            error = 'Email already registered. Please log in.'
            return render_template('register.html', error=error, name=name, email=email)
        
        createUser(name, email, hashedPassword)
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = getUserByEmail(email)
        if user and bcrypt.check_password_hash(user['hashed_password'], password):
            session['user'] = user['name']
            session['email'] = user['email']
            session['credits'] = user['credits']
            session['tokens'] = user['tokens']
            return redirect(url_for('index'))
        
        error = 'Invalid email or password. Please try again.'
        return render_template('login.html', error=error, email=email)
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# Password Recovery
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgotPassword():
    if request.method == 'POST':
        email = request.form['email']
        user = getUserByEmail(email)
        if user:
            otp = str(random.randint(1000, 9999))
            session['otp'] = otp
            session['email'] = email
            sendOtpEmail(email, otp)
            flash('An OTP has been sent to your email. Please check your inbox.', 'info')
            return redirect(url_for('resetPassword'))
        
        error = 'Email not found. Please try again.'
        return render_template('forgotPassword.html', error=error, email=email)

    return render_template('forgotPassword.html')

@app.route('/resetPassword', methods=['GET', 'POST'])
def resetPassword():
    if request.method == 'POST':
        otp = request.form['otp']
        newPassword = request.form['new_password']
        
        if otp == session.get('otp'):
            hashedPassword = bcrypt.generate_password_hash(newPassword).decode('utf-8')
            updatePassword(session['email'], hashedPassword)
            flash('Your password has been reset successfully.', 'success')
            session.pop('otp', None)
            session.pop('email', None)
            return redirect(url_for('login'))
        
        flash('Invalid OTP. Please try again.', 'danger')
    
    return render_template('resetPassword.html')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
    # app.run()
