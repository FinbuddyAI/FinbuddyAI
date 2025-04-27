import os
import json
from openai import OpenAI
from typing import List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd


class ProfileAnalyzer:
    def __init__(self):
        # Get the root directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(current_dir)
        
        # Load configuration
        config_path = os.path.join(root_dir, "config_list.json")
        env_path = os.path.join(root_dir, ".env")
        
        if not os.path.exists(config_path):
            print(f"[ProfileAnalyzer] ❌ config_list.json not found at: {config_path}")
            raise FileNotFoundError(
                f"Configuration files not found in {root_dir}. "
                "Please ensure config_list.json and .env exist in the root directory."
            )
        
        # Load environment variables from .env file
        load_dotenv(dotenv_path=env_path)
        
        # Load OpenAI configuration
        with open(config_path, "r") as f:
            config = json.load(f)
        
        # Initialize Azure OpenAI client
        self.client = OpenAI(
            api_key=config[0]["api_key"],
            base_url=config[0]["base_url"]
        )
        
        self.model = config[0].get("model", "gpt-4o-mini")
        self.temperature = config[0].get("temperature", 0.7)
        
    def _format_conversation_history(self, conversation_history: List[Dict]) -> str:
        formatted = []
        for msg in conversation_history:
            speaker = msg.get("speaker", "unknown")
            content = msg.get("content", "")
            if content.strip() in ["TERMINATE", "quit"]:
                continue
            formatted.append(f"{speaker}: {content}")
        return "\n".join(formatted)
    
    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        try:
            # Find the JSON part in the response
            start = response.find("{")
            end = response.rfind("}") + 1
            if start == -1 or end == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response[start:end]
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            print(f"Response content: {response}")
            raise
    
    def analyze_conversation(self, conversation_history: List[Dict]) -> Dict[str, Any]:
        formatted_history = self._format_conversation_history(conversation_history)
        
        prompt = f"""
You are given a conversation log between a financial advisor and a user. Please analyze it and return a completed user profile.

ONLY use information explicitly stated. Do not invent or infer details.

Return ONLY valid JSON filled into the structure below:

JSON Format:
{{
  "personal_info": {{
    "age_range": "",
    "employment_status": "",
    "family_situation": ""
  }},
  "financial_goals": {{
    "short_term": [],
    "medium_term": [],
    "long_term": []
  }},
  "income": {{
    "primary_source": "",
    "monthly_amount": 0,
    "additional_sources": []
  }},
  "expenses": {{
    "monthly_estimate": 0,
    "major_expense_categories": []
  }},
  "savings": {{
    "current_amount": 0,
    "monthly_saving_goal": 0,
    "saving_habits": ""
  }},
  "investment_profile": {{
    "experience_level": "",
    "risk_tolerance": "",
    "preferred_investment_types": []
  }},
  "financial_concerns": [],
  "previous_tools": [],
  "time_horizon": {{
    "short_term": "",
    "medium_term": "",
    "long_term": ""
  }}
}}

Conversation History:
{formatted_history}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a financial profile analyzer. Extract information from conversations and format it into structured JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature
            )
            
            content = response.choices[0].message.content
            return self._extract_json_from_response(content)
            
        except Exception as e:
            print(f"Error analyzing conversation: {e}")
            raise
    
    def save_analysis(self, user_profile: Dict[str, Any]) -> str:
        # Create user_profiles directory if it doesn't exist
        current_dir = os.path.dirname(os.path.abspath(__file__))
        profiles_dir = os.path.join(current_dir, "user_profiles")
        os.makedirs(profiles_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"user_profile_{timestamp}.json"
        filepath = os.path.join(profiles_dir, filename)
        
        # Save the profile
        with open(filepath, "w") as f:
            json.dump(user_profile, f, indent=2)
        
        return filepath

    def analyze_financial_data(self, user_profile: Dict[str, Any], expense_data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze financial data and provide insights on spending and saving goals."""
        # Analyze expenses
        total_expenses = expense_data['amount'].sum()
        monthly_expense = expense_data.groupby(expense_data['transaction_date'].dt.to_period('M'))['amount'].sum().mean()
        top_categories = expense_data.groupby('category')['amount'].sum().nlargest(3).to_dict()

        # Provide insights
        insights = {
            'total_expenses': total_expenses,
            'average_monthly_expense': monthly_expense,
            'top_categories': top_categories,
            'advice': "To achieve your saving goals, consider reducing spending in top categories."
        }

        user_profile['financial_insights'] = insights
        return user_profile
