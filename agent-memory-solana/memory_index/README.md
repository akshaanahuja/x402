# Agent Memory Index - Solana Program

A decentralized memory storage system for AI agents, built on Solana. Agents can store query results off-chain on IPFS, while Solana acts as the index layer that lets other agents discover those memories.

## 🎯 Overview

This program provides a minimal Solana on-chain index for agent memories stored on IPFS. It supports:

- **Storing memories**: Link IPFS CIDs to query hashes and tags
- **Discovery**: Find memories by tags
- **Immutable records**: Timestamped entries that agents can trust

## 📋 Architecture

### Account Structure

```rust
pub struct MemoryIndex {
    pub query_hash: [u8; 32],      // Hash of the agent query
    pub cid: String,                // IPFS Content ID (max 100 chars)
    pub tags: Vec<String>,          // Tags for discovery (max 20)
    pub timestamp: i64,             // Unix timestamp
    pub authority: Pubkey,          // Who stored this memory
}
```

### Instructions

#### 1. `store_memory`

Stores a new memory entry on-chain:

- **Parameters**: `query_hash` (32 bytes), `cid` (String), `tags` (Vec<String>)
- **Accounts**: PDA derived from query_hash, authority (signer), system program
- **Validation**: CID ≤ 100 chars, tags ≤ 20, each tag ≤ 50 chars

#### 2. `get_memories_by_tag`

Queries memories by tag (currently a placeholder for client-side filtering):

- **Parameters**: `tag` (String)
- **Note**: Proper indexing requires additional infrastructure or CPI

## 🚀 Getting Started

### Prerequisites

1. **Install Solana CLI**:
   ```bash
   sh -c "$(curl -sSfL https://release.solana.com/v1.18.42/install)"
   ```

2. **Install Anchor**:
   ```bash
   cargo install --git https://github.com/coral-xyz/anchor avm --locked --force
   avm install latest
   avm use latest
   ```

3. **Install Node.js dependencies**:
   ```bash
   cd memory_index
   yarn install
   ```

### Build

```bash
anchor build
```

This generates the IDL, TypeScript types, and builds the program.

### Test Locally

```bash
anchor test
```

This will:
1. Start a local Solana validator
2. Deploy your program
3. Run all tests
4. Shutdown the validator

### Test on Devnet

1. **Configure your wallet**:
   ```bash
   solana config set --url devnet
   solana address  # Check your address
   ```

2. **Get devnet SOL** (if needed):
   ```bash
   solana airdrop 2 $(solana address)  # Request airdrop
   ```

3. **Build and deploy**:
   ```bash
   ./deploy-devnet.sh
   ```

4. **Run tests against devnet**:
   ```bash
   ./test-devnet.sh
   ```

## 🧪 Tests

The test suite includes:

- ✅ Storing memories with valid data
- ✅ Validation errors (CID too long, too many tags, tag too long)
- ✅ Multiple memory storage
- ✅ Authority tracking
- ✅ Timestamp verification

See `tests/memory_index.ts` for the full test suite.

## 📊 Program ID

```
6dLHMacUJMThKeCwCzZRTLy9qfA1fwzoPXSYNy4CHEAE
```

## 🔍 Usage Examples

### Store a Memory

```typescript
import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { MemoryIndex } from "../target/types/memory_index";
import { PublicKey } from "@solana/web3.js";

// Initialize
const provider = anchor.AnchorProvider.env();
const program = anchor.workspace.memoryIndex as Program<MemoryIndex>;

// Generate query hash (example)
const queryHash = crypto.randomBytes(32);

// Find PDA
const [memoryPda] = PublicKey.findProgramAddressSync(
  [Buffer.from("memory"), queryHash],
  program.programId
);

// Store memory
const tx = await program.methods
  .storeMemory(queryHash, "QmYjtig7VJQ6XsnUjqqJvj7QaMcCAwtrgNdahSiFofrE7o", ["python", "agent"])
  .accounts({
    memory: memoryPda,
    authority: provider.wallet.publicKey,
    systemProgram: anchor.web3.SystemProgram.programId,
  })
  .rpc();
```

### Fetch a Memory

```typescript
// Fetch by PDA
const memoryAccount = await program.account.memoryIndex.fetch(memoryPda);
console.log("CID:", memoryAccount.cid);
console.log("Tags:", memoryAccount.tags);
console.log("Stored by:", memoryAccount.authority.toBase58());
```

## 🔐 Security Considerations

- **Validation**: All inputs are validated (length limits enforced)
- **Authority**: Only the signer can store memories under their authority
- **PDA**: Account derivation prevents collisions
- **Immutable**: Once stored, memories cannot be modified (by design)

## 🚧 Limitations & Future Work

- `get_memories_by_tag` currently returns empty; needs proper indexing
- Consider adding:
  - Pagination for large tag queries
  - Cross-program invocations for complex queries
  - Memory ownership transfers
  - Expiry mechanisms
  - Gas optimization for batch operations

## 📦 Project Structure

```
memory_index/
├── programs/
│   └── memory_index/
│       └── src/
│           └── lib.rs           # Program logic
├── tests/
│   └── memory_index.ts          # Test suite
├── Anchor.toml                   # Anchor configuration
├── Cargo.toml                    # Rust workspace
├── package.json                  # Node dependencies
├── deploy-devnet.sh              # Deploy to devnet
└── test-devnet.sh                # Test on devnet
```

## 🤝 Contributing

This is part of the x402 ecosystem. Contributions welcome!

## 📄 License

Apache-2.0

