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
    bcrypt__rounds=12  # Can adjust the rounds for security/performance
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

class UserLogin(BaseModel):
    email: str
    password: str

# Initialize database
def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            username VARCHAR(50) UNIQUE NOT NULL,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            hashed_password VARCHAR(255) NOT NULL
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

init_db()

@app.post("/register")
async def register(user: UserCreate):
    conn = psycopg2.connect(DATABASE_URL)
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
            INSERT INTO users (email, username, first_name, last_name, hashed_password)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, email, username, first_name, last_name
        """, (
            user.email, user.username, user.first_name, user.last_name, hashed_password
        ))
        
        new_user = cur.fetchone()
        conn.commit()

        # Create token
        token_data = {"sub": user.email}
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
        
        return {
            "access_token": token,
            "user": {
                "email": new_user["email"],
                "username": new_user["username"],
                "first_name": new_user["first_name"],
                "last_name": new_user["last_name"]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.post("/login")
async def login(user: UserLogin):
    conn = psycopg2.connect(DATABASE_URL)
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
                "last_name": db_user["last_name"]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/profile")
async def get_profile(token: str = Depends(get_token_from_header)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            cur.execute("""
                SELECT email, username, first_name, last_name
                FROM users
                WHERE email = %s
            """, (email,))
            user = cur.fetchone()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return user
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