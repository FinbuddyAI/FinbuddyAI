import requests
import json
import random
from datetime import datetime, timedelta
import uuid

# API configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "email": "test@example.com",
    "password": "testpassword123"
}

def login():
    """Login and get access token"""
    response = requests.post(f"{BASE_URL}/login", json=TEST_USER)
    if response.status_code != 200:
        raise Exception("Login failed")
    return response.json()["access_token"]

def create_test_transaction(token, amount, category, name):
    """Create a test transaction"""
    headers = {"Authorization": f"Bearer {token}"}
    
    transaction = {
        "transaction_id": str(uuid.uuid4()),
        "account_id": "test_account",
        "date": datetime.now().isoformat(),
        "amount": amount,
        "name": name,
        "category": category,
        "user_id": 1  # Assuming test user has ID 1
    }
    
    response = requests.post(
        f"{BASE_URL}/transactions",
        json=transaction,
        headers=headers
    )
    
    if response.status_code != 200:
        raise Exception("Failed to create transaction")
    
    return response.json()

def test_unusual_transaction():
    """Test goal refinement with unusual transaction"""
    print("Testing goal refinement with unusual transaction...")
    
    # Login
    token = login()
    
    # Create a large unusual transaction
    create_test_transaction(
        token,
        -1000.00,  # Large negative amount
        "Shopping",
        "Luxury Purchase"
    )
    
    # Detect unusual activity
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/goals/detect-unusual",
        headers=headers
    )
    
    if response.status_code != 200:
        raise Exception("Failed to detect unusual activity")
    
    unusual_activity = response.json()
    print("\nUnusual activity detected:")
    print(json.dumps(unusual_activity, indent=2))
    
    # Adjust goals
    response = requests.post(
        f"{BASE_URL}/goals/adjust",
        headers=headers
    )
    
    if response.status_code != 200:
        raise Exception("Failed to adjust goals")
    
    adjustment = response.json()
    print("\nGoal adjustment result:")
    print(json.dumps(adjustment, indent=2))
    
    # Get adjustment history
    response = requests.get(
        f"{BASE_URL}/goals/history",
        headers=headers
    )
    
    if response.status_code != 200:
        raise Exception("Failed to get adjustment history")
    
    history = response.json()
    print("\nAdjustment history:")
    print(json.dumps(history, indent=2))

def test_additional_income():
    """Test goal refinement with additional income"""
    print("\nTesting goal refinement with additional income...")
    
    # Login
    token = login()
    
    # Create additional income transaction
    create_test_transaction(
        token,
        500.00,  # Positive amount for income
        "Income",
        "Bonus Payment"
    )
    
    # Detect unusual activity
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/goals/detect-unusual",
        headers=headers
    )
    
    if response.status_code != 200:
        raise Exception("Failed to detect unusual activity")
    
    unusual_activity = response.json()
    print("\nUnusual activity detected:")
    print(json.dumps(unusual_activity, indent=2))
    
    # Adjust goals
    response = requests.post(
        f"{BASE_URL}/goals/adjust",
        headers=headers
    )
    
    if response.status_code != 200:
        raise Exception("Failed to adjust goals")
    
    adjustment = response.json()
    print("\nGoal adjustment result:")
    print(json.dumps(adjustment, indent=2))

if __name__ == "__main__":
    try:
        # Test with unusual transaction
        test_unusual_transaction()
        
        # Test with additional income
        test_additional_income()
        
        print("\nAll tests completed successfully!")
    except Exception as e:
        print(f"\nTest failed: {str(e)}") 