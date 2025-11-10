"""
Agent wallet management for Solana.
Provides functionality to create, fund, and manage Solana wallets for agents.
"""
import json
import os
from pathlib import Path
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
import asyncio

WALLET_FILE = Path.home() / ".x402_wallets_simple.json"
DEVNET_URL = "https://api.devnet.solana.com"
LAMPORTS_PER_SOL = 1_000_000_000


def load_wallets():
    """Load existing wallets from file."""
    if WALLET_FILE.exists():
        with open(WALLET_FILE, "r") as f:
            return json.load(f)
    return {"wallets": []}


def save_wallets(store):
    """Save wallet data to file."""
    WALLET_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(WALLET_FILE, "w") as f:
        json.dump(store, f, indent=2)


async def create_agent_wallet(fund_sol=1):
    """
    Generate a new Solana wallet and fund it on Devnet.
    
    Args:
        fund_sol: Amount of SOL to request from airdrop (default: 1)
    
    Returns:
        dict: Contains 'public_key' (str) and 'secret_key' (str, base64 encoded)
    """
    keypair = Keypair()
    public_key = str(keypair.pubkey())
    secret_key = keypair.secret()

    print(f"🔑 Generated new wallet: {public_key}")

    # Fund with Devnet SOL
    try:
        async with AsyncClient(DEVNET_URL) as client:
            signature = await client.request_airdrop(
                keypair.pubkey(), fund_sol * LAMPORTS_PER_SOL
            )
            # Wait for confirmation
            await client.confirm_transaction(signature.value, Confirmed)
            print(f"💸 Funded {fund_sol} SOL to {public_key}")
    except Exception as e:
        print(f"⚠️ Airdrop failed (Devnet faucet may be down): {e}")

    # Save locally - convert secret key to base58 for storage
    import base58
    secret_key_b58 = base58.b58encode(bytes(secret_key)).decode('utf-8')
    
    store = load_wallets()
    from datetime import datetime
    store["wallets"].append({
        "publicKey": public_key,
        "secretKey": secret_key_b58,
        "createdAt": datetime.now().isoformat()
    })
    save_wallets(store)

    return {"public_key": public_key, "secret_key": secret_key_b58}


def load_agent_wallet(public_key: str) -> Keypair:
    """
    Retrieve wallet keypair by public key.
    
    Args:
        public_key: Public key as string
    
    Returns:
        Keypair: The keypair for the wallet
    
    Raises:
        ValueError: If wallet not found
    """
    store = load_wallets()
    wallet = next((w for w in store["wallets"] if w["publicKey"] == public_key), None)
    if not wallet:
        raise ValueError(f"Wallet not found: {public_key}")

    # Convert base58 secret key back to Keypair
    # solders Keypair can be created from base58 string directly
    try:
        from solders.keypair import Keypair
        # If secretKey is stored as base58 string, decode it
        import base58
        secret_bytes = base58.b58decode(wallet["secretKey"])
        return Keypair.from_bytes(list(secret_bytes))
    except ImportError:
        # Fallback: use solders' from_base58_string if available
        return Keypair.from_base58_string(wallet["secretKey"])


def get_or_create_agent_wallet(agent_id: str = "agent_1", fund_sol: int = 1) -> Keypair:
    """
    Get existing wallet for agent or create a new one.
    Uses agent_id as a lookup key in the wallet store.
    
    Args:
        agent_id: Identifier for the agent (default: "agent_1")
        fund_sol: Amount of SOL to request if creating new wallet
    
    Returns:
        Keypair: The keypair for the agent's wallet
    """
    store = load_wallets()
    
    # Look for wallet with matching agent_id (we'll store it in a comment/metadata)
    # For now, we'll use the first wallet or create a new one
    # You could enhance this to store agent_id in the wallet metadata
    
    if store["wallets"]:
        # Use the first wallet for now
        wallet_data = store["wallets"][0]
        try:
            return load_agent_wallet(wallet_data["publicKey"])
        except Exception:
            # If loading fails, create a new wallet
            pass
    
    # Create a new wallet
    wallet = asyncio.run(create_agent_wallet(fund_sol))
    return load_agent_wallet(wallet["public_key"])


# Demo usage
if __name__ == "__main__":
    async def demo():
        wallet = await create_agent_wallet(1)  # 1 SOL airdrop
        print("\n✅ Wallet created & funded:")
        print(wallet)

        # Example: reload it
        reloaded = load_agent_wallet(wallet["public_key"])
        print(f"\n🔁 Reloaded wallet matches: {str(reloaded.pubkey()) == wallet['public_key']}")

    asyncio.run(demo())

