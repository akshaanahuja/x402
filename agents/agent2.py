import os
import sys
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.tools import tool
import json

# Make project root importable so we can import ipfs.ipfs
# PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# if PROJECT_ROOT not in sys.path:
#     sys.path.append(PROJECT_ROOT)

from ipfs.ipfs import fetch_query as ipfs_fetch




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
        try:
            data = ipfs_fetch(cid)
            return json.dumps(data)
        except Exception as e:
            return f"Error fetching from IPFS: {e}"

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
        agent = create_agent_instance()
        
        print("Agent 2 ready. Enter your query: ", end="", flush=True)
        user_query = sys.stdin.readline().strip()
        
        if not user_query:
            print("No query provided.")
            sys.exit(1)
        
        response = agent.invoke({"messages": [("human", user_query)]})
        output = response.get("messages", [])[-1].content if response.get("messages") else str(response)
        print("\nResponse:\n" + str(output))
        
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(130)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

