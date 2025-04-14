import autogen
import json
import os
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from profile_analyzer import ProfileAnalyzer
import sys

class OnboardingAgent:
    def __init__(self, config_path: str = None):
        """
        Initialize the onboarding agent with necessary configurations.
        
        Args:
            config_path: Optional path to the configuration file for the LLM.
                        If not provided, will look in the root directory.
        """
        # Get the root directory of the project
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        
        # Set default config path if not provided
        if config_path is None:
            config_path = os.path.join(self.root_dir, "config_list.json")
        
        self.llm_config = self._setup_llm_config(config_path)
        self.profile_analyzer = ProfileAnalyzer()
        self.conversation_history = []
        
        # Load existing expense data
        self.expense_data = self._load_expense_data()
        
        # Track required information
        self.required_info = {
            "personal_info": ["age_range", "employment_status"],
            "financial_goals": ["short_term", "medium_term", "long_term"],
            "savings": ["monthly_saving_goal"]
        }
        self.completed_info = {category: False for category in self.required_info.keys()}

    def _load_expense_data(self):
        """Load existing expense data from the demo directory."""
        expense_path = os.path.join(self.root_dir, "demo", "sample_expenses.csv")
        if os.path.exists(expense_path):
            df = pd.read_csv(expense_path)
            df['transaction_date'] = pd.to_datetime(df['transaction_date'])
            return df
        return None

    def _setup_llm_config(self, config_path: str) -> Dict:
        """
        Set up the LLM configuration.
        """
        # Try config_list.json first
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                config_list = json.load(f)
            return {
                "config_list": config_list,
                "temperature": 0.7,
                "timeout": 120,
            }
        
        # If config_list.json not found, try .env in root directory
        env_path = os.path.join(self.root_dir, ".env")
        if os.path.exists(env_path):
            from dotenv import load_dotenv
            load_dotenv(dotenv_path=env_path)
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("❌ .env file found but OPENAI_API_KEY is missing.")
                
            return {
                "config_list": [
                    {
                        "model": os.getenv("MODEL_INDEX", "gpt-4o-mini"),
                        "api_key": api_key,
                        "base_url": os.getenv("BASE_URL", "https://api.openai.com/v1"),
                    }
                ],
                "temperature": 0.7,
                "timeout": 120,
            }
        
        raise FileNotFoundError(
            f"❌ No config_list.json or .env found in {self.root_dir}. "
            "Please provide either an Azure config_list.json or a .env with OPENAI_API_KEY."
        )

    def create_agents(self):
        """
        Create the necessary agents for the onboarding process.
        """
        # Define termination condition function
        def is_termination_msg(msg):
            content = msg.get("content", "").strip()
            return "TERMINATE" in content
        
        # Financial Advisor Agent
        self.financial_advisor = autogen.AssistantAgent(
            name="Financial_Advisor",
            system_message="""You are a friendly and professional financial advisor specializing in personal finance. 
            Your goal is to quickly understand the user's financial situation and goals within a 3-minute conversation.
            
            IMPORTANT: DO NOT ask about expenses or spending habits. We already have this information from the user's expense file.
            
            Key guidelines:
            1. Keep the conversation focused and efficient (max 5 rounds)
            2. Do not ask about specific spending habits (we already have this data)
            3. Focus on gathering:
               - Basic personal information (age, employment)
               - Main financial goals (especially saving goals)
               - Monthly saving targets
            4. Do not provide feedback or advice during the conversation
            5. Keep questions broad and open-ended
            6. End the conversation after gathering essential information
            
            After gathering all essential information, conclude the conversation with:
            "TERMINATE"
            """,
            llm_config=self.llm_config,
            is_termination_msg=is_termination_msg
        )
        
        # User Proxy Agent with proper input handling
        self.user_proxy = autogen.UserProxyAgent(
            name="User_Proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=0,
            code_execution_config={"work_dir": "onboarding", "use_docker": False},
            is_termination_msg=is_termination_msg,
            default_auto_reply="TERMINATE"
        )

    def _get_normalized_conversation(self) -> List[Dict]:
        """
        Get conversation history with normalized speaker names.
        
        Returns:
            List[Dict]: List of messages with normalized speaker names
        """
        messages = self.user_proxy.chat_messages[self.financial_advisor]
        normalized = []
        
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            
            # Skip empty messages
            if not content:
                continue
            
            # Normalize the speaker based on role
            speaker = "Advisor" if role == "user" else "User"
            
            normalized.append({
                "speaker": speaker,
                "content": content,
                "timestamp": datetime.now().isoformat()
            })
        
        return normalized

    def _process_conversation(self) -> bool:
        """
        Process the conversation history and extract relevant information.
        
        Returns:
            bool: True if all required information has been gathered, False otherwise
        """
        # Get normalized conversation
        normalized_messages = self._get_normalized_conversation()
        
        # Process each message
        for msg in normalized_messages:
            content = msg.get("content", "")
            speaker = msg.get("speaker", "")
            
            # Skip duplicate messages
            if content in [m.get("content", "") for m in self.conversation_history]:
                continue
            
            # Store the message in conversation history with proper speaker information
            self.conversation_history.append({
                "speaker": speaker,
                "content": content,
                "timestamp": msg.get("timestamp", datetime.now().isoformat())
            })
            
            # Check for termination message from the Advisor
            if speaker == "Advisor" and "TERMINATE" in content.rstrip():
                return True
        
        return False

    def start_conversation(self) -> str:
        """
        Start the onboarding conversation and return the initial message.
        
        Returns:
            str: The initial message from the financial advisor
        """
        # Start the conversation with the financial advisor
        self.financial_advisor.initiate_chat(
            self.user_proxy,
            message="Hello! I'm your personal financial advisor. I'd like to help you get started with managing your finances better. Could you tell me about your main financial goals and what you hope to achieve?"
        )
        
        # Get the initial message
        messages = self.user_proxy.chat_messages[self.financial_advisor]
        if not messages:
            raise ValueError("Failed to start conversation")
            
        return messages[0]["content"]

    def send_message(self, user_message: str) -> Tuple[str, bool, Optional[Dict]]:
        """
        Send a message to the financial advisor and get the response.
        
        Args:
            user_message: The message from the user
            
        Returns:
            Tuple[str, bool, Optional[Dict]]: 
                - The advisor's response message
                - Whether the conversation is complete
                - The user profile if complete, None otherwise
        """
        # Send the message
        self.user_proxy.send(
            user_message,
            self.financial_advisor
        )
        
        # Get the response
        messages = self.user_proxy.chat_messages[self.financial_advisor]
        if not messages:
            raise ValueError("No response received")
            
        # Process the conversation
        is_complete = self._process_conversation()
        
        # Get the last message
        last_message = messages[-1]["content"]
        
        # If conversation is complete, analyze and return the profile
        if is_complete:
            user_profile = self.profile_analyzer.analyze_conversation(self.conversation_history)
        if self.expense_data is not None:
            self._add_expense_data_to_profile(user_profile)
            return last_message, True, user_profile
            
        return last_message, False, None

    def _add_expense_data_to_profile(self, user_profile: Dict):
        """Add expense data to the user profile."""
        if self.expense_data is not None:
            # Add expense analysis to the profile
            user_profile["expense_analysis"] = {
                "total_expenses": self.expense_data["amount"].sum(),
                "average_monthly_expense": self.expense_data.groupby(self.expense_data["transaction_date"].dt.to_period("M"))["amount"].sum().mean(),
                "top_categories": self.expense_data.groupby("category")["amount"].sum().nlargest(3).to_dict()
            }

    def get_onboarding_goals(self) -> List[str]:
        """Get the list of onboarding goals that need to be completed."""
        goals = []
        for category, fields in self.required_info.items():
            if not self.completed_info[category]:
                goals.extend([f"{category}: {field}" for field in fields])
        return goals

if __name__ == "__main__":
    # Example usage
    agent = OnboardingAgent()
    agent.create_agents()
    user_profile, is_complete = agent.start_onboarding()
    agent.save_user_profile() 