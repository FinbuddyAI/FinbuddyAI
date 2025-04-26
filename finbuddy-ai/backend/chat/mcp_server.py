import os
import json
import logging
from typing import Dict, Any, List
from mcp.server import Server
from mcp.types import CreateMessageRequestParams, CreateMessageResult, TextContent, Tool
from mcp.server.models import InitializationOptions
from openai import OpenAI
from dotenv import load_dotenv
from .db_operations import query_database, update_database
from fastapi import WebSocket, WebSocketDisconnect
import asyncio

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class MCPLLMServer(Server):
    def __init__(self):
        super().__init__("finbuddy-llm")
        logger.debug("Initializing MCPLLMServer")
        
        try:
            # Get configuration from environment variables
            api_key = os.getenv("OPENAI_API_KEY")
            base_url = os.getenv("OPENAI_BASE_URL")
            model = os.getenv("OPENAI_MODEL", "gpt-4")
            temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
            
            # Fallback to config_list.json if env vars are missing
            if not api_key or not base_url:
                logger.warning("Environment variables for OpenAI not found, falling back to config_list.json")
                config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config_list.json')
                try:
                    with open(config_path, 'r') as f:
                        configs = json.load(f)
                    cfg = configs[0]
                    api_key = cfg.get("api_key")
                    base_url = cfg.get("base_url")
                    model = cfg.get("model", model)
                except Exception as e:
                    logger.error(f"Failed to load config_list.json: {e}")
                    raise ValueError("Missing OpenAI configuration and failed to load config_list.json") from e
            
            logger.debug(f"Using OpenAI configuration: model={model}, base_url={base_url}")
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url
            )
            logger.debug("Successfully initialized OpenAI client")
            
            self.model = model
            self.temperature = temperature
            self.connected_clients = set()
            
            # Define tools
            self.tools = [
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
            
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            raise

    async def handle_websocket(self, websocket: WebSocket):
        """Handle WebSocket connection for MCP communication."""
        try:
            await websocket.accept()
            self.connected_clients.add(websocket)
            logger.debug("WebSocket connection accepted")
            
            # Wait for initialization message
            init_message = await websocket.receive_text()
            init_data = json.loads(init_message)
            
            if init_data["type"] != "initialize":
                raise ValueError("Invalid initialization message")
            
            # Send initialization response
            await websocket.send_text(json.dumps({
                "type": "initialized",
                "server_name": "finbuddy-llm",
                "server_version": "1.0.0",
                "capabilities": {
                    "prompts": {"enabled": True},
                    "resources": {"enabled": True},
                    "tools": {"enabled": True},
                    "logging": {"enabled": True},
                    "completion": {"enabled": True}
                }
            }))
            
            # Handle messages
            while True:
                try:
                    message = await websocket.receive_text()
                    data = json.loads(message)
                    
                    if data["type"] == "register_tools":
                        # Acknowledge tool registration
                        await websocket.send_text(json.dumps({
                            "type": "tool_result",
                            "result": {"status": "success"}
                        }))
                    elif data["type"] == "call_tool":
                        result = await self.handle_tool_call(data)
                        await websocket.send_text(json.dumps({
                            "type": "tool_result",
                            "result": result
                        }))
                except WebSocketDisconnect:
                    logger.debug("Client disconnected")
                    break
                except Exception as e:
                    logger.error(f"Error handling message: {str(e)}")
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": str(e)
                    }))
        except Exception as e:
            logger.error(f"WebSocket error: {str(e)}")
        finally:
            self.connected_clients.discard(websocket)
            await websocket.close()

    async def handle_tool_call(self, message: Dict[str, Any]) -> Any:
        """Handle tool calls from the client."""
        tool_name = message.get("name")
        arguments = message.get("arguments", {})
        
        if tool_name == "query_database":
            return await self.query_database(arguments.get("query", ""))
        elif tool_name == "update_database":
            return await self.update_database(arguments.get("query", ""))
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    async def query_database(self, query: str) -> str:
        """Query the database with a SQL query."""
        try:
            result = await query_database(query)
            return str(result)
        except Exception as e:
            logger.error(f"Error querying database: {str(e)}")
            raise

    async def update_database(self, query: str) -> str:
        """Update the database with a SQL query."""
        try:
            result = await update_database(query)
            return str(result)
        except Exception as e:
            logger.error(f"Error updating database: {str(e)}")
            raise

# Create server instance
mcp_server = MCPLLMServer() 