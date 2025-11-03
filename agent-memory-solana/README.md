# Agent Memory Solana Program

A Solana on-chain index for agent memories stored on IPFS. This is Phase 1 of building a decentralized memory system for AI agents.

## 🎯 Overview

This Solana program provides a minimal index layer that lets agents:
- **Store memories**: Link IPFS CIDs to query hashes and tags
- **Discover content**: Find memories by tags (planned for client-side filtering)
- **Trust the data**: Immutable, timestamped entries

The actual query results live on IPFS; Solana only stores the metadata and content IDs.

## 📁 Project Structure

```
agent-memory-solana/
└── memory_index/              # Anchor program
    ├── programs/
    │   └── memory_index/
    │       └── src/
    │           └── lib.rs      # Main program logic
    ├── tests/
    │   └── memory_index.ts     # TypeScript tests
    ├── Anchor.toml             # Anchor configuration
    ├── README.md               # Detailed documentation
    ├── deploy-devnet.sh        # Deploy to devnet script
    └── test-devnet.sh          # Test on devnet script
```

## 🚀 Quick Start

See [memory_index/README.md](./memory_index/README.md) for detailed setup and usage instructions.

### Quick Commands

```bash
cd memory_index

# Build the program
anchor build

# Run tests locally
anchor test

# Deploy to devnet (after configuration)
./deploy-devnet.sh

# Run tests on devnet
./test-devnet.sh
```

## 📊 Features

### Implemented
- ✅ `store_memory`: Store memory metadata on-chain
- ✅ Validation: CID length, tag count, tag length limits
- ✅ PDA-based account storage
- ✅ Timestamped entries
- ✅ Authority tracking

### Planned
- 🔄 `get_memories_by_tag`: Proper indexing implementation
- 🔄 Batch operations
- 🔄 Memory ownership transfers
- 🔄 Client-side filtering helpers

## 🔧 Architecture

### Account Schema
```rust
pub struct MemoryIndex {
    pub query_hash: [u8; 32],      // Hash of the agent query
    pub cid: String,                // IPFS Content ID
    pub tags: Vec<String>,          // Discovery tags
    pub timestamp: i64,             // Unix timestamp
    pub authority: Pubkey,          // Who stored this
}
```

### Program Flow
1. Agent generates a query hash from their prompt
2. Query result is stored on IPFS → gets CID
3. Agent calls `store_memory` with hash, CID, and tags
4. Other agents can discover the CID by tag or query hash

## 🧪 Testing

The test suite includes:
- ✅ Successful memory storage
- ✅ Validation error handling
- ✅ Multiple memory storage
- ✅ Authority verification
- ✅ Timestamp checking

Run tests with:
```bash
anchor test
```

## 📝 Usage Example

```typescript
// Store a memory
await program.methods
  .storeMemory(queryHash, cid, ["python", "agent"])
  .rpc();

// Fetch a memory
const memory = await program.account.memoryIndex.fetch(memoryPda);
console.log("CID:", memory.cid);
console.log("Tags:", memory.tags);
```

## 🔗 Related

This is part of the x402 ecosystem focused on agent-to-agent payments and services.

## 📄 License

Apache-2.0

