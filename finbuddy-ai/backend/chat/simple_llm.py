import os
import json
import asyncio
from typing import List, Dict, Any
from mcp import ClientSession, StdioServerParameters
from mcp.types import CreateMessageRequestParams
from .db_operations import query_database, update_database

class SimpleLLM:
    def __init__(self):
        # Initialize conversation history
        self.conversation_history = []
        
        # Initialize MCP session
        self.mcp_session = None
        self._init_mcp_session()
    
    def _init_mcp_session(self):
        """Initialize the MCP session with server parameters."""
        server_params = StdioServerParameters(
            command=["python", "-m", "backend.chat.mcp_server"]
        )
        
        self.mcp_session = ClientSession(server_params)
        
        # Register tools with MCP
        self._register_tools()
    
    def _register_tools(self):
        """Register available tools with MCP."""
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "query_database",
                    "description": "Query the database with a SQL query",
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
            },
            {
                "type": "function",
                "function": {
                    "name": "update_database",
                    "description": "Update the database with a SQL query",
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
            }
        ]
        
        self.mcp_session.register_tools(tools)
    
    async def get_response(self, message: str) -> str:
        """Get a response from the LLM for the given message."""
        try:
            # Add user message to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": message
            })
            
            # Create MCP prompt
            prompt = CreateMessageRequestParams(
                arguments={
                    "system_prompt": "You are a helpful AI financial advisor. Provide accurate and helpful financial advice.",
                    "conversation_history": self.conversation_history
                }
            )
            
            # Get response from MCP
            response = await self.mcp_session.create_message(prompt)
            
            # Handle tool calls if any
            if response.tool_calls:
                for tool_call in response.tool_calls:
                    if tool_call.function.name == "query_database":
                        result = await query_database(tool_call.function.arguments["query"])
                        self.conversation_history.append({
                            "role": "tool",
                            "name": "query_database",
                            "content": str(result)
                        })
                    elif tool_call.function.name == "update_database":
                        result = await update_database(tool_call.function.arguments["query"])
                        self.conversation_history.append({
                            "role": "tool",
                            "name": "update_database",
                            "content": str(result)
                        })
                
                # Get final response after tool calls
                response = await self.mcp_session.create_message(prompt)
            
            # Add assistant response to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": response.content.text
            })
            
            return response.content.text
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history = [] 