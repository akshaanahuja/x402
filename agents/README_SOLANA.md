# Solana Memory Index Integration

This document explains how to use the Solana memory index functionality in your agents.

## Overview

The agent can now store memories on both IPFS and Solana:
- **IPFS**: Stores the actual data (query + result)
- **Solana**: Stores an on-chain index (CID + tags) for discoverability

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Build the Solana Program

Before using the Solana functionality, you need to build the Anchor program:

```bash
cd ../agent-memory-solana/memory_index
anchor build
```

This generates the IDL file that the Python client needs.

### 3. Deploy to Devnet (Optional)

To test on Solana devnet:

```bash
cd ../agent-memory-solana/memory_index
./deploy-devnet.sh
```

## Usage

### Basic Usage

The agent now has two tools:

1. **`ipfs_post_query`**: Stores data on IPFS and returns a CID
2. **`solana_store_memory`**: Stores the CID and tags on Solana blockchain

### Example Workflow

1. Agent answers a query
2. User provides tags (comma-separated)
3. Agent stores data on IPFS → gets CID
4. Agent stores CID + tags on Solana → gets transaction signature

### Wallet Management

The agent automatically manages its Solana wallet:
- First run: Creates a new wallet and requests devnet SOL airdrop
- Subsequent runs: Uses the existing wallet
- Wallets are stored in `~/.x402_wallets_simple.json`

## Function Details

### `solana_store_memory(cid, tags_csv, agent_id)`

- **cid**: IPFS Content ID from `ipfs_post_query`
- **tags_csv**: Comma-separated tags (same as used for IPFS)
- **agent_id**: Agent identifier (default: "agent_1")

Returns: Solana transaction signature

## Program Details

- **Program ID**: `6dLHMacUJMThKeCwCzZRTLy9qfA1fwzoPXSYNy4CHEAE`
- **Network**: Solana Devnet (default)
- **PDA Seeds**: `["memory", authority, cid]`
- **Limits**:
  - CID: max 100 characters
  - Tags: max 20 tags
  - Tag length: max 50 characters per tag

## Troubleshooting

### IDL Not Found

If you see "IDL file not found":
1. Make sure you've run `anchor build` in the `memory_index` directory
2. Check that `memory_index/target/idl/memory_index.json` exists

### Airdrop Failed

If wallet funding fails:
- Devnet faucet may be rate-limited
- Try again later or manually fund the wallet
- Check wallet balance: `solana balance <wallet-address> --url devnet`

### Transaction Failed

Common issues:
- Insufficient SOL balance (need SOL for transaction fees)
- Program not deployed (if testing on devnet)
- Invalid CID or tags (check limits)

## Files

- `agent1.py`: Main agent with Solana integration
- `wallets/agent_wallet.py`: Wallet management
- `agent-memory-solana/memory_index_python_client.py`: Solana client
- `agent-memory-solana/memory_index/`: Anchor program

## Next Steps

- Query memories by tags
- Share memories between agents
- Build discovery mechanisms

