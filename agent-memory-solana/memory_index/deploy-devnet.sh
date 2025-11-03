#!/bin/bash

# Deploy Memory Index program to Solana devnet
# This script builds and deploys the Anchor program to devnet

set -e

echo "🚀 Deploying Memory Index to Solana devnet..."

# Build the program
echo "📦 Building program..."
anchor build

# Get the program ID
PROGRAM_ID=$(solana address -k target/deploy/memory_index-keypair.json)
echo "📍 Program ID: $PROGRAM_ID"

# Deploy to devnet
echo "🌐 Deploying to devnet..."
anchor deploy --provider.cluster devnet

echo "✅ Deployment complete!"
echo ""
echo "Program deployed at: $PROGRAM_ID"
echo "View on Explorer: https://explorer.solana.com/address/$PROGRAM_ID?cluster=devnet"
echo ""
echo "To run tests against devnet:"
echo "  anchor test --provider.cluster devnet"

