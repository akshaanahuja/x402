import os
import sys
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.tools import tool
import json

# Make project root importable so we can import ipfs.ipfs
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from ipfs.ipfs import post_query as ipfs_post


@tool
def ipfs_post_query(query: str, result_json: str, tags_csv: str, agent_id: str = "agent_1") -> str:
    """
    Store a record in IPFS. Provide:
    - query: the original question
    - result_json: JSON string of the answer/result (or plain text; will be wrapped)
    - tags_csv: comma-separated tags
    - agent_id: identifier of the writing agent (default: agent_1)
    Returns the CID as a string.
    """
    try:
        try:
            result = json.loads(result_json)
        except Exception:
            result = {"answer": result_json}
        tags = [t.strip() for t in (tags_csv or "").split(",") if t.strip()]
        cid = ipfs_post(query=query, result=result, tags=tags, agent_id=agent_id)
        return cid
    except Exception as e:
        return f"Error posting to IPFS: {e}"




def create_agent_instance():
    """Create and return an agent with Tool 1"""
    # Load environment variables
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    
    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    # Define tools
    tools = [ipfs_post_query]
    
    # Create agent with system prompt
    system_prompt = (
        "You are a helpful assistant.\n"
        "- Use Tool 1 for its specialty when needed.\n"
        "- When the user asks to persist/store an answer, call ipfs_post_query with the query, the answer as JSON, and tags."
    )
    agent = create_agent(llm, tools, system_prompt=system_prompt)
    
    return agent


if __name__ == "__main__":
    try:
        agent = create_agent_instance()
        
        print("Agent 1 ready. Enter your query: ", end="", flush=True)
        user_query = sys.stdin.readline().strip()
        
        if not user_query:
            print("No query provided.")
            sys.exit(1)
        
        response = agent.invoke({"messages": [("human", user_query)]})
        output = response.get("messages", [])[-1].content if response.get("messages") else str(response)
        print("\nResponse:\n" + str(output))

        # Prompt to persist to IPFS via tool
        print("\nEnter tags to store this answer to IPFS (comma-separated), or press Enter to skip: ", end="", flush=True)
        tags_csv = sys.stdin.readline().strip()
        if tags_csv:
            cid = ipfs_post_query.invoke({
                "query": user_query,
                "result_json": json.dumps({"answer": output}, ensure_ascii=False),
                "tags_csv": tags_csv,
                "agent_id": "agent_1",
            })
            print(f"\nStored to IPFS. CID: {cid}")
        
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(130)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

