from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import json
import os
import time
import eventlet
eventlet.monkey_patch()
# ✅ Use a shared directory for blockchain storage
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")  # ✅ Shared blockchain folder
BLOCKCHAIN_FILE = os.path.join(DATA_DIR, "blockchain.json")

BLOCKS_PER_PAGE = 5  # Number of blocks per page

app = Flask(__name__, template_folder="templates", static_folder="static")
socketio = SocketIO(app, cors_allowed_origins="*")

# ✅ Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# ✅ Load Blockchain Data
def load_blockchain():
    if os.path.exists(BLOCKCHAIN_FILE):
        with open(BLOCKCHAIN_FILE, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []
    return []

# ✅ Paginate Blockchain Data
def paginate_blocks(page=1):
    blockchain = load_blockchain()
    total_pages = max(1, (len(blockchain) + BLOCKS_PER_PAGE - 1) // BLOCKS_PER_PAGE)
    start = (page - 1) * BLOCKS_PER_PAGE
    end = start + BLOCKS_PER_PAGE

    paginated_blocks = []
    for block in blockchain[start:end]:
        # ✅ Extract validator from first transaction if available
        validator = block["transactions"][0].get("validator", "None") if block.get("transactions") else "None"
        block["validator"] = validator  # ✅ Ensure validator is available in block data
        paginated_blocks.append(block)

    return paginated_blocks, total_pages

@app.route("/")
def home():
    blockchain = load_blockchain()
    total_blocks = len(blockchain)
    last_page = max(1, (total_blocks + BLOCKS_PER_PAGE - 1) // BLOCKS_PER_PAGE)
    page = int(request.args.get("page", last_page))
    blocks, total_pages = paginate_blocks(page)
    return render_template("explorer.html", blockchain=blocks, page=page, total_pages=total_pages)

@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("q", "").strip().lower()  # ✅ Trim spaces, ensure lowercase
    blockchain = load_blockchain()
    results = []

    for block in blockchain:
        block_hash = block.get("hash", "N/A")
        block_index = str(block.get("index", "N/A"))
        validator = block.get("validator", "N/A")
        transactions = block.get("transactions", [])

        # ✅ Debugging: Print block details
        print(f"🔍 Checking Block {block_index}: Hash {block_hash}, Validator {validator}")
        print(f"📜 Transactions: {transactions}")

        # ✅ Ensure valid block hash and index before searching
        if block_hash != "N/A" and (query in block_hash.lower() or query == block_index):
            results.append({
                "block": block_index,
                "hash": block_hash,
                "validator": validator,
                "transactions": transactions
            })

        # ✅ Ensure transaction data exists and is a list
        if not isinstance(transactions, list):
            print(f"⚠️ Skipping Block {block_index} - Transactions not in list format")
            continue  # Skip if transactions are not properly formatted

        for tx in transactions:
            sender = tx.get("sender", "N/A")
            receiver = tx.get("receiver", "N/A")
            amount = tx.get("amount", "N/A")
            fee = tx.get("fee", "N/A")
            tx_hash = tx.get("tx_hash", "N/A")  # ✅ Ensure TX Hash is included

            # ✅ Debugging: Print transaction details
            print(f"💸 Tx: {tx_hash} | {sender} ➡️ {receiver} | Amount: {amount}🔥 | Fee: {fee}🔥")

            # ✅ Search by sender, receiver, amount, or transaction hash
            if query in sender.lower() or query in receiver.lower() or query in str(amount) or query in tx_hash.lower():
                results.append({
                    "sender": sender,
                    "receiver": receiver,
                    "amount": amount,
                    "fee": fee,
                    "block": block_index,
                    "hash": block_hash,
                    "validator": validator,
                    "tx_hash": tx_hash  # ✅ Now properly included
                })

    return jsonify(sorted(results, key=lambda x: x["block"], reverse=True))

# ✅ WebSocket Event to Broadcast New Blocks
def broadcast_new_block():
    while True:
        time.sleep(5)
        blockchain = load_blockchain()
        if blockchain:
            socketio.emit("new_block", blockchain[0])

if __name__ == "__main__":
    socketio.start_background_task(broadcast_new_block)
    socketio.run(app, host="0.0.0.0", port=5000)
