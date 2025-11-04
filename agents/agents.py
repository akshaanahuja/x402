# from typing import Dict, List, Optional
# import json
# import os
# import sys
# from dotenv import load_dotenv


# def _extract_tags(text: str, max_tags: int = 8) -> List[str]:
#     tokens = [t.strip(".,!?;:\"'()[]{}-").lower() for t in text.split()]
#     tokens = [t for t in tokens if t and t.isalnum() and len(t) > 2]
#     seen = set()
#     tags: List[str] = []
#     for t in tokens:
#       # TODO: add logic here that will extract keywords from the query and pass them as tags to our resulting json struct
#         if t not in seen:
#             seen.add(t)
#             tags.append(t)
#         if len(tags) >= max_tags:
#             break
#     return tags


# def agent_answer_and_store(query: str) -> Dict[str, object]:
#     """
#     Agent 1
#     1) Take in a query
#     2) Answer the query (OpenAI LLM)
#     3) Return a JSON-like record suitable for writing to IPFS
#        { query: str, result: str, agent_id: str, tag: List[str] }
#     (Leave actual IPFS write blank for caller to implement.)
#     """
#     try:
#         from langchain.chat_models import init_chat_model

#         api_key = os.getenv("OPENAI_API_KEY")
#         if not api_key:
#             raise RuntimeError("OPENAI_API_KEY is not set")

#         llm = init_chat_model(model="gpt-4o-mini", model_provider="openai", temperature=0)
#         msg = llm.invoke(query)
#         content = getattr(msg, "content", None)
#         result = content.strip() if isinstance(content, str) else ""
#         if not result:
#             result = "(empty response from LLM)"
#     except Exception as e:
#         result = f"(LLM error: {e})"

#     record: Dict[str, object] = {
#         "query": query,
#         "result": result,
#         "agent_id": "agent_1",
#         "tag": _extract_tags(query),
#     }

#     # TODO: Write `record` to IPFS here.

#     return record


# def agent_search_and_unlock(query: str, past_entries: List[Dict[str, object]]) -> Dict[str, object]:
#     """
#     Agent 2
#     1) Take in a query
#     2) Generate tags for this query
#     3) Pay a flat fee via x402 to Agent 1 to unlock the query and result
#     4. call fetch_memory_by_tags in client.ts
#     5. solana program will return the cid's associated with those tags
#     6. read from ipfs those returned cid's
#     7. return the result from the data that is returned from ipfs



#     `past_entries` is the list of JSON-like records previously written to IPFS
#     (supplied by the caller). Each entry must have keys: query, result, agent_id, tag[List[str]].
#     """
#     q_tags = set(_extract_tags(query))

#     # TODO: Pay via x402 here (flat fee). If payment fails, return an error.

#     match: Optional[Dict[str, object]] = None
#     for entry in past_entries:
#         entry_tags = set(entry.get("tag", []) if isinstance(entry.get("tag"), list) else [])
#         if q_tags & entry_tags:
#             match = entry
#             break

#     if match is None:
#         return {"unlocked": False, "message": "No matching tags found in past entries."}

#     return {
#         "unlocked": True,
#         "query": query,
#         "matched_entry": match,
#         "result": match.get("result", ""),
#     }


# if __name__ == "__main__":
#     try:
#         # Load environment variables from agents/.env
#         load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

#         # Prompt user for a natural language query in terminal
#         print("Enter your query: ", end="", flush=True)
#         user_query = sys.stdin.readline().strip()
#         if not user_query:
#             print("No query provided.")
#             sys.exit(1)

#         record = agent_answer_and_store(user_query)

#         # Print answer and the JSON-like structure
#         answer = record.get("result", "")
#         print("\nAnswer:\n" + (answer if isinstance(answer, str) else ""))

#         print("\nRecord to write to IPFS (JSON):")
#         print(json.dumps(record, ensure_ascii=False, indent=2))
#     except KeyboardInterrupt:
#         print("\nCancelled.")
#         sys.exit(130)