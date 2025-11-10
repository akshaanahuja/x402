import os
import sys
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.tools import tool
import json
import traceback
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Make project root importable so we can import ipfs.ipfs
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from ipfs.ipfs import fetch_query as ipfs_fetch
import re


#agent2 needs to be able to call solana fetch memory by tags to find similar past queries - needs a tool that can read from ipfs using a cid and a tool that can call solana fetch memory by tags


def create_agent_instance():
    """Create and return an agent with Tool 2"""
    # Load environment variables
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    
    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    # Define tools
    @tool
    def ipfs_fetch_by_cid(cid: str) -> str:
        """
        Fetch a stored record from IPFS by CID and return it as a JSON string.
        """
        logger.info(f"Attempting to fetch CID from IPFS: {cid}")
        try:
            logger.debug(f"Calling ipfs_fetch with CID: {cid}")
            data = ipfs_fetch(cid)
            logger.info(f"Successfully fetched data from IPFS for CID: {cid}")
            logger.debug(f"Fetched data: {json.dumps(data, indent=2)}")
            return json.dumps(data, indent=2)
        except ImportError as e:
            error_msg = f"Import error - IPFS module not available: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            return f"Error: IPFS module import failed. Details: {error_msg}"
        except AttributeError as e:
            error_msg = f"Attribute error - IPFS API method not found: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            return f"Error: IPFS API method issue. Details: {error_msg}"
        except ConnectionError as e:
            error_msg = f"Connection error - Cannot connect to IPFS gateway: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            return f"Error: Cannot connect to IPFS gateway. Check if IPFS daemon is running or gateway is accessible. Details: {error_msg}"
        except Exception as e:
            error_type = type(e).__name__
            error_msg = f"{error_type}: {str(e)}\nFull traceback:\n{traceback.format_exc()}"
            logger.error(f"Unexpected error fetching from IPFS (CID: {cid}): {error_msg}")
            return f"Error fetching from IPFS (CID: {cid}):\nType: {error_type}\nMessage: {str(e)}\nTraceback: {traceback.format_exc()}"

    tools = [ipfs_fetch_by_cid]
    
    # Create agent with system prompt
    system_prompt = (
        "You are a helpful assistant.\n"
        "- Use Tool 2 for its specialty when needed.\n"
        "- When the user provides a CID or asks to retrieve a past record, call ipfs_fetch_by_cid."
    )
    agent = create_agent(llm, tools, system_prompt=system_prompt)
    
    return agent


if __name__ == "__main__":
    try:
        logger.info("Initializing Agent 2")
        agent = create_agent_instance()
        logger.info("Agent 2 initialized successfully")
        
        print("Agent 2 ready. Enter your query: ", end="", flush=True)
        user_query = sys.stdin.readline().strip()
        
        if not user_query:
            print("No query provided.")
            logger.warning("No query provided by user")
            sys.exit(1)
        
        logger.info(f"Processing user query: {user_query}")
        response = agent.invoke({"messages": [("human", user_query)]})
        logger.debug(f"Agent response structure: {type(response)}")
        logger.debug(f"Agent response keys: {response.keys() if isinstance(response, dict) else 'Not a dict'}")
        
        output = response.get("messages", [])[-1].content if response.get("messages") else str(response)
        logger.info(f"Extracted output from agent response")
        print("\nResponse:\n" + str(output))
        
    except KeyboardInterrupt:
        logger.info("User interrupted (Ctrl+C)")
        print("\nCancelled.")
        sys.exit(130)
    except Exception as e:
        error_type = type(e).__name__
        error_msg = f"{error_type}: {str(e)}\nFull traceback:\n{traceback.format_exc()}"
        logger.error(f"Fatal error in Agent 2: {error_msg}")
        print(f"\nError: {error_type}: {e}")
        print(f"\nFull error details:\n{traceback.format_exc()}")
        sys.exit(1)

