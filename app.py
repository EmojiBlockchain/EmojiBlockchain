import os
import json
import time
import hashlib
import secrets
from flask import Flask, render_template, request, jsonify

# ✅ Shared Data Directory (Ensures all files are stored in the same place)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")  # ✅ Store blockchain & wallets here
BLOCKCHAIN_FILE = os.path.join(DATA_DIR, "blockchain.json")
WALLETS_FILE = os.path.join(DATA_DIR, "genesis.json")

# ✅ Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/")
def home():
    return render_template("index.html")

# ✅ Load wallets
def load_wallets():
    if os.path.exists(WALLETS_FILE):
        with open(WALLETS_FILE, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {}
    return {}

# ✅ Save wallets
def save_wallets(wallets):
    with open(WALLETS_FILE, "w") as file:
        json.dump(wallets, file, indent=4)

# ✅ Load blockchain
def load_blockchain():
    if os.path.exists(BLOCKCHAIN_FILE):
        with open(BLOCKCHAIN_FILE, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []
    return []

# ✅ Save blockchain
def save_blockchain(blockchain):
    with open(BLOCKCHAIN_FILE, "w") as file:
        json.dump(blockchain, file, indent=4)

# ✅ Find Last Block
def get_last_block():
    blockchain = load_blockchain()
    return blockchain[-1] if blockchain else None


def get_last_block():
    blockchain = load_blockchain()
    
    # ✅ Ignore loose transactions and return the last valid block
    for block in reversed(blockchain):
        if "index" in block and "hash" in block:
            return block  # ✅ Return the last valid block

    return None  # No valid blocks found

# ✅ Create Wallet Endpoint
@app.route("/create_wallet", methods=["POST"])
def create_wallet():
    data = request.json
    username = data.get("username")

    if not username:
        return jsonify({"error": "Username is required"}), 400

    wallets = load_wallets()

    if username in wallets:
        return jsonify({"error": "Username already exists"}), 400

    private_key = secrets.token_hex(32)
    public_key = secrets.token_hex(66)
    address = secrets.token_hex(32)

    wallets[username] = {
        "private_key": private_key,
        "public_key": public_key,
        "address": address,
        "balance": "0🔥",  # ✅ New users get starting balance
        "stake": 0
    }

    save_wallets(wallets)

    return jsonify({
        "message": "Wallet created successfully!",
        "username": username,
        "public_key": public_key,
        "private_key": private_key
    })

# ✅ Check Wallet Balance Endpoint
@app.route("/check_balance", methods=["POST"])
def check_balance():
    data = request.json
    username = data.get("username")

    wallets = load_wallets()

    if username not in wallets:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"balance": wallets[username]["balance"]})

import random

# ✅ Send Transaction Endpoint (Includes a transaction fee)
@app.route("/send_transaction", methods=["POST"])
def send_transaction():
    data = request.json
    sender = data.get("sender")
    private_key = data.get("private_key")
    receiver = data.get("receiver")
    amount = float(data.get("amount"))

    wallets = load_wallets()
    blockchain = load_blockchain()

    if sender not in wallets or receiver not in wallets:
        return jsonify({"error": "Sender or receiver does not exist"}), 400

    if wallets[sender]["private_key"] != private_key:
        return jsonify({"error": "Invalid private key"}), 403

    # ✅ Calculate 1% transaction fee
    fee = amount * 0.01
    net_amount = amount - fee  

    if float(wallets[sender]["balance"].replace("🔥", "")) < amount:
        return jsonify({"error": "Insufficient balance"}), 400

    # ✅ Deduct from sender
    wallets[sender]["balance"] = str(float(wallets[sender]["balance"].replace("🔥", "")) - amount) + "🔥"

    # ✅ Add to receiver
    wallets[receiver]["balance"] = str(float(wallets[receiver]["balance"].replace("🔥", "")) + net_amount) + "🔥"

    # ✅ Select a validator to receive the 1% fee
    eligible_validators = [user for user, data in wallets.items() if data.get("stake", 0) > 0]

    if eligible_validators:
        validator = random.choice(eligible_validators)  # ✅ Fair random selection
        wallets[validator]["balance"] = str(float(wallets[validator]["balance"].replace("🔥", "")) + fee) + "🔥"
    else:
        validator = "No validator selected (no staked users)"

    # ✅ Generate transaction hash
    tx_hash = hashlib.sha256(f"{sender}{receiver}{amount}{time.time()}".encode()).hexdigest()

    # ✅ Create transaction
    new_transaction = {
        "tx_hash": tx_hash,
        "sender": sender,
        "receiver": receiver,
        "amount": amount,
        "fee": fee,
        "validator": validator,
        "timestamp": time.time()
    }

    # ✅ Get last valid block
    last_block = get_last_block()

    # ✅ If no blocks exist, create a Genesis Block
    if last_block is None:
        genesis_block = {
            "index": 1,
            "timestamp": time.time(),
            "transactions": [],
            "previous_hash": "0",
            "hash": hashlib.sha256(f"Genesis{time.time()}".encode()).hexdigest()
        }
        blockchain.append(genesis_block)
        last_block = genesis_block  # Now last_block is the Genesis Block

    # ✅ Generate the new block's hash correctly
    block_data = f"{last_block['hash']}{time.time()}".encode()
    new_block_hash = hashlib.sha256(block_data).hexdigest()

    # ✅ Create a new block with correct hash values
    new_block = {
        "index": last_block["index"] + 1,
        "timestamp": time.time(),
        "transactions": [new_transaction],  
        "previous_hash": last_block["hash"],  # ✅ Store previous block's hash
        "hash": new_block_hash  # ✅ Store current block's hash
    }

    # ✅ Append new block to blockchain
    blockchain.append(new_block)
    save_blockchain(blockchain)
    save_wallets(wallets)

    return jsonify({
        "message": "Transaction successful! Block added.",
        "tx_hash": tx_hash,
        "block_index": new_block["index"],
        "current_hash": new_block["hash"],
        "previous_hash": new_block["previous_hash"],
        "validator": validator  # ✅ Show who received the 1% fee
    })

# ✅ Find Username by Public Key
@app.route("/find_username", methods=["POST"])
def find_username():
    data = request.json
    public_key = data.get("public_key")
    
    if not public_key:
        return jsonify({"error": "Public key is required"}), 400
    
    wallets = load_wallets()
    for username, wallet in wallets.items():
        if wallet.get("public_key") == public_key:
            return jsonify({"username": username})
    
    return jsonify({"error": "Username not found"}), 404

# ✅ Recover Wallet with Private Key
@app.route("/recover_wallet", methods=["POST"])
def recover_wallet():
    data = request.json
    new_username = data.get("username")
    private_key = data.get("private_key")
    
    if not new_username or not private_key:
        return jsonify({"error": "Username and private key are required"}), 400
    
    wallets = load_wallets()
    
    for username, wallet in wallets.items():
        if wallet.get("private_key") == private_key:
            wallets[new_username] = wallet  # Assign the wallet to the new username
            del wallets[username]  # Remove the old entry
            save_wallets(wallets)
            return jsonify({"message": "Wallet recovered successfully", "username": new_username})
    
    return jsonify({"error": "Invalid private key"}), 404

# ✅ Stake EMOJI
@app.route("/stake", methods=["POST"])
def stake():
    data = request.json
    username, private_key, amount = data["username"], data["privateKey"], float(data["amount"])
    
    wallets = load_wallets()

    if username not in wallets:
        return jsonify({"message": "❌ User not found"}), 400
    if wallets[username]["private_key"] != private_key:
        return jsonify({"message": "❌ Invalid private key"}), 403
    if float(wallets[username]["balance"].replace("🔥", "")) < amount:
        return jsonify({"message": "❌ Insufficient balance"}), 400
    if amount < 1000:
        return jsonify({"message": "❌ Minimum stake is 1000🔥"}), 400

    wallets[username]["balance"] = str(float(wallets[username]["balance"].replace("🔥", "")) - amount) + "🔥"
    wallets[username]["stake"] += amount
    wallets[username]["stake_timestamp"] = time.time()  # ✅ Store stake timestamp
    save_wallets(wallets)

    return jsonify({"message": f"✅ {amount}🔥 staked successfully!"})

# ✅ Unstake EMOJI (7-day cooldown enforced)
@app.route("/unstake", methods=["POST"])
def unstake():
    data = request.json
    username, private_key, amount = data["username"], data["privateKey"], float(data["amount"])
    
    wallets = load_wallets()

    if username not in wallets:
        return jsonify({"message": "❌ User not found"}), 400
    if wallets[username]["private_key"] != private_key:
        return jsonify({"message": "❌ Invalid private key"}), 403
    if wallets[username]["stake"] < amount:
        return jsonify({"message": "❌ Insufficient staked balance"}), 400
    
    # ✅ Enforce 7-day lock on unstaking
    stake_time = wallets[username].get("stake_timestamp", 0)
    if time.time() - stake_time < 7 * 24 * 60 * 60:
        return jsonify({"message": "❌ You must stake for at least 7 days before unstaking."}), 400

    wallets[username]["stake"] -= amount
    wallets[username]["balance"] = str(float(wallets[username]["balance"].replace("🔥", "")) + amount) + "🔥"
    save_wallets(wallets)

    return jsonify({"message": f"✅ {amount}🔥 unstaked successfully!"})

# ✅ Check Stake Balance
@app.route("/stake_balance", methods=["GET"])
def stake_balance():
    username = request.args.get("username")

    wallets = load_wallets()
    stake_amount = wallets.get(username, {}).get("stake", 0)

    return jsonify({"stake": stake_amount})

if __name__ == "__main__":
    app.run(port=5001, debug=True)