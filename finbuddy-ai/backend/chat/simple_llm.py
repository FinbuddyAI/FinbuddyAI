import os
import json
from openai import OpenAI
from typing import List, Dict, Any
from .db_operations import query_database, update_database

class SimpleLLM:
    def __init__(self):
        # Get the root directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(os.path.dirname(current_dir))
        
        # Load configuration
        config_path = os.path.join(root_dir, "config_list.json")
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(
                f"Configuration file not found in {root_dir}. "
                "Please ensure config_list.json exists in the root directory."
            )
        
        # Load configuration from config_list.json
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if not config or not isinstance(config, list) or len(config) == 0:
            raise ValueError("Invalid configuration in config_list.json")
        
        # Get the first configuration
        azure_config = config[0]
        
        # Initialize OpenAI client with Azure configuration
        self.client = OpenAI(
            api_key=azure_config["api_key"],
            base_url=azure_config["base_url"],
            default_headers={
                "api-key": azure_config["api_key"],
                "api-version": azure_config["api_version"]
            }
        )
        
        self.model = azure_config.get("model", "gpt-4")
        self.temperature = 0.7
        self.conversation_history = []
        self.system_prompt = """You are a helpful financial assistant with access to the user's financial database.
        You can query and update the following tables:
        - users: Contains user profile information
        - transactions: Contains financial transactions
        - budgets: Contains budget information
        - goals: Contains financial goals
        
        You can use the following functions:
        - query_database: Execute a SQL query and get results
        - update_database: Execute an update query
        
        Always provide personalized financial advice based on the user's data."""
        
    async def get_response(self, user_input: str) -> str:
        try:
            # Add user input to conversation history
            self.conversation_history.append({"role": "user", "content": user_input})
            
            # Prepare messages for API call
            messages = [
                {"role": "system", "content": self.system_prompt}
            ] + self.conversation_history
            
            # Make API call with tools
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                tools=[{
                    "type": "function",
                    "function": {
                        "name": "query_database",
                        "description": "Execute a SQL query on the database",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "The SQL query to execute"
                                }
                            },
                            "required": ["query"]
                        }
                    }
                }, {
                    "type": "function",
                    "function": {
                        "name": "update_database",
                        "description": "Execute an update query on the database",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "The SQL update query to execute"
                                }
                            },
                            "required": ["query"]
                        }
                    }
                }]
            )
            
            # Handle tool calls
            if response.choices[0].message.tool_calls:
                for tool_call in response.choices[0].message.tool_calls:
                    if tool_call.function.name == "query_database":
                        query = tool_call.function.arguments["query"]
                        results = await query_database(query)
                        # Add results to conversation history
                        self.conversation_history.append({
                            "role": "assistant",
                            "content": f"Query results: {results}"
                        })
                    elif tool_call.function.name == "update_database":
                        query = tool_call.function.arguments["query"]
                        affected_rows = await update_database(query)
                        # Add update result to conversation history
                        self.conversation_history.append({
                            "role": "assistant",
                            "content": f"Update affected {affected_rows} rows"
                        })
            
            # Get assistant's response
            assistant_response = response.choices[0].message.content
            self.conversation_history.append({"role": "assistant", "content": assistant_response})
            
            return assistant_response
            
        except Exception as e:
            error_message = f"Error getting response: {str(e)}"
            if "401" in str(e):
                error_message = "Authentication error: Please check your API key"
            elif "404" in str(e):
                error_message = "Resource not found: Please check your Azure OpenAI endpoint URL"
            return error_message

    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history = [] 