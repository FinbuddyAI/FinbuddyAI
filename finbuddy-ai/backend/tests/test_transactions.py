import pytest
import pandas as pd
from datetime import datetime, timedelta
from goal_refine.goal_adjuster import detect_unusual_transactions, detect_additional_income, adjust_goals

def test_detect_unusual_transactions():
    # Create test data
    test_data = {
        'transaction_id': ['tx1', 'tx2', 'tx3', 'tx4', 'tx5', 'tx6', 'tx7', 'tx8'],
        'transaction_date': [
            datetime.now() - timedelta(days=i) for i in range(8)
        ],
        'amount': [-100.0, -120.0, -150.0, -5000.0,  # Food transactions
                  -200.0, -250.0, -300.0, -3000.0],  # Transportation transactions
        'category': ['Food', 'Food', 'Food', 'Food',
                    'Transportation', 'Transportation', 'Transportation', 'Transportation'],
        'name': ['Grocery Store', 'Restaurant', 'Cafe', 'Luxury Restaurant',
                'Public Transit', 'Taxi', 'Ride Share', 'Luxury Car Rental']
    }
    
    df = pd.DataFrame(test_data)
    
    # Test unusual transaction detection
    unusual_transactions = detect_unusual_transactions(df)
    
    # Verify that large transactions are detected
    assert len(unusual_transactions) == 2, "Should detect 2 unusual transactions"
    
    # Verify the specific transactions are detected
    unusual_amounts = [tx['amount'] for tx in unusual_transactions]
    assert -5000.0 in unusual_amounts, "Large food purchase should be detected"
    assert -3000.0 in unusual_amounts, "Large transportation expense should be detected"
    
    # Verify the categories are correct
    unusual_categories = [tx['category'] for tx in unusual_transactions]
    assert 'Food' in unusual_categories, "Food category should be detected"
    assert 'Transportation' in unusual_categories, "Transportation category should be detected"

def test_detect_additional_income():
    # Create test data
    test_data = {
        'transaction_id': ['tx1', 'tx2', 'tx3', 'tx4', 'tx5'],
        'transaction_date': [
            datetime.now() - timedelta(days=i) for i in range(5)
        ],
        'amount': [1000.0, 2000.0, 3000.0, 4000.0, 5000.0],  # All positive amounts
        'category': ['Salary', 'Bonus', 'Investment', 'Gift', 'Other'],
        'name': ['Monthly Salary', 'Yearly Bonus', 'Stock Dividend', 'Birthday Gift', 'Misc Income']
    }
    
    df = pd.DataFrame(test_data)
    
    # Test additional income detection
    additional_income, total_income = detect_additional_income(df)
    
    # Verify all income transactions are detected
    assert len(additional_income) == 5, "Should detect all income transactions"
    
    # Verify total income calculation
    assert total_income == 15000.0, "Total income should be 15000.0"

def test_adjust_goals():
    # Create test data for transactions
    transaction_data = {
        'transaction_id': ['tx1', 'tx2', 'tx3', 'tx4'],
        'transaction_date': [
            datetime.now() - timedelta(days=i) for i in range(4)
        ],
        'amount': [-5000.0, -3000.0, 2000.0, 3000.0],
        'category': ['Food', 'Transportation', 'Salary', 'Bonus'],
        'name': ['Luxury Restaurant', 'Luxury Car', 'Monthly Salary', 'Yearly Bonus']
    }
    
    # Create test data for goals
    goal_data = {
        'goal_id': ['sg_001', 'sg_002', 'sg_003', 'sg_004'],
        'category': ['Food', 'Transportation', 'Shopping', 'Travel'],
        'target_amount': [500.0, 300.0, 400.0, 200.0],
        'current_amount': [0.0, 0.0, 0.0, 0.0]
    }
    
    transactions_df = pd.DataFrame(transaction_data)
    goals_df = pd.DataFrame(goal_data)
    
    # Test goal adjustment
    trigger_reasons = {
        "unusual_transactions": [
            {"amount": -5000.0, "category": "Food"},
            {"amount": -3000.0, "category": "Transportation"}
        ],
        "additional_income": [
            {"amount": 2000.0, "category": "Salary"},
            {"amount": 3000.0, "category": "Bonus"}
        ]
    }
    
    adjusted_goals_df, adjustment_result = adjust_goals(transactions_df, trigger_reasons, goals_df)
    
    # Verify goal adjustments
    assert len(adjusted_goals_df) == 4, "Should have 4 adjusted goals"
    
    # Verify specific adjustments
    food_goal = adjusted_goals_df[adjusted_goals_df['category'] == 'Food'].iloc[0]
    transport_goal = adjusted_goals_df[adjusted_goals_df['category'] == 'Transportation'].iloc[0]
    
    assert food_goal['target_amount'] > 500.0, "Food goal should be increased"
    assert transport_goal['target_amount'] > 300.0, "Transportation goal should be increased"
    
    # Verify adjustment result contains summary
    assert 'summary' in adjustment_result, "Adjustment result should contain summary"
    assert 'adjustments' in adjustment_result, "Adjustment result should contain adjustments"
    assert 'recommendations' in adjustment_result, "Adjustment result should contain recommendations" 