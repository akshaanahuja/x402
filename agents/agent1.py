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
import re


def extract_keywords(text: str, max_tags: int = 5) -> list[str]:
    """
    Extract 3-5 keywords/macroconcepts from text.
    Filters out common stop words and returns the most relevant terms.
    """
    # Common stop words to filter out
    stop_words = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", 
        "of", "with", "by", "from", "as", "is", "are", "was", "were", "be", 
        "been", "being", "have", "has", "had", "do", "does", "did", "will", 
        "would", "should", "could", "may", "might", "must", "can", "this", 
        "that", "these", "those", "what", "which", "who", "when", "where", 
        "why", "how", "i", "you", "he", "she", "it", "we", "they", "me", 
        "him", "her", "us", "them", "my", "your", "his", "her", "its", 
        "our", "their", "if", "then", "else", "than", "so", "not", "no", 
        "yes", "all", "each", "every", "some", "any", "many", "much", 
        "more", "most", "other", "another", "such", "only", "just", "now", 
        "then", "here", "there", "up", "down", "out", "off", "over", "under"
    }
    
    # Convert to lowercase and extract words
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())
    
    # Filter out stop words and get unique words
    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    
    # Count frequency and get most common
    from collections import Counter
    word_freq = Counter(keywords)
    
    # Get top keywords (3-5)
    top_keywords = [word for word, _ in word_freq.most_common(max_tags)]
    
    # Ensure we have at least 3 tags, pad with additional common words if needed
    if len(top_keywords) < 3:
        # Get more words if we don't have enough
        all_keywords = [word for word, _ in word_freq.most_common(max_tags * 2)]
        top_keywords = all_keywords[:max_tags]
    
    return top_keywords[:max_tags]
 
# Import Solana wallet and client
AGENT_MEMORY_PATH = os.path.abspath(os.path.join(PROJECT_ROOT, "agent-memory-solana"))
if AGENT_MEMORY_PATH not in sys.path:
    sys.path.append(AGENT_MEMORY_PATH)

from wallets.agent_wallet import get_or_create_agent_wallet
from memory_index_python_client import store_memory


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


@tool
def solana_store_memory(cid: str, tags_csv: str, agent_id: str = "agent_1") -> str:
    """
    Store a memory on Solana blockchain. This creates an on-chain index entry linking the IPFS CID to tags.
    Provide:
    - cid: IPFS Content ID (the CID from ipfs_post_query)
    - tags_csv: comma-separated tags (same tags used for IPFS)
    - agent_id: identifier of the writing agent (default: agent_1)
    Returns the Solana transaction signature as a string.
    """
    try:
        # Parse tags
        tags = [t.strip() for t in (tags_csv or "").split(",") if t.strip()]
        if not tags:
            return "Error: At least one tag is required"
        
        # Get or create agent wallet
        keypair = get_or_create_agent_wallet(agent_id=agent_id, fund_sol=1)
        
        # Store memory on Solana
        tx_signature = store_memory(keypair, cid, tags)
        
        return f"Memory stored on Solana. Transaction: {tx_signature}"
    except Exception as e:
        return f"Error storing memory on Solana: {e}"




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
    tools = [ipfs_post_query, solana_store_memory]
    
    # Create agent with system prompt
    system_prompt = (
        "You are a helpful assistant.\n"
        "- Use ipfs_post_query to store data on IPFS. It returns a CID.\n"
        "- Use solana_store_memory to store the CID and tags on Solana blockchain for discoverability.\n"
        "- When the user asks to persist/store an answer:\n"
        "  1. First call ipfs_post_query with the query, the answer as JSON, and tags to get a CID.\n"
        "  2. Then call solana_store_memory with the CID and the same tags to index it on-chain."
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

        # Automatically generate tags from query and answer
        combined_text = f"{user_query} {output}"
        tags = extract_keywords(combined_text, max_tags=5)
        tags_csv = ",".join(tags)
        
        print(f"\nAuto-generated tags: {tags_csv}")
        
        # Store to IPFS with auto-generated tags
        cid = ipfs_post_query.invoke({
            "query": user_query,
            "result_json": json.dumps({"answer": output}, ensure_ascii=False),
            "tags_csv": tags_csv,
            "agent_id": "agent_1",
        })
        print(f"\n✅ Stored to IPFS. CID: {cid}")
        # Prompt to persist to IPFS and Solana via tools
        print("\nEnter tags to store this answer (comma-separated), or press Enter to skip: ", end="", flush=True)
        tags_csv = sys.stdin.readline().strip()
        if tags_csv:
            # Store on IPFS
            cid = ipfs_post_query.invoke({
                "query": user_query,
                "result_json": json.dumps({"answer": output}, ensure_ascii=False),
                "tags_csv": tags_csv,
                "agent_id": "agent_1",
            })
            print(f"\nStored to IPFS. CID: {cid}")
            
            # Store on Solana
            try:
                solana_result = solana_store_memory.invoke({
                    "cid": cid,
                    "tags_csv": tags_csv,
                    "agent_id": "agent_1",
                })
                print(f"\n{solana_result}")
            except Exception as e:
                print(f"\n⚠️ Warning: Failed to store on Solana: {e}")
                print("   The data is still stored on IPFS with CID:", cid)
        
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(130)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

