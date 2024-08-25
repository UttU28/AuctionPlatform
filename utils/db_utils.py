# Database utility functions
# utils/db_utils.py

import pyodbc
from config import AzureSQLConfig
from datetime import datetime, timezone



# Connection Management
def getDbConnection():
    connection = pyodbc.connect(AzureSQLConfig.connectionString)
    return connection

# User Management
def createUser(name, email, hashedPassword):
    connection = getDbConnection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (email, name, hashed_password, credits, tokens) VALUES (?, ?, ?, 100, 0)",
            (email, name, hashedPassword)
        )
        connection.commit()
    except pyodbc.Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()

def getUserByEmail(email):
    connection = getDbConnection()
    cursor = connection.cursor()
    user = None
    try:
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        if row:
            user = {'email': row[0], 'name': row[1], 'hashed_password': row[2], 'credits': row[3], 'tokens': row[4]}
    except pyodbc.Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()
    return user

def updatePassword(email, hashedPassword):
    connection = getDbConnection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "UPDATE users SET hashed_password = ? WHERE email = ?",
            (hashedPassword, email)
        )
        connection.commit()
    except pyodbc.Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()

def updateUserCreditsTokens(email, whatToAdd, howMuch):
    connection = getDbConnection()
    cursor = connection.cursor()
    try:
        credits, tokens = getUserCreditsTokens(email)
        cursor.execute(
            "UPDATE users SET ? = ? WHERE email = ?",
            (whatToAdd, final, email)
        )
        connection.commit()
    except pyodbc.Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()

def getUserCreditsTokens(email):
    connection = getDbConnection()
    cursor = connection.cursor()
    credits, tokens = 0, 0
    try:
        cursor.execute("SELECT credits, tokens FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        if row:
            credits = row[0]
            tokens = row[1]
    except pyodbc.Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()
    return credits, tokens

# bid Management
def loadAllBids():
    connection = getDbConnection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
                SELECT * FROM bidItems
                ORDER BY startTime ASC
            """
        )
        rows = cursor.fetchall()
        bidQueue = [{'id': row[0], 'title': row[1], 'description': row[2], 'startTime': row[3], 'baseBid': row[4], 'highestBid': row[5], 'highestBidder': row[6]} for row in rows]
    except pyodbc.Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()
    return bidQueue

def addToApplyQueue(bidID, selectedResume, email):
    connection = getDbConnection()
    cursor = connection.cursor()
    try:
        timestamp = int(datetime.now(timezone.utc).timestamp())
        cursor.execute(
            """
                INSERT INTO applyQueue (bidID, timeOfArrival, selectedResume, email)
                SELECT ?, ?, ?, ?
                WHERE NOT EXISTS (
                    SELECT 1 FROM applyQueue WHERE bidID = ? AND email = ?
                );
            """,
            (bidID, timestamp, selectedResume, email, bidID, email)
        )
        if cursor.rowcount != 1:
            print(f"bidID {bidID} already exists in apply queue. No duplicate added.")
        else:
            print(f"Added bidID {bidID} to apply queue")
        connection.commit()
    except pyodbc.Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()

# Resume Management
def addResumeToDatabase(resumeID, resumeName, email):
    connection = getDbConnection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO resumeList (resumeId, resumeName, email) VALUES (?, ?, ?)",
            (resumeID, resumeName, email)
        )
        connection.commit()
    except pyodbc.Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()

def deleteResumeFromDatabase(resumeId):
    connection = getDbConnection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "DELETE FROM resumeList WHERE resumeId = ?",
            (resumeId,)
        )
        connection.commit()
    except pyodbc.Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()

def getUsersResumes(email):
    connection = getDbConnection()
    cursor = connection.cursor()
    resumeData = {}
    try:
        # cursor.execute("SELECT * FROM resumeList")
        cursor.execute(
            "SELECT * FROM resumeList WHERE email = ?", 
            (email,)
        )
        rows = cursor.fetchall()
        resumeData = {row[0]: row[1] for row in rows}
    except pyodbc.Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()
    # print(resumeData)
    return resumeData
