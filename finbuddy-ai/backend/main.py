from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from passlib.context import CryptContext
from jose import jwt, JWTError
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import uuid

# Load environment variables
load_dotenv()

app = FastAPI()
security = HTTPBearer()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")

# Update password hashing configuration
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def get_token_from_header(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return credentials.credentials

# Models
class UserCreate(BaseModel):
    email: str
    password: str
    username: str
    first_name: str
    last_name: str
    phone_number: str

class UserLogin(BaseModel):
    email: str
    password: str

# Initialize database
def init_db():
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        
        # Create users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                username VARCHAR(50) UNIQUE NOT NULL,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                phone_number VARCHAR(15) NOT NULL,
                hashed_password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create bank_accounts table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS bank_accounts (
                id SERIAL PRIMARY KEY,
                account_id VARCHAR(50) UNIQUE NOT NULL,
                user_id INTEGER REFERENCES users(id),
                name VARCHAR(50) NOT NULL,
                mask VARCHAR(4) NOT NULL,
                available_balance DECIMAL(10,2) NOT NULL,
                current_balance DECIMAL(10,2) NOT NULL,
                currency_code VARCHAR(3) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create transactions table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id SERIAL PRIMARY KEY,
                transaction_id VARCHAR(50) UNIQUE NOT NULL,
                account_id VARCHAR(50) NOT NULL,
                date DATE NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                name VARCHAR(100) NOT NULL,
                category VARCHAR(50) NOT NULL,
                user_id INTEGER REFERENCES users(id),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        raise
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

# Initialize database only if tables don't exist
init_db()

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def generate_mock_bank_data(user_id):
    account_id = f"acct_{uuid.uuid4()}"
    mask = str(uuid.uuid4().int)[:4]
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Create bank account
        cur.execute("""
            INSERT INTO bank_accounts 
            (account_id, user_id, name, mask, available_balance, current_balance, currency_code)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            account_id, user_id, "Primary Checking", mask, 1500.00, 1500.00, "USD"
        ))
        conn.commit()
        
        # Generate transactions
        categories = ['Food', 'Transportation', 'Travel', 'Shopping', 'Rent', 'Other']
        merchants = {
            'Food': ['Starbucks', 'McDonalds', 'Whole Foods', 'Local Restaurant', 'Pizza Place'],
            'Transportation': ['Uber', 'Lyft', 'Gas Station', 'Public Transit'],
            'Travel': ['Airbnb', 'Hotel', 'Airline'],
            'Shopping': ['Amazon', 'Target', 'Walmart', 'Best Buy'],
            'Rent': ['Apartment Rent'],
            'Other': ['Netflix', 'Spotify', 'Gym Membership']
        }
        
        transactions = []
        today = datetime.now()
        
        for i in range(60):  # 60 days of transactions
            date = today - timedelta(days=i)
            num_transactions = 3  # 3 transactions per day
            
            for _ in range(num_transactions):
                category = categories[i % len(categories)]
                merchant = merchants[category][i % len(merchants[category])]
                
                if category == 'Rent':
                    amount = -1200.00
                elif category == 'Income':
                    amount = 2000.00
                else:
                    amount = round((i % 200) - 100, 2)  # Random amount between -100 and 100
                
                transaction_id = f"tx_{uuid.uuid4()}"
                transactions.append((
                    transaction_id, account_id, date, amount, merchant, category, user_id
                ))
        
        # Insert transactions
        cur.executemany("""
            INSERT INTO transactions 
            (transaction_id, account_id, date, amount, name, category, user_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, transactions)
        conn.commit()
    except Exception as e:
        print(f"Error generating mock bank data: {str(e)}")
        raise
    finally:
        cur.close()
        conn.close()

@app.post("/register")
async def register(user: UserCreate):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Check if user exists
        cur.execute("SELECT * FROM users WHERE email = %s OR username = %s", 
                   (user.email, user.username))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="Email or username already registered")
        
        # Hash password
        hashed_password = pwd_context.hash(user.password)
        
        # Insert user
        cur.execute("""
            INSERT INTO users (email, username, first_name, last_name, phone_number, hashed_password)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, email, username, first_name, last_name, phone_number
        """, (
            user.email, user.username, user.first_name, user.last_name, user.phone_number, hashed_password
        ))
        
        new_user = cur.fetchone()
        conn.commit()

        # Generate mock bank data
        generate_mock_bank_data(new_user['id'])

        # Create token
        token_data = {"sub": user.email}
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
        
        return {
            "access_token": token,
            "user": {
                "email": new_user["email"],
                "username": new_user["username"],
                "first_name": new_user["first_name"],
                "last_name": new_user["last_name"],
                "phone_number": new_user["phone_number"]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.post("/login")
async def login(user: UserLogin):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("SELECT * FROM users WHERE email = %s", (user.email,))
        db_user = cur.fetchone()
        
        if not db_user or not pwd_context.verify(user.password, db_user["hashed_password"]):
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        
        token_data = {"sub": user.email}
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
        
        return {
            "access_token": token,
            "user": {
                "email": db_user["email"],
                "username": db_user["username"],
                "first_name": db_user["first_name"],
                "last_name": db_user["last_name"],
                "phone_number": db_user["phone_number"]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.post("/bank/init")
async def init_bank_data(token: str = Depends(get_token_from_header)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            # Check if user already has bank data
            cur.execute("""
                SELECT id FROM bank_accounts 
                WHERE user_id = (SELECT id FROM users WHERE email = %s)
            """, (email,))
            if cur.fetchone():
                return {"message": "Bank data already initialized"}
            
            # Get user ID
            cur.execute("SELECT id FROM users WHERE email = %s", (email,))
            user = cur.fetchone()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Generate mock bank data
            generate_mock_bank_data(user['id'])
            
            return {"message": "Bank data initialized successfully"}
        finally:
            cur.close()
            conn.close()
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/profile")
async def get_profile(token: str = Depends(get_token_from_header)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            # Get user profile
            cur.execute("""
                SELECT id, email, username, first_name, last_name, phone_number
                FROM users
                WHERE email = %s
            """, (email,))
            user = cur.fetchone()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Get bank account
            cur.execute("""
                SELECT account_id, name, mask, available_balance, current_balance, currency_code
                FROM bank_accounts
                WHERE user_id = %s
            """, (user['id'],))
            account = cur.fetchone()
            
            # Format account data
            formatted_account = None
            if account:
                formatted_account = {
                    "account_id": account['account_id'],
                    "name": account['name'],
                    "mask": account['mask'],
                    "balances": {
                        "available": account['available_balance'],
                        "current": account['current_balance'],
                        "iso_currency_code": account['currency_code']
                    }
                }
            
            # Get transactions
            transactions = []
            if account:
                cur.execute("""
                    SELECT transaction_id, account_id, date, amount, name, category
                    FROM transactions
                    WHERE account_id = %s
                    ORDER BY date DESC
                """, (account['account_id'],))
                transactions = cur.fetchall()
            
            return {
                "user": {
                    "id": user['id'],
                    "email": user['email'],
                    "username": user['username'],
                    "first_name": user['first_name'],
                    "last_name": user['last_name'],
                    "phone_number": user['phone_number']
                },
                "bank_data": {
                    "accounts": [formatted_account] if formatted_account else [],
                    "transactions": transactions
                }
            }
        finally:
            cur.close()
            conn.close()
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bank/data")
async def get_bank_data(token: str = Depends(get_token_from_header)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            # Get bank account
            cur.execute("""
                SELECT account_id, name, mask, available_balance, current_balance, currency_code
                FROM bank_accounts
                WHERE user_id = (SELECT id FROM users WHERE email = %s)
            """, (email,))
            account = cur.fetchone()
            
            if not account:
                return {
                    "accounts": [],
                    "transactions": []
                }
            
            # Format account data to match frontend expectations
            formatted_account = {
                "account_id": account['account_id'],
                "name": account['name'],
                "mask": account['mask'],
                "balances": {
                    "available": account['available_balance'],
                    "current": account['current_balance'],
                    "iso_currency_code": account['currency_code']
                }
            }
            
            # Get transactions
            cur.execute("""
                SELECT transaction_id, account_id, date, amount, name, category
                FROM transactions
                WHERE account_id = %s
                ORDER BY date DESC
            """, (account['account_id'],))
            transactions = cur.fetchall()
            
            return {
                "accounts": [formatted_account],
                "transactions": transactions
            }
        finally:
            cur.close()
            conn.close()
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "API is running!"} 