from fastapi import FastAPI, HTTPException, Depends, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRouter
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from passlib.context import CryptContext
from jose import jwt, JWTError
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import uuid
import sys
from pathlib import Path
import pandas as pd
from database import get_db, init_db
from chat.routes import router as chat_router
from auth import get_current_user, get_token_from_header, security, SECRET_KEY, ALGORITHM
from goal_refine.goal_adjuster import detect_unusual_transactions, detect_additional_income, adjust_goals
from goal_refine.goal_history_tracker import GoalHistoryTracker
from chat.mcp_server import mcp_server

# Add the onboarding directory to the Python path
onboarding_path = str(Path(__file__).parent.parent / "onboarding")
if onboarding_path not in sys.path:
    sys.path.append(onboarding_path)

from onboarding_agent import OnboardingAgent

# Load environment variables
load_dotenv()

app = FastAPI()

# Create routers
onboarding_router = APIRouter(prefix="/onboarding", tags=["onboarding"])
goal_refine_router = APIRouter(prefix="/goals", tags=["goals"])

# Initialize the onboarding agent
config_path = os.path.join(os.path.dirname(__file__), "..", "config_list.json")
onboarding_agent = OnboardingAgent(config_path=config_path)
onboarding_agent.create_agents()

# Initialize goal history tracker
goal_history_tracker = GoalHistoryTracker()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")

# Update password hashing configuration
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)

# Models
class User(BaseModel):
    id: int
    email: str
    username: str
    first_name: str
    last_name: str
    phone_number: str

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

class ChatMessage(BaseModel):
    message: str

# Onboarding models
class OnboardingMessage(BaseModel):
    content: str

class TransactionCreate(BaseModel):
    amount: float
    category: str
    name: str
    date: str

# Initialize database
def init_db():
    try:
        conn = psycopg2.connect(DATABASE_URL)
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
    return psycopg2.connect(DATABASE_URL)

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

@app.post("/chat")
async def chat(message: ChatMessage, token: str = Depends(get_token_from_header)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Initialize the LLM
        from chat.simple_llm import SimpleLLM
        llm = SimpleLLM()
        
        # Get response from LLM
        response = await llm.get_response(message.message)
        return {"response": response}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Welcome to FinBuddy AI API"}

# Onboarding routes
@onboarding_router.post("/start")
async def start_onboarding(token: str = Depends(get_token_from_header)):
    """
    Start a new onboarding session and return the initial message from the financial advisor.
    """
    try:
        # Start the conversation and get the initial message
        initial_message = onboarding_agent.start_conversation()
        return {"message": initial_message}
    except Exception as e:
        print(f"Error in start_onboarding: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@onboarding_router.post("/send-message")
async def send_message(message: OnboardingMessage, token: str = Depends(get_token_from_header)):
    """
    Send a message to the financial advisor and get the response.
    """
    try:
        # Send the message and get the response
        response_message, is_complete, profile = onboarding_agent.send_message(message.content)
        
        if is_complete:
            return {
                "message": response_message,
                "is_complete": True,
                "profile": profile
            }
            
        return {
            "message": response_message,
            "is_complete": False
        }
    except Exception as e:
        print(f"Error in send_message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@onboarding_router.get("/goals")
async def get_onboarding_goals(token: str = Depends(get_token_from_header)):
    """
    Get the list of onboarding goals that need to be completed.
    """
    try:
        goals = onboarding_agent.get_onboarding_goals()
        return {"goals": goals}
    except Exception as e:
        print(f"Error in get_onboarding_goals: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/goals/saving")
async def get_saving_goals(current_user: dict = Depends(get_current_user)):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT goal_id, category, target_amount, current_amount, target_date, created_at, last_adjusted_at
                    FROM saving_goals
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                """, (current_user['id'],))
                goals = cur.fetchall()
                
                return {
                    "saving_goals": [
                        {
                            "id": goal[0],
                            "category": goal[1],
                            "target_amount": float(goal[2]),
                            "current_amount": float(goal[3]),
                            "date": goal[4].isoformat(),
                            "created_at": goal[5].isoformat(),
                            "last_adjusted_at": goal[6].isoformat()
                        }
                        for goal in goals
                    ]
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/goals/spending")
async def get_spending_goals(current_user: dict = Depends(get_current_user)):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT goal_id, category, target_amount, current_amount, created_at, last_adjusted_at
                    FROM spending_goals
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                """, (current_user['id'],))
                goals = cur.fetchall()
                
                return {
                    "spending_goals": [
                        {
                            "id": goal[0],
                            "category": goal[1],
                            "target_amount": float(goal[2]),
                            "current_amount": float(goal[3]),
                            "created_at": goal[4].isoformat(),
                            "last_adjusted_at": goal[5].isoformat()
                        }
                        for goal in goals
                    ]
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transactions/create")
async def create_transaction(transaction: TransactionCreate, current_user: dict = Depends(get_current_user)):
    """Create a new transaction"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Get user's account_id
        cur.execute("""
            SELECT account_id FROM bank_accounts 
            WHERE user_id = %s 
            LIMIT 1
        """, (current_user['id'],))
        result = cur.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="No bank account found")
            
        account_id = result['account_id']
        
        # Create transaction
        transaction_id = f"tx_{uuid.uuid4()}"
        cur.execute("""
            INSERT INTO transactions 
            (transaction_id, account_id, date, amount, name, category, user_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (
            transaction_id,
            account_id,
            transaction.date,
            transaction.amount,
            transaction.name,
            transaction.category,
            current_user['id']
        ))
        
        new_transaction = cur.fetchone()
        
        # Update bank account balance
        cur.execute("""
            UPDATE bank_accounts 
            SET current_balance = current_balance + %s,
                available_balance = available_balance + %s
            WHERE account_id = %s
        """, (transaction.amount, transaction.amount, account_id))
        
        conn.commit()
        return new_transaction
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

# Include the onboarding router
app.include_router(onboarding_router)

# Include the chat router
app.include_router(chat_router, prefix="/api/chat")

@goal_refine_router.post("/detect-unusual")
async def detect_unusual_activity(token: str = Depends(get_token_from_header)):
    """Detect unusual transactions and additional income"""
    current_user = await get_current_user(token)
    print(f"Debug - Current user in detect-unusual: {current_user}")  # Debug log
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Get recent transactions with explicit column selection
        cur.execute("""
            SELECT 
                transaction_id, 
                account_id, 
                date, 
                amount::float,  -- Convert amount to float
                name, 
                category, 
                user_id
            FROM transactions 
            WHERE user_id = %s 
            AND date >= NOW() - INTERVAL '30 days'
            ORDER BY date DESC
        """, (current_user['id'],))
        
        transactions = cur.fetchall()
        print(f"Debug - Found {len(transactions)} transactions in detect-unusual")  # Debug log
        
        if not transactions:
            return {
                "unusual_transactions": [],
                "additional_income": [],
                "total_additional_income": 0
            }
        
        # Convert to DataFrame with explicit column names
        df = pd.DataFrame(transactions, columns=[
            'transaction_id', 
            'account_id', 
            'date', 
            'amount', 
            'name', 
            'category', 
            'user_id'
        ])
        print(f"Debug - DataFrame columns: {df.columns.tolist()}")  # Debug log
        print(f"Debug - DataFrame sample: {df.head()}")  # Debug log
        print(f"Debug - Amount type: {df['amount'].dtype}")  # Debug log
        
        df['transaction_date'] = pd.to_datetime(df['date'])
        
        # Ensure amount is float
        df['amount'] = df['amount'].astype(float)
        
        # Detect unusual transactions
        unusual_transactions = detect_unusual_transactions(df)
        print(f"Debug - Found {len(unusual_transactions)} unusual transactions in detect-unusual")  # Debug log
        
        # Detect additional income
        additional_income, total_additional_income = detect_additional_income(df)
        print(f"Debug - Additional income in detect-unusual: {additional_income}")  # Debug log
        
        return {
            "unusual_transactions": unusual_transactions,
            "additional_income": additional_income,
            "total_additional_income": total_additional_income
        }
        
    except Exception as e:
        print(f"Debug - Error in detect-unusual: {str(e)}")  # Debug log
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@goal_refine_router.post("/adjust")
async def adjust_goals_endpoint(token: str = Depends(get_token_from_header)):
    """Adjust goals based on recent transactions"""
    current_user = await get_current_user(token)
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Get recent transactions
        cur.execute("""
            SELECT * FROM transactions 
            WHERE user_id = %s 
            AND date >= NOW() - INTERVAL '30 days'
            ORDER BY date DESC
        """, (current_user.id,))
        
        transactions = cur.fetchall()
        
        if not transactions:
            raise HTTPException(status_code=400, detail="No recent transactions found")
        
        # Convert to DataFrame
        df = pd.DataFrame(transactions)
        df['transaction_date'] = pd.to_datetime(df['date'])
        
        # Get current goals
        cur.execute("""
            SELECT * FROM goals 
            WHERE user_id = %s 
            AND status = 'active'
        """, (current_user.id,))
        
        goals = cur.fetchall()
        
        if not goals:
            raise HTTPException(status_code=400, detail="No active goals found")
        
        # Convert to DataFrame
        goals_df = pd.DataFrame(goals)
        
        # Detect unusual transactions and additional income
        unusual_transactions = detect_unusual_transactions(df)
        additional_income, _ = detect_additional_income(df)
        
        # Prepare trigger reasons
        trigger_reasons = []
        if unusual_transactions:
            trigger_reasons.append("Unusual transactions detected")
        if additional_income:
            trigger_reasons.append("Additional income detected")
        
        if not trigger_reasons:
            return {"message": "No significant changes detected to warrant goal adjustment"}
        
        # Adjust goals
        adjusted_goals, adjustment_result = adjust_goals(
            df,
            trigger_reasons,
            goals_df
        )
        
        # Save adjustment to history
        adjustment_id = goal_history_tracker.save_adjustment(
            goals_df,
            adjusted_goals,
            adjustment_result,
            trigger_event=", ".join(trigger_reasons)
        )
        
        # Update goals in database
        for _, goal in adjusted_goals.iterrows():
            cur.execute("""
                UPDATE goals 
                SET target_amount = %s,
                    updated_at = NOW()
                WHERE id = %s AND user_id = %s
            """, (goal['target_amount'], goal['id'], current_user.id))
        
        conn.commit()
        
        return {
            "adjustment_id": adjustment_id,
            "adjusted_goals": adjusted_goals.to_dict('records'),
            "adjustment_result": adjustment_result
        }
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@goal_refine_router.get("/history")
async def get_goal_history(token: str = Depends(get_token_from_header)):
    """Get goal adjustment history"""
    current_user = await get_current_user(token)
    
    try:
        # Get adjustment history
        history = goal_history_tracker.get_adjustment_summary()
        
        return {
            "history": history
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Include routers
app.include_router(onboarding_router)
app.include_router(goal_refine_router)
app.include_router(chat_router)

@app.post("/anomaly/detect")
async def detect_anomalies(token: str = Depends(get_token_from_header)):
    """Detect anomalies in recent transactions"""
    try:
        # print("Debug - Getting current user from token")  # Debug log
        current_user = await get_current_user(token)
        # print(f"Debug - Current user object: {current_user}")  # Debug log
        
        if not current_user or 'id' not in current_user:
            # print(f"Debug - Invalid user object structure: {current_user}")  # Debug log
            raise HTTPException(status_code=500, detail="Invalid user object structure")
            
        user_id = current_user['id']
        # print(f"Debug - Using user_id: {user_id}")  # Debug log
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Get recent transactions
                cur.execute("""
                    SELECT transaction_id, account_id, date, amount, name, category, user_id
                    FROM transactions 
                    WHERE user_id = %s 
                    AND date >= NOW() - INTERVAL '30 days'
                    ORDER BY date DESC
                """, (user_id,))
                
                transactions = cur.fetchall()
                print(f"Debug - Found {len(transactions)} transactions")  # Debug log
                
                if not transactions:
                    raise HTTPException(status_code=400, detail="No recent transactions found")
                
                # Convert to DataFrame
                df = pd.DataFrame(transactions, columns=['transaction_id', 'account_id', 'date', 'amount', 'name', 'category', 'user_id'])
                df['transaction_date'] = pd.to_datetime(df['date'])
                
                # Detect unusual transactions
                unusual_transactions = detect_unusual_transactions(df)
                print(f"Debug - Found {len(unusual_transactions)} unusual transactions")  # Debug log
                
                # Detect additional income
                additional_income, income_details = detect_additional_income(df)
                print(f"Debug - Additional income: {additional_income}")  # Debug log
                
                return {
                    "unusual_transactions": unusual_transactions,
                    "additional_income": additional_income,
                    "income_details": income_details
                }
    except HTTPException as he:
        print(f"Debug - HTTP Exception: {str(he)}")  # Debug log
        raise he
    except Exception as e:
        print(f"Debug - Unexpected error: {str(e)}")  # Debug log
        raise HTTPException(status_code=500, detail=str(e))

# Add MCP WebSocket endpoint
@app.websocket("/ws/mcp")
async def websocket_endpoint(websocket: WebSocket):
    await mcp_server.handle_websocket(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 