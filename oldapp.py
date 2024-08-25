from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_bcrypt import Bcrypt
import urllib3
from config import AzureSQLConfig
from utils.db_utils import *
import re, os, pyodbc, json
from datetime import datetime, timezone
from collections import defaultdict

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(AzureSQLConfig)

# Initialize bcrypt for password hashing
bcrypt = Bcrypt(app)

def timeKyaHai():
    return int(datetime.now(timezone.utc).timestamp())
def getAndSetSessionTokens():
    session['credits'], session['tokens'], session['tokensHold'] = getUserCreditsTokens(session['userID'])
def convertToDict(thisData):
    grouped_data = defaultdict(list)
    for item in thisData:
        bidID = item['bidID']
        grouped_data[bidID].append(item)
    return dict(grouped_data)

# Home route
@app.route('/')
def index():
    if 'user' in session:
        getAndSetSessionTokens()
        allBids = loadAllBids()
        currentTime = timeKyaHai()
        allUserBids = loadAllUserBids()
        timeStamp0 = allBids[0]["bidID"] if allBids else currentTime
        timeStamp1 = allUserBids[0]["bidQueueID"] if allUserBids else currentTime
        # timeStamp1 = allUserBids[0]["bidID"]
        allUserBids = convertToDict(allUserBids)
        allUserBids = removeDuplicatesAndSort(allUserBids)
        return render_template("index.html", user=session['user'], userEmail=session['userID'], credits=session['credits'], tokens=session['tokens'], tokensHold=session['tokensHold'], allBids=allBids, lastLoad0=timeStamp0, lastLoad1=timeStamp1, allUserBids=allUserBids)
    
    return redirect(url_for('login'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        baseBid = request.form['baseBid']
        currentTime = timeKyaHai()
        addToInventory(currentTime, title, description, session['userID'])
        addToBidQueue(currentTime, currentTime, baseBid)
        return redirect(url_for('admin'))
    
    return render_template('admin.html')

@app.route('/convertCreditsToTokens', methods=['POST'])
def convertCreditsToTokens():
    data = request.json
    credits = data.get('credits')
    tokens = data.get('tokens')

    if credits < 3 or tokens <= 0:
        return jsonify({'success': False, 'message': 'Invalid credits or tokens'})
    
    # Check if user has enough credits
    if credits > session['credits']:
        return jsonify({'success': False, 'message': 'Insufficient credits.'})

    newCredits = session['credits'] - credits 
    newTokens = session['tokens'] + tokens 
    updateCreditsAndTokens(session['userID'], newCredits, newTokens)

    return jsonify({
        'success': True,
        'newCredits': newCredits,
        'newTokens': newTokens,
    })

@app.route('/placeBid', methods=['POST'])
def placeBid():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'User not logged in.'})

    data = request.get_json()
    userTokens = session['tokens']

    userID = session['userID']
    bidID = data['bidId']
    bidAmount = data['amount']
    baseBid = data['baseBid'].split("$")[-1].strip()
    highestBid = data['highestBid'].split("$")[-1].strip()
    currentTime = timeKyaHai()

    if "No bids" in highestBid: highestBid = int(baseBid)
    else: highestBid = int(highestBid)

    # bid = getBidById(bidID)

    if bidAmount <= int(highestBid):
        return jsonify({'success': False, 'message': 'Bid must be higher than the current highest bid.'})
    if bidAmount > userTokens:
        return jsonify({'success': False, 'message': 'Not enough tokens.'})

    prevBidAmount = checkUserBid(session['userID'], bidID)
    newAmount = bidAmount - prevBidAmount
    updateBid(bidID, bidAmount, session['userID'])
    deductTokens(session['userID'], newAmount)
    if prevBidAmount:
        updateUserBid(userID, bidID, bidAmount, currentTime)
        print("Updated Current")
    else:
        addNewUserBid(currentTime, userID, bidID, bidAmount, currentTime)
        print("Created New")

    # Update session variables
    getAndSetSessionTokens()
    credits = session['credits']
    tokens = session['tokens']
    tokensHold = session['tokensHold']

    return jsonify({
        'success': True,
        'newAmount': newAmount,
        'credits': credits,
        'tokens': tokens,
        'tokensHold': tokensHold
    })

def mergeTheBids(userBids, oldUserBits):
    oldUserBits = {int(k): v for k, v in oldUserBits.items()}
    for key, bids in oldUserBits.items():
        if key in userBids:
            userBids[key].extend(bids)
        else:
            userBids[key] = bids

    return userBids


def removeDuplicatesAndSort(bids):
    for bidID, bid_list in bids.items():
        unique_bids = {}
        for bid in bid_list:
            key = (bid['userID'], bid['bidAmount'])
            if key not in unique_bids:
                unique_bids[key] = bid
        bids[bidID] = sorted(unique_bids.values(), key=lambda x: x['bidTime'], reverse=True)

    return bids

@app.route('/checkNewBids', methods=['GET', 'POST'])
def checkNewBids():
    timestamp0 = request.args.get('timestamp0', type=int)
    newBids = checkForNewBids(timestamp0)
    newTimestamp0 = newBids[0]["bidID"] if newBids else timestamp0

    timestamp1 = request.args.get('timestamp1', type=int)
    userBids = checkForNewUserBids(timestamp1)
    newTimestamp1 = userBids[0]["bidQueueID"] if userBids else timestamp1
    userBids = convertToDict(userBids)

    oldUserBits = request.args.get('tempUserBids', type=str)
    if oldUserBits:
        oldUserBits = json.loads(oldUserBits)
        oldUserBits = {int(k): v for k, v in oldUserBits.items()}
    else:
        oldUserBits = {}

    # Merge userBids with oldUserBits
    mergedBids = mergeTheBids(userBids, oldUserBits)
    print(1,1,1, mergedBids)
    mergedBids = removeDuplicatesAndSort(mergedBids)
    print(mergedBids)

    return jsonify({
        'newBids': newBids,
        'allUserBids': mergedBids,
        'newTimestamp0': newTimestamp0,
        'newTimestamp1': newTimestamp1
    })
# User Authentication
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['userID']
        password = request.form['password']
        hashedPassword = bcrypt.generate_password_hash(password).decode('utf-8')

        if getUserByUserID(email):
            error = 'Email already registered. Please log in.'
            return render_template('register.html', error=error, name=name, email=email)
        
        createUser(name, email, hashedPassword)
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['userID']
        password = request.form['password']
        
        user = getUserByUserID(email)
        if user and bcrypt.check_password_hash(user['hashed_password'], password):
            session['user'] = user['name']
            session['userID'] = user['userID']
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
