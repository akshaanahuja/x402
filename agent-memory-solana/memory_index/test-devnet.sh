#!/bin/bash

# Run tests against Solana devnet
# This ensures the program is properly deployed and functional on a real network

set -e

echo "🧪 Running tests against devnet..."

# Run tests with devnet provider
anchor test --provider.cluster devnet

echo "✅ Tests complete!"

