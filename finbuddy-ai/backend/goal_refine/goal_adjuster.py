# ./Finbuddy_LLM/demo/goal_adjuster.py

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import autogen
import os
import re

def setup_llm_config():
    """Configure LLM settings"""
    # Look for .env file in the backend directory
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    
    if os.path.exists(env_path):
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=env_path)
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("❌ .env file found but OPENAI_API_KEY is missing.")
        return {
            "config_list": [
                {
                    "model": os.getenv("OPENAI_MODEL", "gpt-4"),
                    "api_key": api_key,
                    "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
                }
            ],
            "temperature": float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
            "timeout": 120,
        }
    else:
        raise FileNotFoundError("❌ No .env file found in the backend directory. Please create one with OpenAI configuration.")

def create_goal_adjustment_agent():
    """Create goal adjustment agent"""
    llm_config = setup_llm_config()
    
    # Financial planner agent
    financial_planner = autogen.AssistantAgent(
        name="Financial_Planner",
        system_message="""You are a professional financial planner specializing in dynamic budget adjustment. Your task is to analyze recent expenses and income to adjust financial goals accordingly.
        
        You should:
        1. Identify unusual spending patterns or outliers in recent transactions
        2. Consider additional income when adjusting monthly targets
        3. Adjust monthly category targets based on actual spending patterns
        4. Ensure the monthly saving target is maintained or adjusted based on income changes
        5. Provide clear explanations for all adjustments
        
        Your goal adjustments should be realistic, data-driven, and help users maintain their overall saving goals while adapting to their actual spending patterns and income changes.
        """,
        llm_config=llm_config,
    )
    
    # User proxy agent
    user_proxy = autogen.UserProxyAgent(
        name="User_Proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=0,
        code_execution_config={"work_dir": "financial_planning", "use_docker": False},
    )
    
    return financial_planner, user_proxy

def detect_unusual_transactions(transactions_df, category_thresholds=None):
    """
    Detect unusual transactions
    
    Args:
        transactions_df: Transactions DataFrame
        category_thresholds: Dictionary of anomaly thresholds for each category. If None, will be calculated automatically.
        
    Returns:
        List of unusual transactions
    """
    try:
        if transactions_df.empty:
            return []
        
        # Only analyze expenses (transactions with negative amounts)
        expenses_df = transactions_df[transactions_df["amount"] < 0].copy()
        expenses_df["amount"] = expenses_df["amount"].abs()  # Convert to positive for analysis
        
        if expenses_df.empty:
            return []
        
        # Ensure transaction date is datetime type
        if isinstance(expenses_df['transaction_date'][0], str):
            expenses_df['transaction_date'] = pd.to_datetime(expenses_df['transaction_date'])
        
        # If no thresholds provided, calculate automatically (mean + 2*std)
        if category_thresholds is None:
            category_thresholds = {}
            for category in expenses_df['category'].unique():
                cat_expenses = expenses_df[expenses_df['category'] == category]['amount']
                if len(cat_expenses) >= 5:  # Need at least 5 records for meaningful stats
                    mean = cat_expenses.mean()
                    std = cat_expenses.std()
                    category_thresholds[category] = mean + 2 * std
                else:
                    # If too few records, use conservative threshold (1.5x max)
                    category_thresholds[category] = cat_expenses.max() * 1.5 if not cat_expenses.empty else 500
        
        # Identify unusual transactions in last 30 days
        recent_date = expenses_df['transaction_date'].max()
        thirty_days_ago = recent_date - timedelta(days=30)
        recent_expenses = expenses_df[expenses_df['transaction_date'] >= thirty_days_ago]
        
        unusual_transactions = []
        for _, row in recent_expenses.iterrows():
            category = row['category']
            amount = row['amount']
            threshold = category_thresholds.get(category, 500)  # Default threshold
            
            if amount > threshold:
                unusual_transactions.append({
                    'transaction_id': _,
                    'date': row['transaction_date'],
                    'category': category,
                    'merchant': row.get('merchant', row.get('name', 'Unknown')),
                    'amount': amount,
                    'threshold': threshold,
                    'description': row.get('description', ''),
                    'percent_over': ((amount - threshold) / threshold) * 100
                })
        
        # Sort by percentage over threshold
        unusual_transactions.sort(key=lambda x: x['percent_over'], reverse=True)
        return unusual_transactions
        
    except Exception as e:
        print(f"Error in detect_unusual_transactions: {str(e)}")
        return []  # Return empty list instead of 0

def detect_additional_income(transactions_df):
    """
    Detect additional income
    
    Args:
        transactions_df: Transactions DataFrame
        
    Returns:
        Tuple of (additional income list, total amount)
    """
    if transactions_df.empty:
        return [], 0
    
    # Only analyze income (positive transactions)
    income_df = transactions_df[transactions_df["amount"] > 0].copy()
    
    if income_df.empty:
        return [], 0
    
    # Ensure transaction date is datetime type
    if isinstance(income_df['transaction_date'], str):
        income_df['transaction_date'] = pd.to_datetime(income_df['transaction_date'])
    
    # Identify income in last 30 days
    recent_date = income_df['transaction_date'].max()
    thirty_days_ago = recent_date - timedelta(days=30)
    recent_income = income_df[income_df['transaction_date'] >= thirty_days_ago]
    
    income_transactions = []
    for _, row in recent_income.iterrows():
        income_transactions.append({
            'transaction_id': _,
            'date': row['transaction_date'],
            'category': row['category'],
            'source': row.get('merchant', row.get('name', 'Unknown')),
            'amount': row['amount'],
            'description': row.get('description', '')
        })
    
    # Calculate total additional income
    total_additional_income = sum(tx['amount'] for tx in income_transactions)
    
    return income_transactions, total_additional_income

def adjust_goals(new_transactions_df, trigger_reasons, goals_df, saving_target=None):
    """
    Dynamically adjust goals based on transactions and income
    
    Args:
        new_transactions_df: New Transactions DataFrame
        goals_df: Goals DataFrame
        saving_target: Monthly saving target. If None, keep total spending target unchanged.
        
    Returns:
        List of adjusted goals
    """
    # Create agents
    financial_planner, user_proxy = create_goal_adjustment_agent()
    
    # Prepare transaction summary
    transaction_summary = prepare_transaction_summary(new_transactions_df)
    
    # Prepare goals data
    goals_data = prepare_goals_data(goals_df)
    
    # Build complete analysis request
    adjustment_request = f"""
    ## Goal adjustment request
    
    ### Transaction summary
    {transaction_summary}
    
    ### Current financial goals
    {goals_data}

    triggered reason:
    {trigger_reasons}
    
    ### Additional information
    - Monthly saving target: {"Keep total spending target unchanged" if saving_target is None else f"¥{saving_target:.2f}"}
    
    Please adjust the user's financial goals based on this information, paying special attention to:
    1. Analyzing impact of unusual transactions on category budgets
    2. Considering effect of additional income on disposable budget
    3. Ensuring adjusted total budget meets saving target
    4. Providing clear explanations for each adjustment
    
    Return adjusted goals and explanations in JSON format with these fields:
    - adjusted_goals: List of adjusted goals, each with:
        - goal_id: The unique identifier of the goal (use the exact goal_id from the current goals)
        - goal_type: Either "spending" or "saving"
        - category: The goal category
        - target_amount: The new target amount (as a number, without currency symbol)
        - period: The goal period (e.g., "monthly")
        - description: Explanation of the adjustment
    - adjustments: Dictionary of category adjustments with explanations
    - summary: Overall adjustment explanation
    - recommendations: List of specific recommendations
    
    Ensure valid JSON format and use numbers (not strings with currency symbols) for target_amount.
    """
    
    # Initiate conversation
    user_proxy.initiate_chat(financial_planner, message=adjustment_request)
    
    # Get analysis results
    adjustment_messages = user_proxy.chat_messages[financial_planner]
    last_response = adjustment_messages[-1]['content']
    
    # Parse JSON response
    try:
        # Extract JSON portion
        json_str = extract_json_from_response(last_response)
        adjustment_result = json.loads(json_str)
        
        # Validate the response format
        if 'adjusted_goals' not in adjustment_result:
            print(f"Error in adjust_goals: Missing 'adjusted_goals' in response")
            return goals_df.to_dict('records')
            
        # Create a mapping of category to goal_id from original goals
        category_to_goal_id = {goal['category']: goal['goal_id'] for goal in goals_df.to_dict('records')}
        
        # Process each adjusted goal
        processed_goals = []
        for goal in adjustment_result['adjusted_goals']:
            if 'target_amount' not in goal:
                print(f"Error in adjust_goals: Missing 'target_amount' in goal")
                return goals_df.to_dict('records')
                
            # Convert target_amount to float if it's a string
            if isinstance(goal['target_amount'], str):
                try:
                    # Remove any currency symbols and whitespace
                    amount_str = goal['target_amount'].replace('¥', '').replace('$', '').strip()
                    goal['target_amount'] = float(amount_str)
                except ValueError:
                    print(f"Error in adjust_goals: Invalid target_amount format: {goal['target_amount']}")
                    return goals_df.to_dict('records')
            
            # Get the correct goal_id for this category
            goal_id = category_to_goal_id.get(goal['category'])
            if not goal_id:
                print(f"Error in adjust_goals: Unknown category {goal['category']}")
                continue
                
            # Find the original goal to get current_amount
            original_goal = next((g for g in goals_df.to_dict('records') if g['goal_id'] == goal_id), None)
            if original_goal:
                processed_goals.append({
                    'goal_id': goal_id,
                    'category': goal['category'],
                    'target_amount': goal['target_amount'],
                    'current_amount': original_goal['current_amount']
                })
        
        # Ensure adjustments and recommendations are present
        if 'adjustments' not in adjustment_result:
            adjustment_result['adjustments'] = {}
        if 'recommendations' not in adjustment_result:
            adjustment_result['recommendations'] = []
        if 'summary' not in adjustment_result:
            adjustment_result['summary'] = "No summary provided"
            
        # Convert any datetime objects to strings
        def convert_datetime(obj):
            if isinstance(obj, dict):
                return {k: convert_datetime(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_datetime(i) for i in obj]
            elif isinstance(obj, (datetime, pd.Timestamp)):
                return obj.isoformat()
            return obj
            
        # Create the adjustment report
        adjustment_report = {
            "user_id": new_transactions_df['user_id'].iloc[0] if 'user_id' in new_transactions_df.columns else None,
            "timestamp": datetime.now().isoformat(),
            "unusual_transactions": convert_datetime(trigger_reasons.get('unusual_transactions', [])),
            "additional_income": convert_datetime(trigger_reasons.get('additional_income', [])),
            "total_additional_income": sum(tx['amount'] for tx in trigger_reasons.get('additional_income', [])),
            "original_goals": goals_df.to_dict('records'),
            "adjusted_goals": processed_goals,
            "adjustment_summary": adjustment_result['summary'],
            "adjustments": adjustment_result['adjustments'],
            "recommendations": adjustment_result['recommendations']
        }
        
        # Save the adjustment report
        report_filename = f"goal_reports/adjustment_report_{adjustment_report['user_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(adjustment_report, f, indent=2)
            
        return processed_goals
        
    except Exception as e:
        print(f"Error in adjust_goals: {str(e)}")
        return goals_df.to_dict('records')  # Return original goals if adjustment fails

def prepare_transaction_summary(df):
    """Prepare transaction summary"""
    if df.empty:
        return "No transaction data available for analysis"
    
    # Ensure transaction date is datetime type
    if isinstance(df['transaction_date'][0], str):
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    
    # Separate expenses and income
    expenses_df = df[df['amount'] < 0].copy()
    income_df = df[df['amount'] > 0].copy()
    
    # Convert expenses to positive for calculation
    expenses_df['amount'] = expenses_df['amount'].abs()
    
    # Basic stats
    total_spent = expenses_df['amount'].sum() if not expenses_df.empty else 0
    total_income = income_df['amount'].sum() if not income_df.empty else 0
    
    # Get last 30 days data
    recent_date = df['transaction_date'].max()
    thirty_days_ago = recent_date - timedelta(days=30)
    recent_expenses = expenses_df[expenses_df['transaction_date'] >= thirty_days_ago]
    recent_income = income_df[income_df['transaction_date'] >= thirty_days_ago]
    
    monthly_spent = recent_expenses['amount'].sum() if not recent_expenses.empty else 0
    monthly_income = recent_income['amount'].sum() if not recent_income.empty else 0
    
    # Calculate category expenses
    category_totals = recent_expenses.groupby('category')['amount'].sum().sort_values(ascending=False) if not recent_expenses.empty else pd.Series()
    
    # Generate summary text
    summary = f"Last 30 days total spending: ¥{monthly_spent:.2f}\n"
    summary += f"Last 30 days total income: ¥{monthly_income:.2f}\n"
    summary += f"Last 30 days net income: ¥{monthly_income - monthly_spent:.2f}\n"
    summary += f"All-time total spending: ¥{total_spent:.2f}\n"
    summary += f"All-time total income: ¥{total_income:.2f}\n"
    
    if not category_totals.empty:
        summary += "Last 30 days spending by category:\n"
        for category, amount in category_totals.items():
            percent = (amount / monthly_spent) * 100 if monthly_spent > 0 else 0
            summary += f"- {category}: ¥{amount:.2f} ({percent:.1f}%)\n"
    
    # Add recent transactions
    recent_transactions = df.sort_values('transaction_date', ascending=False).head(10)
    summary += "\nLast 10 transactions:\n"
    for _, row in recent_transactions.iterrows():
        date_str = row['transaction_date'].strftime('%Y-%m-%d')
        amount = row['amount']
        transaction_type = "Income" if amount > 0 else "Expense"
        amount_str = f"¥{abs(amount):.2f}"
        merchant = row.get('merchant', row.get('name', 'Unknown'))
        summary += f"- {date_str}: {transaction_type} - {merchant} - {amount_str}\n"
    
    return summary

def prepare_goals_data(goals_df):
    """Prepare goals data"""
    if goals_df.empty:
        return "User hasn't set any spending goals"
    
    goals_text = ""
    for _, goal in goals_df.iterrows():
        # Add default period if not present
        period = goal.get('period', 'monthly')
        description = goal.get('description', '')
        goals_text += f"- Category: {goal['category']}, Target: ¥{goal['target_amount']:.2f} ({period}), Description: {description}\n"
    
    return goals_text

def extract_json_from_response(response):
    """Extract JSON portion from response"""
    # Try to find JSON block
    json_matches = re.findall(r'```json\n([\s\S]*?)\n```', response)
    if json_matches:
        return json_matches[0]
    
    # If no explicit JSON block, try to find whole JSON object
    json_pattern = r'(\{[\s\S]*\})'
    matches = re.search(json_pattern, response)
    if matches:
        return matches.group(1)
    
    # If still not found, return original response
    return response

def format_adjustment_report(adjustment_result):
    """Format adjustment report as readable text"""
    if "error" in adjustment_result:
        return f"## Goal adjustment failed\n\nError: {adjustment_result['error']}"
    
    content = "# Financial Goals Adjustment Report\n\n"
    
    # Add overview
    content += "## Adjustment Summary\n"
    summary = adjustment_result.get("summary", "No overall adjustment explanation provided")
    content += summary + "\n\n"
    
    # Add adjustment details
    content += "## Adjustment Details\n"
    adjustments = adjustment_result.get("adjustments", {})
    if isinstance(adjustments, dict):
        for category, adjustment in adjustments.items():
            content += f"### {category}\n"
            content += adjustment + "\n\n"
    else:
        content += str(adjustments) + "\n\n"
    
    # Add adjusted goals
    content += "## Adjusted Goals\n"
    adjusted_goals = adjustment_result.get("adjusted_goals", [])
    if isinstance(adjusted_goals, list):
        for goal in adjusted_goals:
            content += f"- {goal['category']}: ¥{goal['target_amount']:.2f} ({goal['period']})\n  {goal['description']}\n"
    else:
        content += str(adjusted_goals) + "\n\n"
    
    # Add recommendations
    content += "\n## Recommendations\n"
    recommendations = adjustment_result.get("recommendations", [])
    if isinstance(recommendations, list):
        for i, rec in enumerate(recommendations, 1):
            content += f"{i}. {rec}\n"
    else:
        content += str(recommendations) + "\n\n"
    
    return content