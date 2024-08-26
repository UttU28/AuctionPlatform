-- Create users table
CREATE TABLE users (
    userID VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    credits INT NOT NULL DEFAULT 0,
    tokens INT NOT NULL DEFAULT 0,
    tokensHold INT NOT NULL DEFAULT 0
);

-- Create inventory table
CREATE TABLE inventory (
    itemID BIGINT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    currentOwner VARCHAR(255) NOT NULL,
    FOREIGN KEY (currentOwner) REFERENCES users(userID)
);

-- Create bidQueue table
CREATE TABLE bidQueue (
    bidID BIGINT PRIMARY KEY,
    itemID BIGINT NOT NULL,
    baseBid INT NOT NULL,
    highestBid INT DEFAULT 0,
    highestBidder VARCHAR(255),
    isEnded BIT NOT NULL,
    FOREIGN KEY (itemID) REFERENCES inventory(itemID),
    FOREIGN KEY (highestBidder) REFERENCES users(userID)
);

-- Create allBids table
CREATE TABLE allBids (
    bidQueueID BIGINT PRIMARY KEY,
    userID VARCHAR(255) NOT NULL,
    bidID BIGINT NOT NULL,
    bidAmount INT NOT NULL,
    bidTime BIGINT NOT NULL,
    FOREIGN KEY (userID) REFERENCES users(userID),
    FOREIGN KEY (bidID) REFERENCES bidQueue(bidID)
);
