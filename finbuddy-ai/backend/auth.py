from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"

security = HTTPBearer()

def get_token_from_header(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return credentials.credentials

def get_db_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

def convert_to_dict(row):
    """Convert RealDictRow to regular dictionary"""
    if row is None:
        return None
    return dict(row)

async def get_current_user(token: str = Depends(get_token_from_header)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            cur.execute("""
                SELECT id, email, username, first_name, last_name, phone_number
                FROM users
                WHERE email = %s
            """, (email,))
            user = cur.fetchone()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            user_dict = convert_to_dict(user)
            print(f"Debug - User object structure: {user_dict}")  # Debug log
            return user_dict
        finally:
            cur.close()
            conn.close()
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print(f"Debug - Error in get_current_user: {str(e)}")  # Debug log
        raise HTTPException(status_code=500, detail=str(e)) 