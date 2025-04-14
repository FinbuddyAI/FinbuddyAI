import json
import os
from datetime import datetime
from database import get_db, init_db
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()

# Password hashing configuration
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)

# User information
USER_INFO = {
    "email": "john.doe@gmail.com",
    "username": "john.doe",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "2408888888",
    "password": "password123"  # This will be hashed before insertion
}

def create_transactions_table():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"), cursor_factory=RealDictCursor)
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY,
            transaction_id VARCHAR(50) UNIQUE NOT NULL,
            account_id VARCHAR(50) NOT NULL,
            date DATE NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            name VARCHAR(255) NOT NULL,
            category VARCHAR(50) NOT NULL,
            user_id INTEGER REFERENCES users(id),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    cur.close()
    conn.close()

def insert_user():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"), cursor_factory=RealDictCursor)
    cur = conn.cursor()
    
    try:
        # Hash the password
        hashed_password = pwd_context.hash(USER_INFO["password"])
        
        cur.execute("""
            INSERT INTO users (email, username, first_name, last_name, phone_number, hashed_password)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            USER_INFO["email"],
            USER_INFO["username"],
            USER_INFO["first_name"],
            USER_INFO["last_name"],
            USER_INFO["phone_number"],
            hashed_password
        ))
        
        user_id = cur.fetchone()['id']
        conn.commit()
        return user_id
    except Exception as e:
        print(f"Error inserting user: {e}")
        conn.rollback()
        return None
    finally:
        cur.close()
        conn.close()

def insert_transactions(user_id):
    # Read transactions from the JSON file
    with open("transaction_data.json", "r") as f:
        data = json.load(f)
        transactions = data["transactions"]
    
    conn = psycopg2.connect(os.getenv("DATABASE_URL"), cursor_factory=RealDictCursor)
    cur = conn.cursor()
    
    try:
        for transaction in transactions:
            cur.execute("""
                INSERT INTO transactions (
                    transaction_id, account_id, date, amount, name, category, user_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (transaction_id) DO NOTHING
            """, (
                transaction["transaction_id"],
                transaction["account_id"],
                transaction["date"],
                transaction["amount"],
                transaction["name"],
                transaction["category"],
                user_id
            ))
        
        conn.commit()
        print(f"Successfully inserted {len(transactions)} transactions")
    except Exception as e:
        print(f"Error inserting transactions: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def delete_user_data():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"), cursor_factory=RealDictCursor)
    cur = conn.cursor()
    
    try:
        # First get the user ID
        cur.execute("SELECT id FROM users WHERE email = %s", (USER_INFO["email"],))
        result = cur.fetchone()
        
        if result:
            user_id = result["id"]
            # Delete transactions first
            cur.execute("DELETE FROM transactions WHERE user_id = %s", (user_id,))
            # Delete bank accounts
            cur.execute("DELETE FROM bank_accounts WHERE user_id = %s", (user_id,))
            # Finally delete user
            cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
            conn.commit()
            print("Successfully deleted user data")
        else:
            print("User not found")
    except Exception as e:
        print(f"Error deleting user data: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def recreate_transactions_table():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"), cursor_factory=RealDictCursor)
    cur = conn.cursor()
    
    try:
        # First ensure users table exists
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                username VARCHAR(50) UNIQUE NOT NULL,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                phone_number VARCHAR(15) NOT NULL,
                hashed_password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Drop the transactions table if it exists
        cur.execute("DROP TABLE IF EXISTS transactions")
        conn.commit()
        
        # Create the transactions table with the correct schema
        cur.execute("""
            CREATE TABLE transactions (
                id SERIAL PRIMARY KEY,
                transaction_id VARCHAR(50) UNIQUE NOT NULL,
                account_id VARCHAR(50) NOT NULL,
                date DATE NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                name VARCHAR(255) NOT NULL,
                category VARCHAR(50) NOT NULL,
                user_id INTEGER REFERENCES users(id),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("Successfully recreated transactions table")
    except Exception as e:
        print(f"Error recreating transactions table: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def insert_bank_account(user_id):
    conn = psycopg2.connect(os.getenv("DATABASE_URL"), cursor_factory=RealDictCursor)
    cur = conn.cursor()
    
    try:
        # Insert bank account
        cur.execute("""
            INSERT INTO bank_accounts (account_id, user_id, name, mask, available_balance, current_balance, currency_code)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING account_id
        """, (
            "vzeNDwK7KQIm4yEog683uElbp9GRleFXsKw6J",  # account_id from transactions
            user_id,
            "Plaid Checking",
            "0000",
            1000.00,
            1100.00,
            "USD"
        ))
        
        account_id = cur.fetchone()['account_id']
        conn.commit()
        return account_id
    except Exception as e:
        print(f"Error inserting bank account: {e}")
        conn.rollback()
        return None
    finally:
        cur.close()
        conn.close()

def setup_database():
    # Initialize database and create tables
    init_db()
    
    # Insert user and get user_id
    user_id = insert_user()
    
    if user_id:
        # Insert bank account and get account_id
        account_id = insert_bank_account(user_id)
        if account_id:
            # Read transactions from the JSON file
            with open("transaction_data.json", "r") as f:
                data = json.load(f)
                transactions = data["transactions"]
            
            conn = psycopg2.connect(os.getenv("DATABASE_URL"), cursor_factory=RealDictCursor)
            cur = conn.cursor()
            
            try:
                for transaction in transactions:
                    # Format category to match frontend expectations
                    category = transaction["category"].capitalize()
                    if category == "Food":
                        category = "Food"
                    elif category == "Transportation":
                        category = "Transportation"
                    elif category == "Travel":
                        category = "Travel"
                    elif category == "Shopping":
                        category = "Shopping"
                    elif category == "Rent":
                        category = "Rent"
                    else:
                        category = "Other"
                    
                    # Use the account_id from the bank account we just created
                    cur.execute("""
                        INSERT INTO transactions (
                            transaction_id, account_id, date, amount, name, category, user_id
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (transaction_id) DO NOTHING
                    """, (
                        transaction["transaction_id"],
                        account_id,  # Use the account_id from the bank account
                        transaction["date"],
                        transaction["amount"],
                        transaction["name"],
                        category,  # Use formatted category
                        user_id
                    ))
                
                conn.commit()
                print(f"Successfully inserted {len(transactions)} transactions")
            except Exception as e:
                print(f"Error inserting transactions: {e}")
                conn.rollback()
            finally:
                cur.close()
                conn.close()
        else:
            print("Failed to insert bank account")
    else:
        print("Failed to insert user")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "setup":
            setup_database()
        elif sys.argv[1] == "delete":
            delete_user_data()
        else:
            print("Invalid command. Use 'setup' or 'delete'")
    else:
        print("Please provide a command: 'setup' or 'delete'") 