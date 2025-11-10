"""
Python client for the Solana Memory Index program.
Provides functionality to store and query memories on Solana.
"""
import json
from pathlib import Path
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from anchorpy import Program, Provider, Wallet, Idl
from anchorpy.coder.accounts import ACCOUNT_DISCRIMINATOR_SIZE
import asyncio

# Program ID for the Memory Index program
PROGRAM_ID = Pubkey.from_string("6dLHMacUJMThKeCwCzZRTLy9qfA1fwzoPXSYNy4CHEAE")
DEVNET_URL = "https://api.devnet.solana.com"


class MemoryIndexClient:
    """Client for interacting with the Solana Memory Index program."""
    
    def __init__(self, keypair: Keypair, cluster_url: str = DEVNET_URL):
        """
        Initialize the Memory Index client.
        
        Args:
            keypair: Solana keypair for signing transactions
            cluster_url: Solana cluster URL (default: devnet)
        """
        self.keypair = keypair
        self.cluster_url = cluster_url
        self._client = None
        self._provider = None
        self._program = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        # Find IDL file - the client is in agent-memory-solana/ directory
        # IDL is at agent-memory-solana/memory_index/target/idl/memory_index.json
        idl_path = Path(__file__).parent / "memory_index" / "target" / "idl" / "memory_index.json"
        if not idl_path.exists():
            # Try alternative path (if running from project root)
            alt_path = Path(__file__).parent.parent / "agent-memory-solana" / "memory_index" / "target" / "idl" / "memory_index.json"
            if alt_path.exists():
                idl_path = alt_path
            else:
                raise FileNotFoundError(
                    f"IDL file not found at {idl_path} or {alt_path}. "
                    "Please build the Anchor program first with 'anchor build' from the memory_index directory"
                )
        
        # Load IDL
        with open(idl_path) as f:
            idl_json = json.load(f)
        idl = Idl.from_json(json.dumps(idl_json))
        
        # Create client and provider
        self._client = AsyncClient(self.cluster_url)
        wallet = Wallet(self.keypair)
        self._provider = Provider(self._client, wallet)
        
        # Create program
        self._program = Program(idl, PROGRAM_ID, self._provider)
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.close()
    
    async def store_memory(self, cid: str, tags: list[str]) -> str:
        """
        Store a memory on Solana.
        
        Args:
            cid: IPFS Content ID (max 100 characters)
            tags: List of tags (max 20 tags, each max 50 characters)
        
        Returns:
            str: Transaction signature
        
        Raises:
            ValueError: If CID or tags are invalid
            Exception: If transaction fails
        """
        if len(cid) > 100:
            raise ValueError("CID is too long, maximum 100 characters")
        if len(tags) > 20:
            raise ValueError("Too many tags, maximum 20 tags")
        for tag in tags:
            if len(tag) > 50:
                raise ValueError(f"Tag '{tag}' is too long, maximum 50 characters")
        
        # Derive PDA for the memory account
        # Seeds: [b"memory", authority.key().as_ref(), cid.as_bytes()]
        authority_pubkey = self.keypair.pubkey()
        seeds = [
            b"memory",
            bytes(authority_pubkey),
            cid.encode('utf-8')
        ]
        memory_pda, _bump = Pubkey.find_program_address(seeds, PROGRAM_ID)
        
        try:
            # Use anchorpy's method builder pattern
            # The IDL has PDA seeds defined, so anchorpy should handle derivation
            # But we need to provide the accounts manually since PDA depends on instruction args
            method = self._program.methods.store_memory(cid, tags)
            
            # Set accounts with the derived PDA
            tx = await method.accounts(
                memory=memory_pda,
                authority=authority_pubkey,
                system_program=Pubkey.from_string("11111111111111111111111111111111"),
            ).rpc()
            
            print(f"✅ Memory stored on Solana. Transaction: {tx}")
            return str(tx)
        except Exception as e:
            print(f"❌ Error storing memory: {e}")
            raise
    
    async def get_memory_by_cid(self, cid: str) -> dict:
        """
        Get a memory by CID for the current authority.
        
        Args:
            cid: IPFS Content ID
        
        Returns:
            dict: Memory account data or None if not found
        """
        authority_pubkey = self.keypair.pubkey()
        seeds = [
            b"memory",
            bytes(authority_pubkey),
            cid.encode('utf-8')
        ]
        memory_pda, _ = Pubkey.find_program_address(seeds, PROGRAM_ID)
        
        try:
            account = await self._program.account["MemoryIndex"].fetch(memory_pda)
            return {
                "cid": account.cid,
                "tags": list(account.tags),
                "timestamp": account.timestamp,
                "authority": str(account.authority),
            }
        except Exception:
            return None


async def store_memory_async(keypair: Keypair, cid: str, tags: list[str], cluster_url: str = DEVNET_URL) -> str:
    """
    Async function for storing a memory.
    
    Args:
        keypair: Solana keypair for signing
        cid: IPFS Content ID
        tags: List of tags
        cluster_url: Solana cluster URL
    
    Returns:
        str: Transaction signature
    """
    async with MemoryIndexClient(keypair, cluster_url) as client:
        return await client.store_memory(cid, tags)


def store_memory(keypair: Keypair, cid: str, tags: list[str], cluster_url: str = DEVNET_URL) -> str:
    """
    Synchronous wrapper for storing a memory.
    
    Args:
        keypair: Solana keypair for signing
        cid: IPFS Content ID
        tags: List of tags
        cluster_url: Solana cluster URL
    
    Returns:
        str: Transaction signature
    """
    return asyncio.run(store_memory_async(keypair, cid, tags, cluster_url))


# For easier import and usage
def create_client(keypair: Keypair, cluster_url: str = DEVNET_URL) -> MemoryIndexClient:
    """Create a MemoryIndexClient instance."""
    return MemoryIndexClient(keypair, cluster_url)

