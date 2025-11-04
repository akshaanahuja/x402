import os
import sys
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.tools import tool


@tool
def tool_2_api_call(input_data: str) -> str:
    """
    Tool 2: This is a boilerplate tool that can call some unique API.
    Replace this with your actual API call logic.
    
    Args:
        input_data: The input data to process
        
    Returns:
        A string response from the API
    """
    # TODO: Implement actual API call here
    return f"Tool 2 processed: {input_data}"


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
    tools = [tool_2_api_call]
    
    # Create agent with system prompt
    system_prompt = "You are a helpful assistant with access to Tool 2. Use it when appropriate."
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

