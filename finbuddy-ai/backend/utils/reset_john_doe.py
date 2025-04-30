from transaction_manager import delete_user_data, setup_database
from goals_manager import delete_goals_data, setup_goals
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

def get_user_id():
    """Get John Doe's user ID"""
    conn = psycopg2.connect(os.getenv("DATABASE_URL"), cursor_factory=RealDictCursor)
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT id FROM users WHERE email = %s", ("john.doe@gmail.com",))
        result = cur.fetchone()
        return result["id"] if result else None
    finally:
        cur.close()
        conn.close()

def reset_john_doe():
    """Reset John Doe's data and reinitialize it"""
    print("Starting reset of John Doe's data...")
    
    # First get the user ID
    user_id = get_user_id()
    if not user_id:
        print("User not found, setting up fresh data...")
        setup_database()
        user_id = get_user_id()
    
    # Delete existing goals first (due to foreign key constraints)
    delete_goals_data()
    print("Deleted existing goals")
    
    # Then delete user data
    delete_user_data()
    print("Deleted existing user data")
    
    # Set up fresh data
    setup_database()
    print("Set up fresh user data")
    
    # Set up fresh goals
    setup_goals()
    print("Set up fresh goals")
    
    print("Reset complete!")

if __name__ == "__main__":
    reset_john_doe() 