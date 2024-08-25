# utils/db_utils.py

import pyodbc
from config import AzureSQLConfig
from datetime import datetime, timezone

# Helper function to handle database connections
def getDbConnection():
    return pyodbc.connect(AzureSQLConfig.connectionString)

# Helper function to execute a query with error handling
def execute_query(query, params=(), fetchone=False, fetchall=False, commit=False):
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
def createUser(name, email, hashedPassword):
    query = """
        INSERT INTO users (email, name, hashed_password, credits, tokens) 
        VALUES (?, ?, ?, 100, 0)
    """
    execute_query(query, (email, name, hashedPassword), commit=True)

def getUserByEmail(email):
    query = "SELECT * FROM users WHERE email = ?"
    row = execute_query(query, (email,), fetchone=True)
    if row:
        return {'email': row[0], 'name': row[1], 'hashed_password': row[2], 'credits': row[3], 'tokens': row[4]}
    return None

def getUserCreditsTokens(email):
    query = "SELECT credits, tokens FROM users WHERE email = ?"
    row = execute_query(query, (email,), fetchone=True)
    if row:
        return row[0], row[1]
    return 0, 0

# Bid Management
def loadAllBids():
    query = """
        SELECT * FROM bidItems
        ORDER BY startTime DESC
    """
    rows = execute_query(query, fetchall=True)
    return [{'id': row[0], 'title': row[1], 'description': row[2], 'startTime': row[3], 'baseBid': row[4], 'highestBid': row[5], 'highestBidder': row[6]} for row in rows]

def checkForNewBids(fromWhatTime):
    query = """
        SELECT * FROM bidItems
        WHERE startTime > ?
        ORDER BY startTime DESC
    """
    rows = execute_query(query, (fromWhatTime,), fetchall=True)
    return [{'id': row[0], 'title': row[1], 'description': row[2], 'startTime': row[3], 'baseBid': row[4], 'highestBid': row[5], 'highestBidder': row[6]} for row in rows]

def getBidById(bidID):
    query = "SELECT * FROM bidItems WHERE id = ?"
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
    query = "UPDATE bidItems SET highestBid = ?, highestBidder = ? WHERE id = ?"
    execute_query(query, (amount, highestBidder, bidID), commit=True)

def deductTokens(email, amount):
    query = "UPDATE users SET tokens = tokens - ? WHERE email = ?"
    execute_query(query, (amount, email), commit=True)
