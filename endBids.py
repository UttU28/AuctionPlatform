from time import sleep
import pyodbc
from config import AzureSQLConfig
from datetime import datetime, timezone

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

def getAllBidInfo():
    query = "SELECT * FROM bidQueue WHERE isEnded = 0"
    rows = execute_query(query, fetchall=True)
    if rows:
        return [{'bidID': row[0], 'itemID': row[1], 'baseBid': row[2], 'highestBid': row[3], 'highestBidder': row[4], 'isEnded': row[5]} for row in rows]
    return None

def checkBidAge(bidTimeStamp):
    age = int(datetime.now(timezone.utc).timestamp()) - bidTimeStamp
    return age > 70

def getAllUserBidFor(thisBid):
    query = """
        SELECT bidQueueID, userID, bidID, bidAmount, bidTime
        FROM allBids
        WHERE bidID = ?
        ORDER BY bidQueueID DESC
    """
    rows = execute_query(query, (thisBid,), fetchall=True)
    return [{'bidQueueID': row[0], 'userID': row[1], 'bidID': row[2], 'bidAmount': row[3], 'bidTime': row[4]} for row in rows]

def getCurrentOwner(thisItem):
    query = """
        SELECT currentOwner
        FROM inventory
        WHERE itemID = ?
    """
    rows = execute_query(query, (thisItem,), fetchone=True)
    return rows[0]

def endTheBidOn(thisBid):
    query = "UPDATE bidQueue SET isEnded = 1 WHERE bidID = ?"
    execute_query(query, (thisBid,), commit=True)   

def giveRefundTo(userID, bidAmount):
    query = """
        UPDATE users SET
        tokensHold = tokensHold - ?,
        tokens = tokens + ?
        WHERE userID = ?;
    """
    execute_query(query, (bidAmount, bidAmount, userID), commit=True)
    print(f"Refunded to user {userID}.")

def deductTokens(giveTo, takeFrom, bidAmount, itemID):
    query = """
        UPDATE users SET tokensHold = tokensHold - ? WHERE userID = ?;
        UPDATE users SET tokens = tokens + ? WHERE userID = ?;
        UPDATE inventory SET currentOwner = ? WHERE itemID = ?;
    """
    execute_query(query, (bidAmount, takeFrom, bidAmount, giveTo, takeFrom, itemID), commit=True)
    print(f"Tokens deducted from user {giveTo}.")

while True:
    allBids = getAllBidInfo()
    if allBids:
        for bid in allBids:
            bidID = bid['bidID']
            if checkBidAge(bidID):
                userBids = getAllUserBidFor(bidID)
                print(userBids)
                currentOwner = getCurrentOwner(bidID)
                print('currentOwner', currentOwner)
                for userBid in userBids:
                    if userBid['userID'] != bid['highestBidder']:
                        giveRefundTo(userBid['userID'], userBid['bidAmount'])
                    else:
                        deductTokens(currentOwner, userBid['userID'], userBid['bidAmount'], bidID)
                endTheBidOn(bidID)
                print(f"Hello, Bid ID {bidID} is older than 70 seconds.")
    
    sleep(10)
