import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def get_json_path(filename):
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Join it with the filename to get the full path
    return os.path.join(script_dir, filename)

def insert_spending_goals(user_id):
    # Read spending goals from the JSON file
    with open(get_json_path("spending_goals.json"), "r") as f:
        data = json.load(f)
        goals = data["spending_goals"]
    
    conn = psycopg2.connect(os.getenv("DATABASE_URL"), cursor_factory=RealDictCursor)
    cur = conn.cursor()
    
    try:
        for goal in goals:
            cur.execute("""
                INSERT INTO spending_goals (
                    goal_id, user_id, category, target_amount, current_amount, created_at, last_adjusted_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (goal_id) DO NOTHING
            """, (
                goal["id"],
                user_id,
                goal["category"],
                goal["target_amount"],
                goal["current_amount"],
                goal["created_at"],
                goal["last_adjusted_at"]
            ))
        
        conn.commit()
        print(f"Successfully inserted {len(goals)} spending goals")
    except Exception as e:
        print(f"Error inserting spending goals: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def insert_saving_goals(user_id):
    # Read saving goals from the JSON file
    with open(get_json_path("saving_goals.json"), "r") as f:
        data = json.load(f)
        goals = data["saving_goals"]
    
    conn = psycopg2.connect(os.getenv("DATABASE_URL"), cursor_factory=RealDictCursor)
    cur = conn.cursor()
    
    try:
        for goal in goals:
            cur.execute("""
                INSERT INTO saving_goals (
                    goal_id, user_id, category, target_amount, current_amount, target_date, created_at, last_adjusted_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (goal_id) DO NOTHING
            """, (
                goal["id"],
                user_id,
                goal["category"],
                goal["target_amount"],
                goal["current_amount"],
                goal["date"],
                goal["created_at"],
                goal["last_adjusted_at"]
            ))
        
        conn.commit()
        print(f"Successfully inserted {len(goals)} saving goals")
    except Exception as e:
        print(f"Error inserting saving goals: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def delete_goals_data():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"), cursor_factory=RealDictCursor)
    cur = conn.cursor()
    
    try:
        # First get the user ID
        cur.execute("SELECT id FROM users WHERE email = %s", ("john.doe@gmail.com",))
        result = cur.fetchone()
        
        if result:
            user_id = result["id"]
            # Delete spending goals
            cur.execute("DELETE FROM spending_goals WHERE user_id = %s", (user_id,))
            # Delete saving goals
            cur.execute("DELETE FROM saving_goals WHERE user_id = %s", (user_id,))
            conn.commit()
            print("Successfully deleted goals data")
        else:
            print("User not found")
    except Exception as e:
        print(f"Error deleting goals data: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def setup_goals():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"), cursor_factory=RealDictCursor)
    cur = conn.cursor()
    
    try:
        # Get user ID
        cur.execute("SELECT id FROM users WHERE email = %s", ("john.doe@gmail.com",))
        result = cur.fetchone()
        
        if result:
            user_id = result["id"]
            # Insert spending goals
            insert_spending_goals(user_id)
            # Insert saving goals
            insert_saving_goals(user_id)
        else:
            print("User not found")
    except Exception as e:
        print(f"Error setting up goals: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "setup":
            setup_goals()
        elif sys.argv[1] == "delete":
            delete_goals_data()
        else:
            print("Invalid command. Use 'setup' or 'delete'")
    else:
        print("Please provide a command: 'setup' or 'delete'") 