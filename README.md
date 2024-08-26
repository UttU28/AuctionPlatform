# AuctionPlatform

## Overview

AuctionPlatform is a Python-based web application built with Flask and Azure SQL. This platform allows users to register, log in, place bids, and manage their inventory. Bids are active for 1 minute, and successful bids are recorded in the user's inventory. The platform supports token-based bidding, with tokens convertible from credits (3 Credits = 1 Token).

## Features

- **User Registration & Authentication**: Users can register, log in, and manage their accounts.
- **Bidding System**: Place bids on auction items with a 1-minute expiration.
- **Token Management**: Convert credits to tokens for bidding (3 Credits = 1 Token).
- **Bid Handling**: Bids are held until they expire; tokens are deducted for winning bids and released for losing ones.
- **Inventory Management**: Track and manage auction items won.

## Tech Stack

- **Backend**: Python, Flask
- **Database**: Azure SQL
- **Frontend**: HTML, CSS, JavaScript

## Setup Instructions

### Prerequisites

- Python 3.x
- Flask
- Azure SQL Database
- Required Python packages (listed in `requirements.txt`)

### Installation

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd AuctionPlatform
   ```

2. **Create and Activate a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the Database**
   - Set up your Azure SQL database and update the connection string in `config.py`.

5. **Run Migrations**
   ```bash
   flask db upgrade
   ```

6. **Start the Application**
   ```bash
   flask run
   ```

   The app will be available at `http://localhost:5000`.

## Usage

- **Register**: Create a new account.
- **Log In**: Access your account with your credentials.
- **Place Bids**: Use tokens to place bids on auction items.
- **Manage Inventory**: View and manage items you have won.

## Token Conversion

- Convert 3 Credits to 1 Token.
- Manage credits and tokens from the user dashboard.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request with your improvements.

## Contact

For any questions or issues, please contact [your-email@example.com].

---

It is a Python based webapp created using Flask, SQL for data storing. Each user can Register and Log In to the app, Check for any bids and place your bids on it. Each bid lives for 1 minute from creation, and is added to your inventory if your bid is the highest when the bid ends. The amount of TOKEN placed by user in the bid is kept in hold until the bid ends  and is deducted if won and released if lost. You can convert oyur credits to tokens for placing in the et. here 3 Credit = 1 Token

Tools Used: Python, Flaks, HTML, CSS, JS, Azure SQL, 