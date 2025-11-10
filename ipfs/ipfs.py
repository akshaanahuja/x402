import ipfsApi, json, requests

api = ipfsApi.Client('127.0.0.1', 5001)

def post_query(query: str, result: dict, tags: list[str], agent_id: str) -> str:
    data = {"query": query, "result": result, "agent_id": agent_id, "tags": tags}
    cid = api.add_json(json.dumps(data))
    print(f"✅ Uploaded to IPFS: CID = {cid}")
    return cid

def fetch_query(cid: str) -> dict:
    """
    Fetch using a public HTTP gateway (works with all modern IPFS nodes). 
    """
    gateway_url = f"https://ipfs.io/ipfs/{cid}"
    res = requests.get(gateway_url)
    res.raise_for_status()
    data = res.json()
    print("📦 Retrieved from gateway:")
    print(json.dumps(data, indent=2))
    return data


# Example usage
if __name__ == "__main__":
    query = "Get the latest Solana validator count"
    result = {"validators": 2374, "timestamp": "2025-11-03T23:00:00Z"}
    agent_id = "agent_1"
    tags = ["solana", "validators", "count"]

    cid = post_query(query, result, tags, agent_id)
    fetched = fetch_query(cid)
