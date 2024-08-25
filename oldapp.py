from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_bcrypt import Bcrypt
from config import AzureSQLConfig
from utils.db_utils import *
import re, os, pyodbc
from datetime import datetime, timezone

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(AzureSQLConfig)

# Initialize bcrypt for password hashing
bcrypt = Bcrypt(app)

# Home route
@app.route('/')
def index():
    if 'user' in session:
        session['credits'], session['tokens'], session['tokensHold'] = getUserCreditsTokens(session['email'])
        allBids = loadAllBids()
        timeStamp = allBids[0]["startTime"]
        return render_template("index.html", user=session['user'], userEmail=session['email'], credits=session['credits'], tokens=session['tokens'], tokensHold=session['tokensHold'], allBids=allBids, lastLoad=timeStamp)
    
    return redirect(url_for('login'))

@app.route('/placeBid', methods=['POST'])
def placeBid():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'User not logged in.'})

    data = request.get_json()
    userTokens = session['tokens']

    userID = session['email']
    bidID = data['bidId']
    bidAmount = data['amount']
    depositAmount = int(bidAmount*.75)
    bidTime = int(datetime.now(timezone.utc).timestamp())

    bid = getBidById(bidID)

    if bidAmount <= bid['highestBid']:
        return jsonify({'success': False, 'message': 'Bid must be higher than the current highest bid.'})

    if bidAmount > userTokens:
        return jsonify({'success': False, 'message': 'Not enough tokens.'})

    prevBidAmount = checkUserBid(session['email'], bidID)
    newAmount = bidAmount - prevBidAmount
    updateBid(bidID, bidAmount, session['email'])
    deductTokens(session['email'], newAmount)
    if prevBidAmount: updateUserBid(userID, bidID, bidAmount, depositAmount, bidTime)
    else: addNewUserBid(userID, bidID, bidAmount, depositAmount, bidTime)

    return jsonify({'success': True})

@app.route('/checkNewBids', methods=['GET'])
def checkNewBids():
    timestamp = request.args.get('timestamp', type=int)
    newBids = checkForNewBids(timestamp)
    if newBids: newTimestamp = newBids[0]["startTime"]
    else: newTimestamp = timestamp
    return jsonify({'newBids': newBids, 'newTimestamp': newTimestamp})


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

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
    # app.run()
