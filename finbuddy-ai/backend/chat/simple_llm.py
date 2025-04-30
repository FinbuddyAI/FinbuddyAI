import os
import json
import asyncio
import logging
from typing import List, Dict, Any
from mcp.types import Tool
from .db_operations import query_database, update_database
import traceback
from dotenv import load_dotenv
import websockets

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
        # logger.debug("Initializing SimpleLLM")
        
        # Load environment variables
        load_dotenv()
        
        # Initialize configuration
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4")
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        
        # Fallback to config_list.json if OPENAI_API_KEY is missing
        if not self.api_key:
            logger.warning("Environment variable OPENAI_API_KEY not found, falling back to config_list.json")
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config_list.json')
            try:
                with open(config_path, 'r') as f:
                    configs = json.load(f)
                cfg = configs[0]
                self.api_key = cfg.get("api_key")
                self.base_url = cfg.get("base_url", self.base_url)
                self.model = cfg.get("model", self.model)
            except Exception as e:
                logger.error(f"Failed to load config_list.json: {e}")
                raise ValueError("OPENAI_API_KEY environment variable required and fallback failed") from e
        
        # Initialize conversation history
        self.conversation_history = []
        
        # Initialize MCP session
        self.websocket = None
        self._init_task = None
        self.initialized = False
        self.ws_url = "ws://localhost:8000/ws/mcp"
        
    async def initialize(self):
        """Initialize the MCP session asynchronously."""
        logger.debug("Starting initialization")
        if self._init_task is None:
            logger.debug("Creating initialization task")
            self._init_task = asyncio.create_task(self._init_mcp_session())
        await self._init_task
        logger.debug("Initialization complete")
    
    async def _init_mcp_session(self):
        """Initialize MCP session using WebSocket connection."""
        try:
            logger.debug("Starting MCP session initialization")
            
            # Connect to WebSocket
            self.websocket = await websockets.connect(self.ws_url)
            logger.debug("WebSocket connection established")
            
            # Send initialization message
            init_message = {
                "type": "initialize",
                "server_name": "finbuddy-llm",
                "server_version": "1.0.0",
                "capabilities": {
                    "prompts": {"enabled": True},
                    "resources": {"enabled": True},
                    "tools": {"enabled": True},
                    "logging": {"enabled": True},
                    "completion": {"enabled": True}
                }
            }
            
            await self.websocket.send(json.dumps(init_message))
            logger.debug("Sent initialization message")
            
            # Wait for initialization response
            response = await self.websocket.recv()
            init_data = json.loads(response)
            
            if init_data["type"] != "initialized":
                raise ValueError("Invalid initialization response")
            
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
            
            # Send tool registration message
            await self.websocket.send(json.dumps({
                "type": "register_tools",
                "tools": [tool.dict() for tool in tools]
            }))
            logger.debug("Sent tool registration message")
            
            # Wait for registration response
            response = await self.websocket.recv()
            result = json.loads(response)
            logger.debug(f"Received tool registration response: {result}")
            
            if result["type"] != "tool_result" or not result["result"].get("status") == "success":
                raise ValueError("Tool registration failed")
            
            logger.debug("Successfully registered tools with MCP")
            
        except Exception as e:
            logger.error(f"Error in tool registration: {str(e)}", exc_info=True)
            raise
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool by name with the given arguments."""
        if not self.initialized:
            await self.initialize()
        
        try:
            # Send tool call message
            await self.websocket.send(json.dumps({
                "type": "call_tool",
                "name": name,
                "arguments": arguments
            }))
            
            # Wait for tool result
            response = await self.websocket.recv()
            result = json.loads(response)
            
            if result["type"] == "error":
                raise ValueError(result["message"])
            
            return result["result"]
            
        except Exception as e:
            logger.error(f"Error calling tool {name}: {str(e)}")
            raise

    async def get_response(self, message: str) -> str:
        """Get a response from the LLM for the given message."""
        logger.debug(f"Getting response for message: {message}")
        try:
            # Ensure MCP session is initialized
            if self.websocket is None:
                logger.debug("MCP session not initialized, initializing now")
                await self.initialize()
            
            # Add user message to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": message
            })
            logger.debug("Added user message to conversation history")
            
            # Create MCP prompt
            prompt = {
                "type": "prompt",
                "system_prompt": "You are a helpful AI financial advisor. Provide accurate and helpful financial advice.",
                "conversation_history": self.conversation_history
            }
            logger.debug("Created MCP prompt")
            
            # Send prompt to MCP
            await self.websocket.send(json.dumps(prompt))
            logger.debug("Sent prompt to MCP")
            
            # Wait for response
            response = await self.websocket.recv()
            logger.debug("Received response from MCP")
            
            # Handle tool calls if any
            if response.startswith("tool_call:"):
                tool_name = response[len("tool_call:"):].split("|")[0]
                tool_arguments = json.loads(response[len("tool_call:"):].split("|")[1])
                logger.debug(f"Processing tool call: {tool_name}")
                result = await self.call_tool(tool_name, tool_arguments)
                self.conversation_history.append({
                    "role": "tool",
                    "name": tool_name,
                    "content": str(result)
                })
                logger.debug("Tool call processed successfully")
                
                # Get final response after tool call
                logger.debug("Getting final response after tool call")
                try:
                    async with asyncio.timeout(60.0):  # 60 second timeout
                        response = await self.websocket.recv()
                except asyncio.TimeoutError:
                    logger.error("Timeout while waiting for final MCP response")
                    return "I apologize, but the request timed out while processing tools. Please try again."
            
            # Add assistant response to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": response
            })
            logger.debug("Added assistant response to conversation history")
            
            return response
            
        except Exception as e:
            logger.error(f"Error in get_response: {str(e)}", exc_info=True)
            return f"Error: {str(e)}"
    
    def clear_history(self):
        """Clear the conversation history."""
        logger.debug("Clearing conversation history")
        self.conversation_history = [] 