// agent_wallets.js
const fs = require("fs");
const path = require("path");
const os = require("os");
const solanaWeb3 = require("@solana/web3.js");

const WALLET_FILE = path.join(os.homedir(), ".x402_wallets_simple.json");
const connection = new solanaWeb3.Connection(solanaWeb3.clusterApiUrl("devnet"), "confirmed");

// Load existing wallets or create a new store
function loadWallets() {
    if (fs.existsSync(WALLET_FILE)) {
        return JSON.parse(fs.readFileSync(WALLET_FILE, "utf8"));
    }
    return { wallets: [] };
}

// Save wallet data
function saveWallets(store) {
    fs.writeFileSync(WALLET_FILE, JSON.stringify(store, null, 2));
}

// Generate a new Solana wallet and fund it on Devnet
async function createAgentWallet(fundSol = 1) {
    const keypair = solanaWeb3.Keypair.generate();
    const publicKey = keypair.publicKey.toBase58();
    const secretKey = Buffer.from(keypair.secretKey).toString("base64");

    console.log(`🔑 Generated new wallet: ${publicKey}`);

    // Fund with Devnet SOL
    try {
        const airdropSig = await connection.requestAirdrop(keypair.publicKey, fundSol * solanaWeb3.LAMPORTS_PER_SOL);
        await connection.confirmTransaction(airdropSig, "confirmed");
        console.log(`💸 Funded ${fundSol} SOL to ${publicKey}`);
    } catch (e) {
        console.warn("⚠️ Airdrop failed (Devnet faucet may be down):", e.message);
    }

    // Save locally
    const store = loadWallets();
    store.wallets.push({ publicKey, secretKey, createdAt: new Date().toISOString() });
    saveWallets(store);

    return { publicKey, secretKey };
}

// Retrieve wallet keypair by public key
function loadAgentWallet(publicKey) {
    const store = loadWallets();
    const wallet = store.wallets.find((w) => w.publicKey === publicKey);
    if (!wallet) throw new Error("Wallet not found.");

    const secretKey = Buffer.from(wallet.secretKey, "base64");
    return solanaWeb3.Keypair.fromSecretKey(new Uint8Array(secretKey));
}

// Demo usage
async function demo() {
    const wallet = await createAgentWallet(1); // 1 SOL airdrop
    console.log("\n✅ Wallet created & funded:");
    console.log(wallet);

    // Example: reload it and sign
    const reloaded = loadAgentWallet(wallet.publicKey);
    console.log(`\n🔁 Reloaded wallet matches: ${reloaded.publicKey.toBase58() === wallet.publicKey}`);
}

if (require.main === module) {
    demo();
}

module.exports = { createAgentWallet, loadAgentWallet };
