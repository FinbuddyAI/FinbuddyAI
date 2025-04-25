import requests
import json
from datetime import datetime

# API endpoints
BASE_URL = "http://localhost:8000"

def get_auth_token():
    """Get authentication token for john.doe@gmail.com"""
    response = requests.post(f"{BASE_URL}/login", json={
        "email": "john.doe@gmail.com",
        "password": "password123"
    })
    
    if response.status_code != 200:
        raise Exception(f"Login failed: {response.text}")
    
    return response.json()["access_token"]

def create_test_transaction(headers, amount, category, name):
    """Create a test transaction via API"""
    transaction_data = {
        "amount": amount,
        "category": category,
        "name": name,
        "date": datetime.now().strftime("%Y-%m-%d")
    }
    
    response = requests.post(f"{BASE_URL}/transactions/create", headers=headers, json=transaction_data)
    if response.status_code != 200:
        print(f"Failed to create transaction: {response.text}")
        return False
    return True

def test_transactions_and_anomalies():
    """Test creating transactions and detecting anomalies"""
    try:
        # Get auth token
        token = get_auth_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        print("\n=== Creating Test Transactions ===")
        
        # 1. Create unusual large expense
        print("\nCreating unusual large expense...")
        create_test_transaction(
            headers=headers,
            amount=-1000.00,  # Large expense
            category="shopping",
            name="Luxury Purchase"
        )
        
        # Create some normal transactions
        print("\nCreating normal transactions...")
        create_test_transaction(
            headers=headers,
            amount=-50.00,
            category="food",
            name="Restaurant"
        )
        create_test_transaction(
            headers=headers,
            amount=-30.00,
            category="transportation",
            name="Taxi"
        )
        
        # Create additional income
        print("\nCreating additional income...")
        create_test_transaction(
            headers=headers,
            amount=2000.00,
            category="Income",
            name="Bonus"
        )
        
        # 2. Check for unusual activity
        print("\nChecking for unusual activity...")
        response = requests.post(f"{BASE_URL}/goals/detect-unusual", headers=headers)
        if response.status_code == 200:
            result = response.json()
            print("\nUnusual Activity Detection Result:")
            print(json.dumps(result, indent=2))
        else:
            print(f"Failed to detect unusual activity: {response.text}")
        
        # 3. Trigger goal adjustment
        print("\nTriggering goal adjustment...")
        response = requests.post(f"{BASE_URL}/goals/adjust", headers=headers)
        if response.status_code == 200:
            result = response.json()
            print("\nGoal Adjustment Result:")
            print(json.dumps(result, indent=2))
        else:
            print(f"Failed to adjust goals: {response.text}")
        
        # 4. Get adjustment history
        print("\nGetting adjustment history...")
        response = requests.get(f"{BASE_URL}/goals/history", headers=headers)
        if response.status_code == 200:
            result = response.json()
            print("\nAdjustment History:")
            print(json.dumps(result, indent=2))
        else:
            print(f"Failed to get adjustment history: {response.text}")
            
    except Exception as e:
        print(f"Error in test: {str(e)}")

if __name__ == "__main__":
    test_transactions_and_anomalies() 