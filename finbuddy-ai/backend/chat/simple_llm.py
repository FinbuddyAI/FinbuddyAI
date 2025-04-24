import os
import json
import asyncio
import sys
from typing import List, Dict, Any
from mcp import ClientSession, StdioServerParameters
from mcp.types import CreateMessageRequestParams, Tool
from mcp.client.stdio import stdio_client
from .db_operations import query_database, update_database

class SimpleLLM:
    def __init__(self):
        # Initialize conversation history
        self.conversation_history = []
        
        # Initialize MCP session
        self.mcp_session = None
        self._init_task = None
        
        # Add project root to Python path
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
    
    async def initialize(self):
        """Initialize the MCP session asynchronously."""
        if self._init_task is None:
            self._init_task = asyncio.create_task(self._init_mcp_session())
        await self._init_task
    
    async def _init_mcp_session(self):
        """Connect to the existing MCP server."""
        # Get the absolute path to mcp_server.py
        mcp_server_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_server.py")
        
        # Create server parameters for stdio connection
        server_params = StdioServerParameters(
            command="python",  # Executable
            args=[mcp_server_path],  # Direct path to the script
            env=None  # Optional environment variables
        )
        
        # Connect to the MCP server using stdio_client
        async with stdio_client(server_params) as (read, write):
            self.mcp_session = ClientSession(read, write)
            
            # Register tools with MCP
            await self._register_tools()
    
    async def _register_tools(self):
        """Register available tools with MCP."""
        tools = [
            Tool(
                name="query_database",
                description="Query the database with a SQL query",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The SQL query to execute"
                        }
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="update_database",
                description="Update the database with a SQL query",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The SQL query to execute"
                        }
                    },
                    "required": ["query"]
                }
            )
        ]
        
        # Register tools using the correct method
        await self.mcp_session.call_tool("register_tools", {"tools": tools})
    
    async def get_response(self, message: str) -> str:
        """Get a response from the LLM for the given message."""
        try:
            # Ensure MCP session is initialized
            if self.mcp_session is None:
                await self.initialize()
            
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