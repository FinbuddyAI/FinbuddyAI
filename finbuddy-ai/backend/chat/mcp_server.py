import os
import json
from typing import Dict, Any
from mcp.server import Server
from mcp.types import CreateMessageRequestParams, CreateMessageResult, TextContent
from mcp.server.models import InitializationOptions
from openai import OpenAI

class MCPLLMServer(Server):
    def __init__(self):
        super().__init__("finbuddy-llm")
        
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

    async def create_message(self, params: CreateMessageRequestParams) -> CreateMessageResult:
        """Handle message creation requests."""
        try:
            # Prepare messages for the API call
            messages = []
            
            # Add system prompt if provided
            if "system_prompt" in params.arguments:
                messages.append({
                    "role": "system",
                    "content": params.arguments["system_prompt"]
                })
            
            # Add conversation history
            if "conversation_history" in params.arguments:
                messages.extend(params.arguments["conversation_history"])
            
            # Call Azure OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature
            )
            
            # Format response
            return CreateMessageResult(
                role="assistant",
                content=TextContent(
                    type="text",
                    text=response.choices[0].message.content
                ),
                model=self.model,
                stopReason="endTurn"
            )
            
        except Exception as e:
            return CreateMessageResult(
                role="assistant",
                content=TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                ),
                model=self.model,
                stopReason="error"
            )

if __name__ == "__main__":
    import asyncio
    from mcp.server.stdio import stdio_server
    
    async def run():
        server = MCPLLMServer()
        async with stdio_server() as (read, write):
            await server.run(
                read,
                write,
                InitializationOptions(
                    server_name="finbuddy-llm",
                    server_version="1.0.0",
                    capabilities={
                        "prompts": {"enabled": True},
                        "resources": {"enabled": True},
                        "tools": {"enabled": True}
                    }
                )
            )
    
    asyncio.run(run()) 