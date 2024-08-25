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
        elif commitLog:
            connection.commit()
            result = cursor.lastrowid
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
        SELECT * FROM bidQueue
        ORDER BY startTime DESC
    """
    rows = execute_query(query, fetchall=True)
    return [{'id': row[0], 'title': row[1], 'description': row[2], 'startTime': row[3], 'baseBid': row[4], 'highestBid': row[5], 'highestBidder': row[6]} for row in rows]

def checkForNewBids(fromWhatTime):
    query = """
        SELECT * FROM bidQueue
        WHERE startTime > ?
        ORDER BY startTime DESC
    """
    rows = execute_query(query, (fromWhatTime,), fetchall=True)
    return [{'id': row[0], 'title': row[1], 'description': row[2], 'startTime': row[3], 'baseBid': row[4], 'highestBid': row[5], 'highestBidder': row[6]} for row in rows]

def getBidById(bidID):
    query = "SELECT * FROM bidQueue WHERE id = ?"
    row = execute_query(query, (bidID,), fetchone=True)
    if row:
        return {
            'id': row[0],
            'title': row[1],
            'description': row[2],
            'startTime': row[3],
            'baseBid': row[4],
            'highestBid': row[5],
            'highestBidder': row[6]
        }
    return None

def updateBid(bidID, amount, highestBidder):
    query = "UPDATE bidQueue SET highestBid = ?, highestBidder = ? WHERE id = ?"
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
def addNewUserBid(userID, bidID, bidAmount, bidTime):
    query = """
        INSERT INTO allBids (userID, bidID, bidAmount, bidTime) 
        VALUES (?, ?, ?, ?)
    """
    execute_query(query, (userID, bidID, bidAmount, bidTime), commit=True)

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
    execute_query(query, (itemID, title, description, currentOwner), commitLog=True)

def addToBidQueue(bidID, itemID, baseBid):
    query = """
        INSERT INTO bidQueue (bidID, itemID, baseBid) 
        VALUES (?, ?, ?)
    """
    execute_query(query, (bidID, itemID, baseBid), commit=True)
