# utils/db_utils.py

import pyodbc
from config import AzureSQLConfig
from datetime import datetime, timezone
# int(datetime.now(timezone.utc).timestamp())
# Helper function to handle database connections
def getDbConnection():
    return pyodbc.connect(AzureSQLConfig.connectionString)

# Helper function to execute a query with error handling
def execute_query(query, params=(), fetchone=False, fetchall=False, commit=False, commitLog=False):
    connection = getDbConnection()
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query, params)
        if fetchone:
            result = cursor.fetchone()
        elif fetchall:
            result = cursor.fetchall()
        if commit:
            connection.commit()
    except pyodbc.Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()
    return result

# User Management
def createUser(name, userID, hashedPassword):
    query = """
        INSERT INTO users (userID, name, hashed_password, credits, tokens, tokensHold) 
        VALUES (?, ?, ?, 100000, 100000, 0)
    """
    execute_query(query, (userID, name, hashedPassword), commit=True)

def getUserByUserID(userID):
    query = "SELECT * FROM users WHERE userID = ?"
    row = execute_query(query, (userID,), fetchone=True)
    if row:
        return {'userID': row[0], 'name': row[1], 'hashed_password': row[2], 'credits': row[3], 'tokens': row[4], 'tokensHold': row[5]}
    return None

def getUserCreditsTokens(userID):
    query = "SELECT credits, tokens, tokensHold FROM users WHERE userID = ?"
    row = execute_query(query, (userID,), fetchone=True)
    if row:
        return row[0], row[1], row[2]
    return 0, 0, 0

def updateCreditsAndTokens(user, credits, tokens):
    query = "UPDATE users SET credits = ?, tokens = ? WHERE userID = ?"
    execute_query(query, (credits, tokens, user), commit=True)

# Bid Management
def loadAllBids():
    query = """
        SELECT b.bidID, b.baseBid, b.highestBid, b.highestBidder, i.title, i.description, i.currentOwner
        FROM bidQueue b
        JOIN inventory i ON b.itemID = i.itemID
        ORDER BY b.bidID DESC
    """
    rows = execute_query(query, fetchall=True)
    return [{'bidID': row[0], 'baseBid': row[1], 'highestBid': row[2], 'highestBidder': row[3], 'title': row[4], 'description': row[5], 'currentOwner': row[6]} for row in rows]

def checkForNewBids(fromWhatTime):
    query = """
        SELECT b.bidID, b.baseBid, b.highestBid, b.highestBidder, i.title, i.description, i.currentOwner
        FROM bidQueue b
        JOIN inventory i ON b.itemID = i.itemID
        WHERE b.bidID > ?
        ORDER BY b.bidID DESC
    """
    rows = execute_query(query, (fromWhatTime,), fetchall=True)
    return [{'bidID': row[0], 'baseBid': row[1], 'highestBid': row[2], 'highestBidder': row[3], 'title': row[4], 'description': row[5], 'currentOwner': row[6]} for row in rows]

def loadAllUserBids():
    query = """
        SELECT bidQueueID, userID, bidID, bidAmount, bidTime
        FROM allBids
        ORDER BY bidQueueID DESC
    """
    rows = execute_query(query, fetchall=True)
    return [{'bidQueueID': row[0], 'userID': row[1], 'bidID': row[2], 'bidAmount': row[3], 'bidTime': row[4]} for row in rows]

def checkForNewUserBids(fromWhatTime):
    query = """
        SELECT bidQueueID, userID, bidID, bidAmount, bidTime
        FROM allBids
        WHERE bidTime > ?
        ORDER BY bidQueueID DESC
    """
    rows = execute_query(query, (fromWhatTime,), fetchall=True)
    return [{'bidQueueID': row[0], 'userID': row[1], 'bidID': row[2], 'bidAmount': row[3], 'bidTime': row[4]} for row in rows]

def getBidById(bidID):
    query = "SELECT * FROM bidQueue WHERE bidID = ?"
    row = execute_query(query, (bidID,), fetchone=True)
    if row:
        return {
            'bidID': row[0],
            'itemID': row[1],
            'baseBid': row[2],
            'highestBid': row[3],
            'highestBidder': row[4],
            'isEnded': row[5],
        }
    return None

def updateBid(bidID, amount, highestBidder):
    query = "UPDATE bidQueue SET highestBid = ?, highestBidder = ? WHERE bidID = ?"
    execute_query(query, (amount, highestBidder, bidID), commit=True)


# User  Bids Management
def checkUserBid(user, bidID):
    query = """
        SELECT bidAmount FROM allBids
        WHERE userID = ? AND bidID = ?
    """
    result = execute_query(query, (user, bidID), fetchone=True)
    return result[0] if result else 0

def deductTokens(userID, amount):
    query = "UPDATE users SET tokens = tokens-?, tokensHold = tokensHold+? WHERE userID = ?"
    execute_query(query, (amount, amount, userID), commit=True)

# All User Bids Management
def addNewUserBid(bidQueueID, userID, bidID, bidAmount, bidTime):
    query = """
        INSERT INTO allBids (bidQueueID, userID, bidID, bidAmount, bidTime) 
        VALUES (?, ?, ?, ?, ?)
    """
    execute_query(query, (bidQueueID, userID, bidID, bidAmount, bidTime), commit=True)

def updateUserBid(userID, bidID, bidAmount, bidTime):
    query = """
        UPDATE allBids
        SET bidAmount = ?, bidTime = ?
        WHERE userID = ? AND bidID = ?
    """
    execute_query(query, (bidAmount, bidTime, userID, bidID), commit=True)

# Add Bids, Items and Inventory
def addToInventory(itemID, title, description, currentOwner):
    query = """
        INSERT INTO inventory (itemID, title, description, currentOwner) 
        VALUES (?, ?, ?, ?)
    """
    execute_query(query, (itemID, title, description, currentOwner), commit=True)

def loadInventoryFor(userID):
    query = """
        SELECT * FROM inventory
        WHERE currentOwner = ?
        ORDER BY itemID DESC
    """
    rows = execute_query(query, (userID,), fetchall=True)
    return [{'itemID': row[0], 'title': row[1], 'description': row[2], 'currentOwner': row[3]} for row in rows]

def addToBidQueue(bidID, itemID, baseBid):
    query = """
        INSERT INTO bidQueue (bidID, itemID, baseBid, isEnded) 
        VALUES (?, ?, ?, 0)
    """
    execute_query(query, (bidID, itemID, baseBid), commit=True)
