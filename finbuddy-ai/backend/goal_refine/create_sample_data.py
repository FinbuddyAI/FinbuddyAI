# ./Finbuddy_LLM/demo/create_sample_data.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os
import json

# Create sample spending categories and merchants
CATEGORIES = [
    "Food & Drink", "Shopping", "Transportation", "Housing", "Entertainment", 
    "Education", "Healthcare", "Travel", "Electronics", "Daily Necessities"
]

MERCHANTS = {
    "Food & Drink": ["KFC", "McDonald's", "Pizza Hut", "Starbucks", "Bubble Tea Shop", "Local Restaurant", "Cafeteria"],
    "Shopping": ["Taobao", "JD.com", "Tmall", "Suning", "Physical Store", "Supermarket"],
    "Transportation": ["Didi", "Bus", "Subway", "High-speed Rail", "Airplane", "Bike Sharing"],
    "Housing": ["Rent", "Water Bill", "Electricity Bill", "Property Fee", "Internet Fee"],
    "Entertainment": ["Movie", "KTV", "Gaming", "Gym", "Concert"],
    "Education": ["Online Course", "Books", "Training", "Tuition"],
    "Healthcare": ["Medicine", "Clinic", "Health Check"],
    "Travel": ["Hotel", "Attraction Ticket", "Tour Group", "Souvenir"],
    "Electronics": ["Phone", "Computer", "Camera", "Accessories"],
    "Daily Necessities": ["Toiletries", "Cosmetics", "Cleaning Supplies", "Kitchenware"]
}

# Income sources
INCOME_SOURCES = [
    "Paycheck", "Bonus", "Freelance", "Investment", "Gift", "Refund", "Side Hustle", "Other Income"
]

# Create sample user goals
def create_sample_goals():
    goals = [
        {"category": "Food & Drink", "target_amount": 1500, "period": "monthly", "description": "Control monthly dining expenses"},
        {"category": "Shopping", "target_amount": 2000, "period": "monthly", "description": "Reduce impulse shopping"},
        {"category": "Transportation", "target_amount": 500, "period": "monthly", "description": "Prioritize public transportation"},
        {"category": "Entertainment", "target_amount": 800, "period": "monthly", "description": "Reasonable entertainment arrangement"}
    ]
    
    goals_df = pd.DataFrame(goals)
    goals_df.to_csv("./sample_goals.csv", index=False)
    print(f"Sample goals data created: sample_goals.csv")
    return goals_df

# Create sample transaction and income data
def create_sample_transactions(num_records=100):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)
    
    transactions = []
    account_id = "acct_123"
    
    # Create account information
    account = {
        "account_id": account_id,
        "name": "Primary Checking",
        "mask": "4321",
        "balances": {
            "available": 1500.00,
            "current": 1500.00,
            "iso_currency_code": "USD"
        }
    }
    
    # Generate transaction records
    for i in range(num_records):
        # Randomly decide if it's an expense or income (80% chance expense, 20% chance income)
        is_expense = random.random() < 0.8
        
        # Random date
        random_days = random.randint(0, 60)
        transaction_date = end_date - timedelta(days=random_days)
        date_str = transaction_date.strftime("%Y-%m-%d")
        
        if is_expense:
            # Expense record
            category = random.choice(CATEGORIES)
            merchant = random.choice(MERCHANTS.get(category, ["Unknown"]))
            
            # Set reasonable amount ranges based on category
            if category in ["Housing", "Travel", "Electronics"]:
                amount = round(random.uniform(500, 5000), 2)
            elif category in ["Food & Drink", "Shopping", "Healthcare"]:
                amount = round(random.uniform(50, 500), 2)
            else:
                amount = round(random.uniform(10, 200), 2)
            
            # Expense amounts are negative
            amount = -amount
            
            transaction = {
                "transaction_id": f"tx_{i+1:03d}",
                "account_id": account_id,
                "date": date_str,
                "amount": amount,
                "name": merchant,
                "category": category
            }
        else:
            # Income record
            income_source = random.choice(INCOME_SOURCES)
            
            # Set income amount ranges
            if income_source == "Paycheck":
                amount = round(random.uniform(3000, 10000), 2)
            elif income_source == "Bonus":
                amount = round(random.uniform(1000, 5000), 2)
            elif income_source in ["Freelance", "Side Hustle"]:
                amount = round(random.uniform(500, 3000), 2)
            else:
                amount = round(random.uniform(100, 1000), 2)
            
            transaction = {
                "transaction_id": f"tx_{i+1:03d}",
                "account_id": account_id,
                "date": date_str,
                "amount": amount,  # Income is positive
                "name": income_source,
                "category": "Income"
            }
        
        transactions.append(transaction)
    
    # Sort by date
    transactions.sort(key=lambda x: x["date"], reverse=True)
    
    # Create complete data structure
    data = {
        "accounts": [account],
        "transactions": transactions
    }
    
    # Save as JSON file
    with open("sample_transactions.json", "w") as f:
        json.dump(data, f, indent=2)
    
    # Also save as CSV for compatibility with existing code
    df = pd.DataFrame(transactions)
    
    # Add columns for compatibility with old code
    df["transaction_date"] = df["date"]
    df["merchant"] = df["name"]
    df["description"] = df.apply(lambda row: f"{row['name']} {'payment' if row['amount'] < 0 else 'deposit'}", axis=1)
    
    # Ensure amount column is absolute value for compatibility with old code
    df["amount"] = df["amount"].abs()
    
    df.to_csv("sample_expenses.csv", index=False)
    
    print(f"Sample transaction data created: sample_transactions.json and sample_expenses.csv")
    print(f"Total transactions: {len(transactions)}")
    print(f"Expenses: {len([t for t in transactions if t['amount'] < 0])}")
    print(f"Incomes: {len([t for t in transactions if t['amount'] > 0])}")
    
    return data

if __name__ == "__main__":
    create_sample_goals()
    create_sample_transactions(100)