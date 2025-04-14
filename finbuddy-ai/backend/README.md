# Transaction Manager

This script helps manage transaction data in the database. It provides functionality to:
1. Set up the database with sample transaction data for a test user (John Doe)
2. Delete all data associated with the test user

## Prerequisites

- Python 3.x
- PostgreSQL database
- Required Python packages (install via pip):
  - psycopg2-binary
  - python-dotenv

## Setup

1. Make sure your `.env` file contains the `DATABASE_URL` variable
2. The transaction data is stored in `transaction_data.json`
3. The user data is hardcoded in the script (John Doe's information)

## Usage

To set up the database and insert the test data:
```bash
python transaction_manager.py setup
```

To delete all data associated with the test user:
```bash
python transaction_manager.py delete
```

## Data Structure

The script will:
1. Create a transactions table if it doesn't exist
2. Create a test user (John Doe)
3. Insert all transactions from the JSON file, linking them to the test user
4. Provide a way to clean up all this test data

The transactions table has the following structure:
- id: Serial primary key
- transaction_id: Unique identifier for the transaction
- account_id: Account identifier
- date: Transaction date
- amount: Transaction amount
- name: Merchant name
- category: Transaction category
- user_id: Foreign key to users table
- created_at: Timestamp of record creation 