import os
import json
import asyncio
import sys
import logging
from typing import List, Dict, Any
from mcp import ClientSession, StdioServerParameters
from mcp.types import CreateMessageRequestParams, Tool
from mcp.client.stdio import stdio_client
from .db_operations import query_database, update_database
import traceback
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)  # Change to INFO level
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Keep DEBUG level for our chat logs

# Silence other noisy loggers
logging.getLogger('matplotlib').setLevel(logging.WARNING)
logging.getLogger('docker').setLevel(logging.WARNING)
logging.getLogger('autogen.import_utils').setLevel(logging.WARNING)

class SimpleLLM:
    def __init__(self):
        logger.debug("Initializing SimpleLLM")
        
        # Load environment variables
        load_dotenv()
        
        # Initialize configuration
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4")
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # Initialize conversation history
        self.conversation_history = []
        
        # Initialize MCP session
        self.mcp_session = None
        self._init_task = None
        self.initialized = False
        
        # Add project root to Python path
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
            logger.debug(f"Added {project_root} to Python path")
    
    async def initialize(self):
        """Initialize the MCP session asynchronously."""
        logger.debug("Starting initialization")
        if self._init_task is None:
            logger.debug("Creating initialization task")
            self._init_task = asyncio.create_task(self._init_mcp_session())
        await self._init_task
        logger.debug("Initialization complete")
    
    async def _init_mcp_session(self):
        """Initialize MCP session using the SDK's client implementation."""
        try:
            logger.debug("Starting MCP session initialization")
            
            # Create server parameters for stdio connection
            server_params = StdioServerParameters(
                command="python",
                args=["-m", "backend.chat.mcp_server"],
                env={
                    "OPENAI_API_KEY": self.api_key,
                    "OPENAI_BASE_URL": self.base_url,
                    "OPENAI_MODEL": self.model,
                    "OPENAI_TEMPERATURE": str(self.temperature)
                }
            )
            
            # Create client session
            async with stdio_client(server_params) as (read, write):
                self.mcp_session = ClientSession(read, write)
                await self.mcp_session.initialize()
                
                # Register tools
                await self._register_tools()
                
                self.initialized = True
                logger.debug("MCP session initialized successfully")
            
        except Exception as e:
            logger.error(f"Error in MCP session initialization: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    async def _register_tools(self):
        """Register available tools with MCP."""
        logger.debug("Registering tools")
        try:
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
            
            await self.mcp_session.register_tools(tools)
            logger.debug("Successfully registered tools with MCP")
            
        except Exception as e:
            logger.error(f"Error in tool registration: {str(e)}", exc_info=True)
            raise
    
    async def get_response(self, message: str) -> str:
        """Get a response from the LLM for the given message."""
        logger.debug(f"Getting response for message: {message}")
        try:
            # Ensure MCP session is initialized
            if self.mcp_session is None:
                logger.debug("MCP session not initialized, initializing now")
                await self.initialize()
            
            # Add user message to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": message
            })
            logger.debug("Added user message to conversation history")
            
            # Create MCP prompt
            prompt = CreateMessageRequestParams(
                arguments={
                    "system_prompt": "You are a helpful AI financial advisor. Provide accurate and helpful financial advice.",
                    "conversation_history": self.conversation_history
                }
            )
            logger.debug("Created MCP prompt")
            
            # Get response from MCP with timeout
            logger.debug("Sending request to MCP")
            try:
                async with asyncio.timeout(60.0):  # 60 second timeout
                    response = await self.mcp_session.create_message(prompt)
                    logger.debug("Received response from MCP")
            except asyncio.TimeoutError:
                logger.error("Timeout while waiting for MCP response")
                return "I apologize, but the request timed out. Please try again."
            
            # Handle tool calls if any
            if response.tool_calls:
                logger.debug(f"Processing {len(response.tool_calls)} tool calls")
                for tool_call in response.tool_calls:
                    if tool_call.function.name == "query_database":
                        logger.debug("Executing database query")
                        result = await query_database(tool_call.function.arguments["query"])
                        self.conversation_history.append({
                            "role": "tool",
                            "name": "query_database",
                            "content": str(result)
                        })
                    elif tool_call.function.name == "update_database":
                        logger.debug("Executing database update")
                        result = await update_database(tool_call.function.arguments["query"])
                        self.conversation_history.append({
                            "role": "tool",
                            "name": "update_database",
                            "content": str(result)
                        })
                
                # Get final response after tool calls
                logger.debug("Getting final response after tool calls")
                try:
                    async with asyncio.timeout(60.0):  # 60 second timeout
                        response = await self.mcp_session.create_message(prompt)
                except asyncio.TimeoutError:
                    logger.error("Timeout while waiting for final MCP response")
                    return "I apologize, but the request timed out while processing tools. Please try again."
            
            # Add assistant response to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": response.content.text
            })
            logger.debug("Added assistant response to conversation history")
            
            return response.content.text
            
        except Exception as e:
            logger.error(f"Error in get_response: {str(e)}", exc_info=True)
            return f"Error: {str(e)}"
    
    def clear_history(self):
        """Clear the conversation history."""
        logger.debug("Clearing conversation history")
        self.conversation_history = [] 