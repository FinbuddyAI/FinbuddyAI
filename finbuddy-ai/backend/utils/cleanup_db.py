import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def cleanup_database():
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        
        # Drop all tables in the correct order (respecting foreign key constraints)
        cur.execute("DROP TABLE IF EXISTS transactions CASCADE")
        cur.execute("DROP TABLE IF EXISTS bank_accounts CASCADE")
        cur.execute("DROP TABLE IF EXISTS users CASCADE")
        
        conn.commit()
        print("Database cleanup completed successfully")
    except Exception as e:
        print(f"Error during database cleanup: {str(e)}")
        raise
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("WARNING: This will delete all data in the database!")
    confirmation = input("Are you sure you want to proceed? (yes/no): ")
    
    if confirmation.lower() == 'yes':
        cleanup_database()
    else:
        print("Database cleanup cancelled") 