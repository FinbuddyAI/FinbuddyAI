# Mini Spending Goal Adjuster

## Create transaction data
```bash
python create_sample_data.py
```

## Add API Config File
```bash
# .env
OPENAI_API_KEY=sk-**
BASE_URL=https://api**
MODEL_INDEX=gpt-4o
```

## Simulate Spending Goal Adjucting
```bash
python demo.py
```

## More Details
The core function is **adjust_goals()** in **goal_adjuster.py**.
```bash
def adjust_goals(new_transactions_df, trigger_reasons, goals_df, saving_target=None):
    """
    Dynamically adjust goals based on transactions and income
    
    Args:
        new_transactions_df: New Transactions DataFrame
        goals_df: Goals DataFrame
        saving_target: Monthly saving target. If None, keep total spending target unchanged.
        
    Returns:
        Tuple of (adjusted goals DataFrame, adjustment results)
    """
```