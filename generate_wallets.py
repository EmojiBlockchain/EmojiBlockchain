import json
import os
from ecdsa import SigningKey, SECP256k1
import hashlib

# Define categories & initial allocations
CATEGORIES = {
    "@Presale": 3000000000,
    "@Liquidity1": 2000000000,
    "@Liquidity2": 2000000000,
    "@Ecosystem": 1000000000,
    "@Team": 800000000,
    "@Marketing": 700000000,
    "@Airdrops": 500000000
}

GENESIS_FILE = "genesis.json"

def generate_wallet():
    """Generate a new wallet address with private/public keys."""
    private_key = SigningKey.generate(curve=SECP256k1)
    public_key = private_key.verifying_key.to_string().hex()
    address = hashlib.sha256(public_key.encode()).hexdigest()
    
    return {
        "private_key": private_key.to_string().hex(),
        "public_key": public_key,
        "address": address,
        "balance": "0🔥",  # Default balance
        "stake": 0  # Default stake
    }

def create_genesis_wallets():
    """Create wallets for each allocation category."""
    wallets = {}
    
    for category, amount in CATEGORIES.items():
        wallet = generate_wallet()
        wallet["balance"] = f"{amount}🔥"  # Assign initial allocation
        wallets[category] = wallet
    
    # Save to file
    with open(GENESIS_FILE, "w") as f:
        json.dump(wallets, f, indent=4)
    
    print(f"✅ Genesis wallets saved to {GENESIS_FILE}")

# Run the script
if __name__ == "__main__":
    create_genesis_wallets()
