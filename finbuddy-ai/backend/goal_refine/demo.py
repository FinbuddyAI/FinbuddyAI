# ./Finbuddy_LLM/demo/simulation.py

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import matplotlib.pyplot as plt
from tabulate import tabulate
import random

from goal_adjuster import adjust_goals, format_adjustment_report
from goal_history_tracker import GoalHistoryTracker

def setup_environment():
    """Set up environment"""
    # Create necessary directories
    os.makedirs("./data", exist_ok=True)
    os.makedirs("./result", exist_ok=True)
    
    # Check data files
    if not os.path.exists("sample_transactions.json") or not os.path.exists("sample_goals.csv"):
        print("Sample data files not found. Please run create_sample_data.py first.")
        return False
    
    return True

def load_data():
    """Load data"""
    # Load transaction data
    try:
        with open("sample_transactions.json", "r") as f:
            transaction_data = json.load(f)
        
        # Convert to DataFrame
        transactions_df = pd.DataFrame(transaction_data["transactions"])
        transactions_df['transaction_date'] = pd.to_datetime(transactions_df['date'])
        
        # Ensure amount column is float
        transactions_df['amount'] = transactions_df['amount'].astype(float)
    except:
        # If JSON loading fails, try loading CSV (for backward compatibility)
        transactions_df = pd.read_csv("sample_expenses.csv")
        transactions_df['transaction_date'] = pd.to_datetime(transactions_df['transaction_date'])
        
        # Convert expense amounts to negative
        if 'category' in transactions_df.columns:
            mask = transactions_df['category'] != 'Income'
            transactions_df.loc[mask, 'amount'] = -transactions_df.loc[mask, 'amount']
    
    # Load goals data
    goals_df = pd.read_csv("sample_goals.csv")
    
    # Initialize history tracker
    history_tracker = GoalHistoryTracker()

    # Check for historical adjustment records
    active_goals = history_tracker.get_active_goals()
    
    if active_goals:
        print("Detected historical goal adjustment records, using latest active goal settings")
        goals_df = pd.DataFrame(active_goals)
    
    return transactions_df, goals_df, history_tracker

def generate_daily_transactions(base_date, categories):
    """Generate daily transactions"""
    # Generate 1-4 transactions
    num_transactions = np.random.randint(1, 5)
    transactions = []
    
    # Common merchants
    merchants = {
        "Food & Drink": ["Quanjude", "McDonald's", "Pizza Hut", "Starbucks", "Bubble Tea Shop", "Local Restaurant", "Cafeteria"],
        "Shopping": ["Taobao", "JD.com", "Tmall", "Suning", "Physical Store", "Supermarket"],
        "Transportation": ["Didi", "Bus", "Subway", "High-speed Rail", "Airplane", "Bike Sharing"],
        "Entertainment": ["Movie", "KTV", "Gaming", "Gym", "Concert"],
        "Utilities": ["Water Bill", "Electric Bill", "Mobile Bill", "Internet Fee"],
        "Health": ["Hospital", "Pharmacy", "Gym Membership"],
        "Education": ["Online Course", "Books", "Training", "Tuition"]
    }
    
    # Income sources
    income_sources = ["Paycheck", "Bonus", "Freelance", "Investment", "Gift", "Refund", "Side Hustle"]
    
    # Randomly decide if there's income (15% probability)
    has_income = random.random() < 0.15
    
    # Generate transactions
    for _ in range(num_transactions):
        # Randomly select category, some categories have higher probability
        prob = [random.randint(1, 100) for _ in range(len(categories))]
        p = [_ / sum(prob) for _ in prob]
        category = np.random.choice(
            categories, 
            p=p  # Adjust probability to reflect real spending patterns
        )
        
        # Set amount range based on category
        amount_ranges = {
            "Food & Drink": (20, 500),
            "Shopping": (50, 1000),
            "Transportation": (5, 100),
            "Entertainment": (30, 300),
            "Utilities": (50, 500),
            "Health": (50, 1000),
            "Education": (100, 2000)
        }
        
        # Set amount and merchant
        amount = np.random.uniform(*amount_ranges.get(category, (50, 500)))
        merchant = np.random.choice(merchants.get(category, ["Unknown"]))
        
        # Set transaction time (random time during the day)
        hour = np.random.randint(9, 22)
        minute = np.random.randint(0, 60)
        transaction_date = base_date.replace(hour=hour, minute=minute)
        
        # Generate transaction description
        descriptions = [
            f"{merchant} payment",
            f"Purchase at {merchant}",
            f"{category} expense",
            f"Payment for {category}"
        ]
        description = np.random.choice(descriptions)
        
        # Special case: occasional large expenses
        if np.random.random() < 0.1:  # 10% probability for special cases
            if category == "Food & Drink":
                amount = amount * 5  # Large dining expense
                description = f"Group dinner at {merchant}"
            elif category == "Shopping":
                amount = amount * 3  # Large shopping expense
                description = f"Major purchase at {merchant}"
        
        # Expense amounts are negative
        transactions.append({
            "transaction_id": f"tx_{random.randint(1000, 9999)}",
            "account_id": "acct_123",
            "date": transaction_date.strftime("%Y-%m-%d"),
            "transaction_date": transaction_date,
            "amount": -amount,  # Expenses are negative
            "name": merchant,
            "merchant": merchant,
            "category": category,
            "description": description
        })
    
    # If there's income today
    if has_income:
        income_source = random.choice(income_sources)
        
        # Set income amount
        if income_source == "Paycheck":
            amount = round(random.uniform(3000, 10000), 2)
        elif income_source == "Bonus":
            amount = round(random.uniform(1000, 5000), 2)
        elif income_source in ["Freelance", "Side Hustle"]:
            amount = round(random.uniform(500, 3000), 2)
        else:
            amount = round(random.uniform(100, 1000), 2)
        
        # Set transaction time (random time during work hours)
        hour = np.random.randint(9, 17)  # Work hours
        minute = np.random.randint(0, 60)
        transaction_date = base_date.replace(hour=hour, minute=minute)
        
        transactions.append({
            "transaction_id": f"tx_{random.randint(1000, 9999)}",
            "account_id": "acct_123",
            "date": transaction_date.strftime("%Y-%m-%d"),
            "transaction_date": transaction_date,
            "amount": amount,  # Income is positive
            "name": income_source,
            "merchant": income_source,
            "category": "Income",
            "description": f"{income_source} received"
        })
    
    return transactions

def check_goal_adjustment_trigger(recent_transactions, goals_df):
    """Check if goal adjustment should be triggered"""
    # Separate expenses and income
    expenses = recent_transactions[recent_transactions['amount'] < 0].copy()
    income = recent_transactions[recent_transactions['amount'] > 0].copy()
    
    # Convert expenses to positive for calculation
    expenses['amount'] = expenses['amount'].abs()
    
    total_expense = expenses['amount'].sum() if not expenses.empty else 0
    total_income = income['amount'].sum() if not income.empty else 0
    
    # Calculate total target amount
    total_target = goals_df['target_amount'].sum()
    
    # Check if any category exceeds 50% of budget
    category_expenses = expenses.groupby('category')['amount'].sum() if not expenses.empty else pd.Series()
    
    trigger_reasons = []
    
    # Check if total expenses exceed 40% of total target
    if total_expense > total_target * 0.4:
        trigger_reasons.append(f"Total expenses (¥{total_expense:.2f}) have reached {(total_expense/total_target*100):.1f}% of total target (¥{total_target:.2f})")
    
    # Check each category for overspending
    for category, expense in category_expenses.items():
        category_target = goals_df[goals_df['category'] == category]['target_amount'].values
        if len(category_target) > 0:
            target = category_target[0]
            if expense > target * 0.5:
                trigger_reasons.append(f"{category} category expenses (¥{expense:.2f}) have reached {(expense/target*100):.1f}% of target (¥{target:.2f})")
    
    # Check for unusually large transactions (single transaction exceeding 30% of category target)
    for _, tx in expenses.iterrows():
        category = tx['category']
        amount = tx['amount']
        category_target = goals_df[goals_df['category'] == category]['target_amount'].values
        
        if len(category_target) > 0:
            target = category_target[0]
            if amount > target * 0.3:
                trigger_reasons.append(f"Detected large transaction: {tx['transaction_date'].strftime('%Y-%m-%d')} {category} ¥{amount:.2f} (exceeds {(amount/target*100):.1f}% of category target)")
    
    # Check for additional income
    if total_income > 0:
        trigger_reasons.append(f"Detected additional income: ¥{total_income:.2f}")
    
    return trigger_reasons

def run_simulation():
    """Run 5-day spending simulation"""
    # Set up environment
    if not setup_environment():
        return
    
    # Load data
    transactions_df, goals_df, history_tracker = load_data()
    
    # Set simulation start date
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Display initial goals
    print("\n=== Current Financial Goals ===")
    print(tabulate(goals_df[['category', 'target_amount', 'period', 'description']], 
                  headers='keys', tablefmt='pretty', showindex=False))
    
    # Track all new transactions
    all_new_transactions = []
    cumulative_expenses = {}
    total_income = 0
    
    # Run 5-day simulation
    for day in range(5):
        current_date = start_date + timedelta(days=day)
        print(f"\n\n=== Day {day+1}: {current_date.strftime('%Y-%m-%d')} ===")
        
        # Generate daily transactions
        daily_transactions = generate_daily_transactions(
            current_date, 
            goals_df['category'].unique()
        )
        
        # Display daily transactions
        print(f"\nToday's Transactions ({len(daily_transactions)}):")
        transactions_df = pd.DataFrame(daily_transactions)
        
        # Separate expenses and income for display
        expenses = transactions_df[transactions_df['amount'] < 0].copy()
        income = transactions_df[transactions_df['amount'] > 0].copy()
        
        # Display expenses
        if not expenses.empty:
            print("\nExpenses:")
            expenses['amount'] = expenses['amount'].abs()  # Convert to positive for display
            print(tabulate(
                expenses[['transaction_date', 'category', 'merchant', 'amount', 'description']], 
                headers=['Time', 'Category', 'Merchant', 'Amount', 'Description'], 
                tablefmt='pretty', 
                showindex=False
            ))
        
        # Display income
        if not income.empty:
            print("\nIncome:")
            print(tabulate(
                income[['transaction_date', 'merchant', 'amount', 'description']], 
                headers=['Time', 'Source', 'Amount', 'Description'], 
                tablefmt='pretty', 
                showindex=False
            ))
        
        # Add to all transactions
        all_new_transactions.extend(daily_transactions)
        
        # Update cumulative expenses and income
        for tx in daily_transactions:
            amount = tx['amount']
            category = tx['category']
            
            if amount < 0:  # Expense
                if category in cumulative_expenses:
                    cumulative_expenses[category] += amount
                else:
                    cumulative_expenses[category] = amount
            else:  # Income
                total_income += amount
        
        # Display cumulative expenses
        print("\nCumulative Expenses:")
        cumulative_data = []
        for category, amount in cumulative_expenses.items():
            target = goals_df[goals_df['category'] == category]['target_amount'].values
            if len(target) > 0:
                target_value = target[0]
                percentage = (abs(amount) / target_value) * 100
                status = "✓" if percentage <= 100 else "❗"
                cumulative_data.append([category, abs(amount), target_value, f"{percentage:.1f}%", status])
        
        print(tabulate(
            sorted(cumulative_data, key=lambda x: x[3], reverse=True),
            headers=['Category', 'Cumulative', 'Target', 'Percentage', 'Status'],
            tablefmt='pretty'
        ))
        
        # Display cumulative income
        print(f"\nCumulative Additional Income: ¥{total_income:.2f}")
        
        # # Combine new transactions with existing ones
        # updated_transactions_df = pd.concat([
        #     transactions_df, 
        #     pd.DataFrame(all_new_transactions)
        # ]).reset_index(drop=True)
        
        # Check if goal adjustment is needed
        recent_transactions = pd.DataFrame(all_new_transactions)
        trigger_reasons = check_goal_adjustment_trigger(recent_transactions, goals_df)

        print("#################################")
        print(trigger_reasons)
        print("#################################")
        
        if trigger_reasons:
            print("\n\n=== Goal Adjustment Triggered ===")
            for reason in trigger_reasons:
                print(f"- {reason}")
            
            print("\nAnalyzing spending patterns and income changes to adjust goals...")

            # print("#######################################")
            # print(all_new_transactions)
            # print("#################################")
            
            # Perform goal adjustment
            adjusted_goals_df, adjustment_result = adjust_goals(
                recent_transactions,
                trigger_reasons,
                goals_df
            )
            
            # Display adjustment results
            if "error" in adjustment_result:
                print(f"\nGoal adjustment failed: {adjustment_result['error']}")
            else:
                print("\nGoal adjustment completed!")
                print("\n=== Adjusted Goals ===")
                print(tabulate(
                    adjusted_goals_df[['category', 'target_amount', 'period', 'description']], 
                    headers='keys', 
                    tablefmt='pretty', 
                    showindex=False
                ))
                
                # Save adjustment report
                report = format_adjustment_report(adjustment_result)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                report_file = f"./result/adjustment_report_{timestamp}.md"
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write(report)
                print(f"\nDetailed adjustment report saved to: {report_file}")
                
                # Save adjustment history
                trigger_event = "Spending patterns and income changes analysis"
                adjustment_id = history_tracker.save_adjustment(
                    goals_df, 
                    adjusted_goals_df, 
                    adjustment_result,
                    trigger_event=trigger_event
                )
                print(f"\nAdjustment record saved, adjustment ID: {adjustment_id}")
                
                # Update current goals
                goals_df = adjusted_goals_df
        else:
            print("\nCurrent spending patterns and income status are normal, no goal adjustment needed.")
        
        input("\nPress Enter to continue to next day...")
    
    print("\nSimulation complete! All reports saved to ./result/ directory")

if __name__ == "__main__":    
    # Run 5-day simulation
    run_simulation()
    