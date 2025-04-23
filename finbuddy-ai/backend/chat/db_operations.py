from typing import Dict, List, Any
from sqlalchemy import text
from database import get_db

async def query_database(query: str) -> List[Dict[str, Any]]:
    """
    Execute a SQL query on the database and return the results.
    
    Args:
        query: The SQL query to execute
        
    Returns:
        List[Dict[str, Any]]: The query results as a list of dictionaries
    """
    try:
        db = next(get_db())
        result = db.execute(text(query))
        return [dict(row) for row in result]
    except Exception as e:
        print(f"Error executing query: {str(e)}")
        raise

async def update_database(query: str) -> int:
    """
    Execute an update query on the database and return the number of affected rows.
    
    Args:
        query: The SQL update query to execute
        
    Returns:
        int: The number of affected rows
    """
    try:
        db = next(get_db())
        result = db.execute(text(query))
        db.commit()
        return result.rowcount
    except Exception as e:
        print(f"Error executing update: {str(e)}")
        raise 