import os
import json
import logging
from typing import Dict, Any, List
from mcp.server import Server
from mcp.types import CreateMessageRequestParams, CreateMessageResult, TextContent, Tool
from mcp.server.models import InitializationOptions
from openai import OpenAI
import asyncio
import signal
from mcp.server.stdio import stdio_server
from dotenv import load_dotenv
from .db_operations import query_database, update_database

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
            
            if not api_key or not base_url:
                raise ValueError("Missing required environment variables: OPENAI_API_KEY and OPENAI_BASE_URL")
            
            logger.debug("Using OpenAI configuration from environment variables")
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url
            )
            logger.debug("Successfully initialized OpenAI client")
            
            self.model = model
            self.temperature = temperature
            
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

    async def list_tools(self) -> List[Tool]:
        """List available tools."""
        return self.tools

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool by name with the given arguments."""
        if name == "query_database":
            return await self.query_database(arguments["query"])
        elif name == "update_database":
            return await self.update_database(arguments["query"])
        else:
            raise ValueError(f"Unknown tool: {name}")

# Create server instance
mcp_server = MCPLLMServer()

async def run_server():
    """Run the MCP server."""
    logger.debug("Starting MCP server")
    try:
        async with stdio_server() as (read, write):
            await mcp_server.run(
                read,
                write,
                InitializationOptions(
                    server_name="finbuddy-llm",
                    server_version="1.0.0",
                    capabilities={
                        "prompts": {"enabled": True},
                        "resources": {"enabled": True},
                        "tools": {"enabled": True},
                        "logging": {"enabled": True},
                        "completion": {"enabled": True}
                    }
                )
            )
    except Exception as e:
        logger.error(f"Error in MCP server main: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    try:
        # Create a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Set up proper signal handling
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: loop.stop())
        
        # Run the server
        loop.run_until_complete(run_server())
    except KeyboardInterrupt:
        logger.info("MCP server shutting down gracefully")
    except Exception as e:
        logger.error(f"Fatal error in MCP server: {str(e)}", exc_info=True)
        raise
    finally:
        # Clean up the event loop
        loop.close() 