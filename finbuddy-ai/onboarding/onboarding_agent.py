import autogen
import json
import os
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from profile_analyzer import ProfileAnalyzer
import sys
import logging
import uuid
from database import query_database
from decimal import Decimal, getcontext

# Set decimal precision
getcontext().prec = 10

logger = logging.getLogger(__name__)

class OnboardingAgent:
    def __init__(self, user_id: int, config_path: str = None):
        """
        Initialize the onboarding agent with necessary configurations.
        
        Args:
            user_id: The ID of the user
            config_path: Optional path to the configuration file for the LLM.
                        If not provided, will look in the root directory.
        """
        self.user_id = user_id
        # Get the root directory of the project
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        
        # Set default config path if not provided
        if config_path is None:
            config_path = os.path.join(self.root_dir, "config_list.json")
        
        self.llm_config = self._setup_llm_config(config_path)
        self.profile_analyzer = ProfileAnalyzer()
        self.conversation_history = []
        
        # Load existing expense data
        db_data = self._load_expense_data_from_db()
        if db_data is not None:
            self.expense_data = db_data
        else:
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
            try:
                df = pd.read_csv(expense_path)
                # Ensure column names match database schema
                df = df.rename(columns={
                    'transaction_date': 'date',
                    'transaction_id': 'transaction_id',
                    'account_id': 'account_id',
                    'amount': 'amount',
                    'name': 'name',
                    'category': 'category'
                })
                df['date'] = pd.to_datetime(df['date'])
                logger.debug(f"Loaded expense data from file: {len(df)} transactions")
                return df
            except Exception as e:
                logger.error(f"Failed to load expense data from file: {e}")
                return None
        return None

    def _load_expense_data_from_db(self):
        """Load expense data from the database for the current user and log it."""
        query = """
        SELECT 
            transaction_id,
            account_id,
            date,
            amount,
            name,
            category
        FROM transactions 
        WHERE user_id = %s
        ORDER BY date DESC
        """
        try:
            data = query_database(query, (self.user_id,))
            if not data:  # Check if the result is empty
                logger.debug(f"No expense data found for user {self.user_id}")
                return None
                
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            logger.debug(f"Fetched expense data for user {self.user_id}: {len(df)} transactions")
            return df
        except Exception as e:
            logger.error(f"Failed to load expense data from DB: {e}")
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
        """Create the necessary agents for the onboarding process."""
        # Log user data and expense information
        logger.debug(f"Creating agents for user {self.user_id}")
        if self.expense_data is not None and not self.expense_data.empty:
            logger.debug(f"User expense data summary:")
            logger.debug(f"Total transactions: {len(self.expense_data)}")
            logger.debug(f"Date range: {self.expense_data['date'].min()} to {self.expense_data['date'].max()}")
            logger.debug(f"Total spending: {self.expense_data['amount'].sum()}")
            logger.debug(f"Categories: {self.expense_data['category'].unique().tolist()}")
        else:
            logger.warning(f"No expense data found for user {self.user_id}")

        # Get current date for context
        current_date = datetime.now().strftime("%B %d, %Y")

        # Define termination condition function
        def is_termination_msg(msg):
            content = msg.get("content", "").strip()
            return "TERMINATE" in content

        # Financial Analyst Agent
        self.financial_analyst = autogen.AssistantAgent(
            name="Financial_Analyst",
            system_message=f"""You are a financial analyst specializing in personal finance data analysis.
            Today's date is {current_date}.
            
            Your role is to analyze the user's transaction data and provide insights to the Financial Advisor.
            
            You have access to the user's complete transaction history. Analyze this data to:
            1. Calculate key financial metrics:
               - Average monthly expenses
               - Spending patterns by category
               - Current saving rate
               - Top expense categories
               - Monthly spending trends
            
            2. Identify potential areas for improvement:
               - Categories with highest spending
               - Unusual spending patterns
               - Opportunities for cost reduction
            
            3. Format your analysis in a clear, structured way that the Financial Advisor can use to:
               - Understand the user's current financial situation
               - Make informed recommendations
               - Set realistic goals
            
            Provide your analysis in a concise, professional format that focuses on actionable insights.
            Use plain text only - no markdown formatting.
            """,
            llm_config=self.llm_config
        )

        # Financial Advisor Agent
        self.financial_advisor = autogen.AssistantAgent(
            name="Financial_Advisor",
            system_message=f"""You are a friendly and professional financial advisor specializing in personal finance. 
            Today's date is {current_date}.
            
            Your role is to help users set and achieve their financial goals through a detailed conversation and analysis.
            
            You will receive a comprehensive financial analysis from the Financial Analyst before starting the conversation.
            Use this analysis to provide personalized advice and recommendations.
            
            Follow these steps in order:
            1. Review the financial analysis provided by the Financial Analyst
            2. Ask about their financial goals in detail:
               - What specific goals do they want to achieve? (e.g., saving for a house, car, vacation)
               - What's their target amount for each goal?
               - What's their desired timeline?
               - Encourage them to elaborate on their goals and priorities
            
            3. Provide specific advice based on their actual spending data:
               - Suggest monthly saving targets for each goal
               - Recommend specific spending adjustments based on their transaction history, be very specific on how much to save on each category
               - Explain how these changes will help reach their goals
            
            4. Check feasibility:
               - Ask if the suggested saving targets seem achievable
               - If they say no, ask what would be more realistic
               - Adjust the plan based on their feedback
            
            5. Finalize the plan:
               - Summarize the agreed-upon goals and targets
               - Confirm they're comfortable with the plan
            
            IMPORTANT FORMATTING RULES:
            1. Use plain text only - NO markdown formatting
            2. Do NOT use any of these characters for formatting:
               - No asterisks (*) for bold or emphasis
               - No underscores (_) for italics
               - No hash symbols (#) for headers
               - No backticks (`) for code
               - No square brackets [] or parentheses () for links
            3. Instead, use:
               - Regular text for emphasis
               - Line breaks for separation
               - Bullet points (-) for lists
               - Numbers for ordered lists
               - Proper spacing for readability
            
            Keep your responses clear and easy to read with proper spacing and line breaks.
            
            End the conversation with "TERMINATE" only after completing all steps and getting user confirmation.
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
        """Process the conversation history and extract relevant information."""
        # Get normalized conversation
        normalized_messages = self._get_normalized_conversation()
        
        # Process each message
        for msg in normalized_messages:
            content = msg.get("content", "")
            speaker = msg.get("speaker", "")
            
            # Skip duplicate messages
            if content in [m.get("content", "") for m in self.conversation_history]:
                continue
            
            # Store the message in conversation history
            self.conversation_history.append({
                "speaker": speaker,
                "content": content,
                "timestamp": msg.get("timestamp", datetime.now().isoformat())
            })
            
            # If this is a response from the advisor containing financial analysis
            if speaker == "Advisor" and "financial analysis" in content.lower():
                # Add the financial data analysis to the message
                financial_data = self.analyze_financial_data()
                self.conversation_history.append({
                    "speaker": "System",
                    "content": json.dumps(financial_data),
                    "timestamp": datetime.now().isoformat()
                })
            
            # Check for termination message and goal saving
            if speaker == "Advisor" and "TERMINATE" in content.rstrip():
                # Extract and save goals before terminating
                user_profile = self.profile_analyzer.analyze_conversation(self.conversation_history)
                if user_profile:
                    self.save_goals_to_db(user_profile)
                return True
        
        return False

    def _get_financial_summary(self) -> Dict:
        """Get a summary of the user's current financial situation from the database."""
        try:
            # Get current account balances from bank_accounts
            accounts_query = """
            SELECT 
                account_id,
                name,
                available_balance,
                current_balance,
                currency_code
            FROM bank_accounts 
            WHERE user_id = %s
            """
            accounts_result = query_database(accounts_query, (self.user_id,))
            
            # Calculate total available balance
            total_available = Decimal('0')
            total_current = Decimal('0')
            for account in accounts_result:
                total_available += Decimal(str(account['available_balance']))
                total_current += Decimal(str(account['current_balance']))

            # Get transactions for the last 30 days
            transactions_query = """
            SELECT 
                COALESCE(SUM(CASE WHEN category = 'Income' THEN amount ELSE 0 END), 0) as total_income,
                COALESCE(SUM(CASE WHEN category != 'Income' THEN amount ELSE 0 END), 0) as total_spending,
                category,
                COALESCE(SUM(amount), 0) as category_amount
            FROM transactions 
            WHERE user_id = %s 
            AND date >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY category
            ORDER BY category_amount DESC
            """
            transactions_result = query_database(transactions_query, (self.user_id,))
            
            # Process category spending
            category_spending = {}
            total_spending = Decimal('0')
            total_income = Decimal('0')
            
            for row in transactions_result:
                if row['category'] == 'Income':
                    total_income = Decimal(str(row['total_income']))
                else:
                    amount = Decimal(str(row['category_amount']))
                    category_spending[row['category']] = amount
                    total_spending += amount

            # Calculate actual money left (available balance - spending)
            actual_money_left = total_available - total_spending

            logger.debug(f"Financial summary for user {self.user_id}:")
            logger.debug(f"Total available balance: {total_available}")
            logger.debug(f"Total current balance: {total_current}")
            logger.debug(f"Total income (30 days): {total_income}")
            logger.debug(f"Total spending (30 days): {total_spending}")
            logger.debug(f"Category spending: {category_spending}")

            return {
                'current_savings': float(total_available),
                'current_balance': float(total_current),
                'current_spending': float(total_spending),
                'current_income': float(total_income),
                'actual_money_left': float(actual_money_left),
                'category_spending': {k: float(v) for k, v in category_spending.items()}
            }
        except Exception as e:
            logger.error(f"Failed to get financial summary: {e}")
            return {}

    def start_conversation(self) -> str:
        """Start the onboarding conversation and return the initial message, logging user data."""
        # Log user data
        logger.debug(f"Starting conversation for user {self.user_id} with data: {self.expense_data}")
        
        # Get financial summary
        financial_summary = self._get_financial_summary()
        
        # Create the initial message with financial summary
        initial_message = f"""Hello! I'm your personal financial advisor. I've analyzed your current financial situation:

Current Financial Summary:
- Available Balance: ${financial_summary.get('current_savings', 0):,.2f}
- Current Balance: ${financial_summary.get('current_balance', 0):,.2f}
- Income (Last 30 Days): ${financial_summary.get('current_income', 0):,.2f}
- Spending (Last 30 Days): ${financial_summary.get('current_spending', 0):,.2f}
- Actual Money Left: ${financial_summary.get('actual_money_left', 0):,.2f}

Spending by Category (Last 30 Days):
{chr(10).join([f"- {category}: ${amount:,.2f}" for category, amount in financial_summary.get('category_spending', {}).items()])}

Based on this analysis, I'd like to help you set and achieve your financial goals. Could you tell me about your main financial goals and what you hope to achieve?"""

        # Start the conversation with the financial advisor
        self.financial_advisor.initiate_chat(
            self.user_proxy,
            message=initial_message
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
                "average_monthly_expense": self.expense_data.groupby(self.expense_data["date"].dt.to_period("M"))["amount"].sum().mean(),
                "top_categories": self.expense_data.groupby("category")["amount"].sum().nlargest(3).to_dict()
            }

    def get_onboarding_goals(self) -> List[str]:
        """Get the list of onboarding goals that need to be completed."""
        goals = []
        for category, fields in self.required_info.items():
            if not self.completed_info[category]:
                goals.extend([f"{category}: {field}" for field in fields])
        return goals

    def start_goal_collection(self):
        """Start the goal collection phase with enhanced prompts."""
        self.financial_advisor.initiate_chat(
            self.user_proxy,
            message="Let's discuss your financial goals in detail. What are you aiming to achieve, and how do you plan to get there?"
        )
        # Process conversation and check feasibility
        while not self._process_conversation():
            response = self.user_proxy.chat_messages[self.financial_advisor][-1]['content']
            if "feasible" in response.lower():
                self.financial_advisor.initiate_chat(
                    self.user_proxy,
                    message="Do you think these goals are feasible? If not, how would you adjust them?"
                )

    def analyze_financial_data(self) -> Dict:
        """Analyze the user's financial data and return insights."""
        if self.expense_data is None:
            return {}
        
        # Calculate key metrics
        monthly_expenses = self.expense_data.groupby(
            self.expense_data['date'].dt.to_period('M')
        )['amount'].sum()
        
        category_spending = self.expense_data.groupby('category')['amount'].agg(['sum', 'mean'])
        
        return {
            'average_monthly_expense': monthly_expenses.mean(),
            'top_expenses': category_spending.nlargest(3, 'sum').to_dict('index'),
            'monthly_breakdown': monthly_expenses.to_dict(),
            'spending_patterns': category_spending.to_dict('index')
        }

    def save_goals_to_db(self, goals: Dict):
        """Save the user's financial goals to the database."""
        try:
            # Save saving goals
            for goal in goals.get('saving_goals', []):
                query = """
                INSERT INTO saving_goals 
                (goal_id, user_id, category, target_amount, current_amount, target_date, created_at, last_adjusted_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
                """
                goal_id = f"goal_{uuid.uuid4()}"
                update_database(query, (
                    goal_id,
                    self.user_id,
                    goal['category'],
                    goal['target_amount'],
                    0,  # current_amount starts at 0
                    goal['target_date']
                ))

            # Save spending goals
            for goal in goals.get('spending_goals', []):
                query = """
                INSERT INTO spending_goals 
                (goal_id, user_id, category, target_amount, current_amount, created_at, last_adjusted_at)
                VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
                """
                goal_id = f"goal_{uuid.uuid4()}"
                update_database(query, (
                    goal_id,
                    self.user_id,
                    goal['category'],
                    goal['target_amount'],
                    0  # current_amount starts at 0
                ))

            logger.debug(f"Successfully saved goals for user {self.user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save goals for user {self.user_id}: {e}")
            return False

if __name__ == "__main__":
    # Example usage
    agent = OnboardingAgent(user_id=1)
    agent.create_agents()
    user_profile, is_complete = agent.start_onboarding()
    agent.save_user_profile() 