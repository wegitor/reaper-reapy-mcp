import logging
import argparse

from mcp.server.fastmcp import FastMCP
from .mcp_tools import setup_mcp_tools

from .reaper_controller import ReaperController

def main():
    # Setup logging
    logging.basicConfig(
        level=logging.WARNING,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    logger.info("Starting MCP server for Reaper...")
    
    try:
        # Create Reaper controller
        logger.info("Initializing ReaperController...")
        controller = ReaperController(debug=True)
        logger.info("ReaperController initialized successfully.")
        
        parser = argparse.ArgumentParser(description = "")
        parser.add_argument("--mode", type = str, help = "MCP server mode stdio or http", default = "std")
        parser.add_argument("--http-host", type = str, help = "MCP server http mode configurtion host", default = "127.0.0.1")
        parser.add_argument("--http-port", type = int, help = "MCP server http mode configurtion port", default = 3957)
        args = parser.parse_args()
        args_dict = vars(args)

        # Create MCP server
        if args.mode == "std":
            mcp = FastMCP("Reaper Control")
        elif args.mode == "http":
            mcp = FastMCP("Reaper Control", host = args_dict['http_host'], port = args_dict['http_port'])
        
        # Setup MCP tools
        setup_mcp_tools(mcp, controller)
        
        # Run MCP server
        logger.info("Starting MCP server...")

        # Run MCP server
        logger.info("Starting MCP server...")
        if args.mode == "std":
            mcp.run()
        elif args.mode == "http":
            mcp.run(transport='streamable-http')
        
    except Exception as e:
        logger.error(f"Error running MCP server: {e}")
        raise

if __name__ == "__main__":
    main()