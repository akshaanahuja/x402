import os
import sys
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.tools import tool

import requests
import json


# IN OUR FLOW, WE WILL GIVE EACH AGENT ACCESS TO ONE SPECIAL API AND IN THE SYSTEM PROMPT, WE WILL SAY TO USE THE API/TOOL WHEN ASKED ABOUT THIS TOPIC, BUT IF THE QUESTION IS NOT ABOUT ITS SPECIALTY, IT WILL CALL THE SOLANA FUNCTION GETMEMORYBYTAGS TO FIND CIDS OF RELATED PAST QUEIRES FROM OTHER AGENTS, PAY VIA X402 TO VIEW THESE CIDS AND THEN READ THEM FROM IPFS AND THEN RETURN THE RESULT VALUE IN THE IPFS RETURN. 

@tool
def get_exchange_rates(base_currency: str = "USD") -> str:
    """
    USE THIS TOOL whenever the user asks about cryptocurrency prices, exchange rates, 
    or currency conversions. This tool fetches REAL-TIME exchange rates from CoinAPI.
    
    Examples of when to use:
    - "What is the price of BTC?" -> use base_currency="BTC"
    - "What is BTC worth in USD?" -> use base_currency="BTC" 
    - "Show me USD exchange rates" -> use base_currency="USD"
    - "How much is 1 ETH worth?" -> use base_currency="ETH"
    
    Args:
        base_currency: The base currency code (e.g., "USD", "BTC", "ETH"). Defaults to "USD".
        For Bitcoin questions, use "BTC". For Ethereum, use "ETH". For US Dollar, use "USD".
        
    Returns:
        A JSON string containing exchange rates, or an error message if the API call fails.
        ALWAYS call this tool - never make up prices or claim you cannot access them.
    """
    # Step 1: Get API key from environment variables
    # Make sure .env is loaded (it should be, but double-check)
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
    api_key = os.getenv("COINAPI_KEY")
    if not api_key:
        return "Error: COINAPI_KEY not found in environment variables. Please add 'COINAPI_KEY=your_key_here' to your agents/.env file."
    
    # Step 2: Set up the API endpoint
    # CoinAPI endpoint: GET https://rest.coinapi.io/v1/exchangerate/{asset_id_base}
    base_url = "https://rest.coinapi.io/v1/exchangerate"
    url = f"{base_url}/{base_currency}"
    
    # Step 3: Set up headers with API key
    headers = {
        "X-CoinAPI-Key": api_key,
        "Accept": "application/json"
    }
    
    try:
        # Step 4: Make the API request
        response = requests.get(url, headers=headers, timeout=10)
        
        # Step 5: Handle the response
        if response.status_code == 200:
            data = response.json()
            # Format the response nicely for the LLM
            rates = []
            for rate in data.get("rates", [])[:10]:  # Limit to first 10 for readability
                rates.append(f"{rate.get('asset_id_quote')}: {rate.get('rate')}")
            
            result = {
                "base_currency": base_currency,
                "timestamp": data.get("time"),
                "rates": rates,
                "total_rates": len(data.get("rates", []))
            }
            return json.dumps(result, indent=2)
        elif response.status_code == 429:
            return f"Error: CoinAPI rate limit exceeded. Status code 429. You may have exceeded your API quota. Check your CoinAPI dashboard for usage limits. Response: {response.text}"
        elif response.status_code == 401:
            return f"Error: CoinAPI authentication failed. Status code 401. Your COINAPI_KEY may be invalid or missing. Check your .env file. Response: {response.text}"
        else:
            return f"Error: CoinAPI returned status code {response.status_code}. Response: {response.text}"
            
    except requests.exceptions.RequestException as e:
        return f"Error making API request: {str(e)}"
    except Exception as e:
        return f"Error processing API response: {str(e)}"


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
    tools = [get_exchange_rates]
    
    # Create agent with system prompt
    system_prompt = """You are a helpful assistant with access to cryptocurrency exchange rate data.
    When users ask about exchange rates, currency conversions, or cryptocurrency prices, 
    YOU MUST use the get_exchange_rates tool to fetch current data from CoinAPI.
    NEVER make up exchange rates or claim you cannot access the data - ALWAYS use the tool.
    If the tool returns an error, report that error to the user exactly as it appears."""
    agent = create_agent(llm, tools, system_prompt=system_prompt, debug=True)
    
    return agent


if __name__ == "__main__":
    try:
        agent = create_agent_instance()
        
        print("Agent 1 ready. Enter your query: ", end="", flush=True)
        user_query = sys.stdin.readline().strip()
        
        if not user_query:
            print("No query provided.")
            sys.exit(1)
        
        # Enable verbose mode to see what the agent is doing
        print("\n[DEBUG] Calling agent with query:", user_query)
        response = agent.invoke({"messages": [("human", user_query)]})
        
        # Print full response for debugging
        print("\n[DEBUG] Full agent response:", json.dumps(response, indent=2, default=str))
        
        # Extract output
        output = response.get("messages", [])[-1].content if response.get("messages") else str(response)
        print("\nResponse:\n" + str(output))
        
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(130)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

