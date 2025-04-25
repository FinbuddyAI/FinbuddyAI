import requests
import json
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

# API endpoints
BASE_URL = "http://localhost:8000"

def login():
    """Login and get token"""
    response = requests.post(
        f"{BASE_URL}/login",
        json={
            "email": "john.doe@gmail.com",
            "password": "password123"
        }
    )
    return response.json()["access_token"]

def create_transaction(token, amount, category, name, days_ago=0):
    """Create a transaction"""
    date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
    response = requests.post(
        f"{BASE_URL}/transactions/create",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "amount": amount,
            "category": category,
            "name": name,
            "date": date
        }
    )
    return response.json()

def detect_anomalies(token):
    """Detect anomalies in transactions"""
    response = requests.post(
        f"{BASE_URL}/goals/detect-unusual",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()

def main():
    # Login
    token = login()
    print("Logged in successfully")
    
    # First, create a baseline of normal transactions in the same category
    print("\nCreating baseline transactions...")
    for i in range(5):  # Create 5 normal transactions to establish baseline
        create_transaction(token, -100.00, "Shopping", "Clothing Store", i+1)
    
    # Create an unusually large transaction that should trigger detection
    # This will be > mean + 2*std of the baseline transactions
    print("\nCreating unusual transaction...")
    create_transaction(token, -1000.00, "Shopping", "Luxury Watch Store", 0)  # Today
    
    # Create some other normal transactions in different categories
    print("\nCreating other normal transactions...")
    create_transaction(token, -50.00, "Food", "Grocery Store", 1)
    create_transaction(token, -25.00, "Transportation", "Gas Station", 2)
    
    # Detect anomalies
    print("\nDetecting anomalies...")
    anomalies = detect_anomalies(token)
    print("\nAnomaly Detection Results:")
    print(json.dumps(anomalies, indent=2))

if __name__ == "__main__":
    main() 