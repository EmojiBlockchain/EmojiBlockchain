import json
import time
import random
import hashlib
import base64
from ecdsa import SigningKey, VerifyingKey, SECP256k1

BLOCKCHAIN_FILE = "blockchain.json"
WALLET_FILE = "genesis.json"

# 🔥 List of emojis for transactions
EMOJI_LIST = ["🔥", "🚀", "💎", "💰", "⚡", "🌟", "🎉", "🪙", "💡", "🔮"]
MAX_SUPPLY = 10_000_000_000  # 🔥 Max Token Supply: 10 Billion

# 🌟 Genesis Block
class Block:
    def __init__(self, index, transactions, previous_hash, validator, timestamp=None, hash=None):
        self.index = index
        self.transactions = transactions  # ✅ Keeps all transaction details, including fee
        self.previous_hash = previous_hash
        self.validator = validator
        self.timestamp = timestamp if timestamp else time.time()
        self.hash = hash if hash else self.calculate_hash()

    def calculate_hash(self):
        block_data = f"{self.index}{self.transactions}{self.previous_hash}{self.timestamp}".encode()
        return hashlib.sha256(block_data).hexdigest()

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "validator": self.validator,
            "hash": self.hash
        }

# 🔥 Blockchain Class with Multi-Block Support
class Blockchain:
    def __init__(self):
        self.chain = []
        self.load_blockchain()

    def create_genesis_block(self):
        """Creates the first block in the blockchain."""
        genesis_block = Block(0, [], "0", "Genesis")
        self.chain.append(genesis_block)
        self.save_blockchain()

    def add_block(self, transactions, validator):
        """Adds a new block with transactions and a validator."""
        previous_block = self.chain[-1]
        new_block = Block(
            index=len(self.chain),
            transactions=transactions,  # ✅ Ensures fee is included
            previous_hash=previous_block.hash,
            validator=validator
        )
        self.chain.append(new_block)
        self.save_blockchain()
        print(f"✅ New Block {new_block.index} Added! Transactions: {new_block.transactions}")

    def save_blockchain(self):
        """Saves blockchain data to a file."""
        blockchain_data = [block.to_dict() for block in self.chain]
        with open(BLOCKCHAIN_FILE, "w") as file:
            json.dump(blockchain_data, file, indent=4)

    def load_blockchain(self):
        """Loads blockchain from a file or creates a genesis block if missing."""
        try:
            with open(BLOCKCHAIN_FILE, "r") as file:
                blockchain_data = json.load(file)
                self.chain = [
                    Block(
                        index=block["index"],
                        transactions=block["transactions"],
                        previous_hash=block["previous_hash"],
                        validator=block["validator"],
                        timestamp=block.get("timestamp"),
                        hash=block.get("hash")
                    )
                    for block in blockchain_data
                ]
                print("✅ Blockchain loaded successfully!")
        except (FileNotFoundError, json.JSONDecodeError):
            print("⚠️ No blockchain found. Creating a new one...")
            self.create_genesis_block()

# 🔥 Load Wallets
def load_wallets():
    try:
        with open(WALLET_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# 🔥 Send Tokens & Add Transactions to Blocks
blockchain = Blockchain()

def send_transaction(sender, receiver, amount, private_key_hex):
    wallets = load_wallets()
    
    if sender not in wallets or receiver not in wallets:
        return "❌ Error: Sender or receiver does not exist."
    
    sender_balance = int(wallets[sender]["balance"].replace("🔥", ""))
    if sender_balance < amount:
        return "❌ Error: Insufficient balance."
    
    # Select random validator
    validator = random.choice(list(wallets.keys()))
    
    # ✅ Calculate transaction fee (1%)
    fee = max(1, amount * 1 // 100)  # 1% fee
    amount_after_fee = amount - fee

    # ✅ Deduct from sender (including fee)
    wallets[sender]["balance"] = f"{sender_balance - amount}🔥"

    receiver_balance = int(wallets[receiver]["balance"].replace("🔥", ""))
    wallets[receiver]["balance"] = f"{receiver_balance + amount_after_fee}🔥"

    validator_balance = int(wallets[validator]["balance"].replace("🔥", ""))
    wallets[validator]["balance"] = f"{validator_balance + fee}🔥"  # ✅ Validator gets fee

    # Save updated wallets
    save_wallets(wallets)

    # Create transaction and add to a new block
    transaction = {
        "from": sender,
        "to": receiver,
        "amount": f"{amount_after_fee}🔥",
        "fee": f"{fee}🔥",  # ✅ Fee is now stored in blockchain
        "validator": validator,
        "timestamp": time.time()
    }

    blockchain.add_block([transaction], validator)

    return f"✅ {sender} sent {amount_after_fee}🔥 to {receiver}. 💰 {fee}🔥 reward to {validator}. Transaction added in Block {len(blockchain.chain) - 1}"
