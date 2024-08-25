CREATE TABLE users (
    email VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    credits INT NOT NULL,
    tokens INT NOT NULL,
    tokensHold INT NOT NULL
);

-- Create bidItems table
CREATE TABLE bidItems (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description NTEXT,
    startTime BIGINT NOT NULL,
    baseBid INT NOT NULL,
    highestBid INT,
    highestBidder VARCHAR(36),
);


-- Create allBids table
CREATE TABLE allBids (
    bidQueueID INT IDENTITY(1,1) PRIMARY KEY,
    userID VARCHAR(36) NOT NULL,
    bidID VARCHAR(36) NOT NULL,
    bidAmount INT NOT NULL,
    depositAmount INT NOT NULL,
    bidTime BIGINT NOT NULL
);

-- -- Create resumeList table
-- CREATE TABLE resumeList (
--     resumeId VARCHAR(255) PRIMARY KEY,
--     resumeName VARCHAR(255) NOT NULL,
--     email VARCHAR(255) NOT NULL
-- );

-- -- Create applyQueue table
-- CREATE TABLE applyQueue (
--     applyQueueID INT IDENTITY(1,1) PRIMARY KEY,
--     jobID VARCHAR(36) NOT NULL,
--     timeOfArrival BIGINT NOT NULL,
--     selectedResume VARCHAR(255) NOT NULL,
--     email VARCHAR(255) NOT NULL
-- );
-- SELECT * FROM applyQueue;

-- -- Create scoreBoard table
-- CREATE TABLE scoreBoard (
--     contender VARCHAR(255) NOT NULL,
--     score INT NOT NULL,
--     PRIMARY KEY (contender)
-- );
