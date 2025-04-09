import hashlib
from ecdsa import SigningKey, SECP256k1
import json
import os
import random

GENESIS_FILE = "genesis.json"

def create_wallet():
    """Generate a new wallet with public/private keys."""
    private_key = SigningKey.generate(curve=SECP256k1)
    public_key = private_key.verifying_key.to_string().hex()
    address = hashlib.sha256(public_key.encode()).hexdigest()

    return {
        "private_key": private_key.to_string().hex(),
        "public_key": public_key,
        "address": address,
        "balance": "0🔥",
        "stake": 0
    }

# Load wallets from genesis.json and ensure required fields exist
def load_wallets():
    if not os.path.exists(GENESIS_FILE) or os.stat(GENESIS_FILE).st_size == 0:
        return {}
    try:
        with open(GENESIS_FILE, "r") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                return {}
            
            updated = False
            for user in data:
                if "stake" not in data[user]:
                    data[user]["stake"] = 0  # Ensure 'stake' field exists
                    updated = True
                if "public_key" not in data[user]:
                    data[user]["public_key"] = ""  # Ensure public key exists
                    updated = True
                if "balance" not in data[user]:
                    data[user]["balance"] = "0🔥"  # Ensure balance exists
                    updated = True
            
            if updated:
                with open(GENESIS_FILE, "w") as f:
                    json.dump(data, f, indent=4)
            
            return data
    except json.JSONDecodeError:
        return {}

def save_wallets(wallets):
    with open(GENESIS_FILE, "w") as f:
        json.dump(wallets, f, indent=4)

def stake_tokens(username, amount):
    wallets = load_wallets()
    if username not in wallets:
        return "Error: Wallet not found."
    
    balance = int(''.join(filter(str.isdigit, str(wallets[username]["balance"]))))
    if balance < amount:
        return "Error: Insufficient balance to stake."
    
    wallets[username]["balance"] = f"{balance - amount}🔥"
    wallets[username]["stake"] += amount
    
    save_wallets(wallets)
    return f"✅ {username} staked {amount}🔥 successfully!"

def check_stake(username):
    wallets = load_wallets()
    if username not in wallets:
        return "Error: Wallet not found."
    return f"{username} has staked {wallets[username]['stake']}🔥"

def select_validator():
    wallets = load_wallets()
    stakers = {user: data["stake"] for user, data in wallets.items() if data["stake"] > 0}
    
    if not stakers:
        return f"🎉 No stakes found, randomly selecting: {random.choice(list(wallets.keys()))}"
    
    highest_staker = max(stakers, key=stakers.get)
    return f"🎉 Selected Validator: {highest_staker}"
