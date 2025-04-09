import json
import time
import random
import re
from ecdsa import SigningKey, VerifyingKey, SECP256k1
import hashlib
from wallet import load_wallets, save_wallets, select_validator
from blockchain import Blockchain

EMOJI_LIST = ["🔥", "🚀", "💎", "💰", "⚡", "🌟", "🎉", "🪙", "💡", "🔮"]
MAX_SUPPLY = 10_000_000_000  # 10 Billion Emoji max supply
TRANSACTION_FEE_PERCENT = 1  # 1% Fee goes to validator

blockchain = Blockchain()

def extract_numeric_balance(balance):
    return int(re.sub(r"[^0-9]", "", str(balance)))  # ✅ Convert balance to number

def get_random_emoji():
    return random.choice(EMOJI_LIST)

def sign_transaction(private_key_hex, sender, receiver, amount):
    sk = SigningKey.from_string(bytes.fromhex(private_key_hex), curve=SECP256k1)
    transaction_data = f"{sender}{receiver}{amount}".encode()
    signature = sk.sign(transaction_data).hex()
    return signature

def verify_signature(public_key_hex, sender, receiver, amount, signature_hex):
    try:
        vk = VerifyingKey.from_string(bytes.fromhex(public_key_hex), curve=SECP256k1)
        transaction_data = f"{sender}{receiver}{amount}".encode()
        signature = bytes.fromhex(signature_hex)
        return vk.verify(signature, transaction_data)
    except:
        return False  # Signature verification failed

def send_transaction(sender, receiver, amount, private_key_hex):
    wallets = load_wallets()
    
    if sender not in wallets or receiver not in wallets:
        return "❌ Error: Sender or receiver does not exist."

    sender_public_key = wallets[sender]["public_key"]
    signature = sign_transaction(private_key_hex, sender, receiver, amount)
    
    if not verify_signature(sender_public_key, sender, receiver, amount, signature):
        return "❌ Error: Signature verification failed!"

    sender_balance = extract_numeric_balance(wallets[sender]["balance"])
    if sender_balance < amount:
        return "❌ Error: Insufficient balance."
    
    validator = select_validator().replace("🎉 Selected Validator: ", "")
    if validator not in wallets:
        return f"❌ ERROR: Validator {validator} not found in wallets!"
    
    # ✅ Calculate transaction fee (1%)
    fee = max(1, amount * TRANSACTION_FEE_PERCENT // 100)
    amount_after_fee = amount - fee

    # ✅ Ensure max supply is not exceeded
    total_supply = sum(extract_numeric_balance(wallet["balance"]) for wallet in wallets.values())
    if total_supply + fee > MAX_SUPPLY:
        print("❌ Warning: Max supply reached! Adjusting fee to fit within limit.")
        fee = max(0, MAX_SUPPLY - total_supply)  # Reduce fee if needed
        amount_after_fee = amount - fee  # Adjust transaction amount

    if amount <= fee:
        return f"❌ Transaction failed! You must send more than the {fee}🔥 fee."
    
    print(f"DEBUG: Sender {sender} Balance Before: {wallets[sender]['balance']}🔥")
    wallets[sender]["balance"] = f"{sender_balance - amount - fee}🔥"  # ✅ Deduct fee from sender!
    print(f"DEBUG: Sender {sender} Balance After Deduction: {wallets[sender]['balance']}🔥")

    receiver_balance = extract_numeric_balance(wallets[receiver]["balance"])
    wallets[receiver]["balance"] = f"{receiver_balance + amount_after_fee}🔥"
    
    validator_balance = extract_numeric_balance(wallets[validator]["balance"])
    print(f"DEBUG: Validator {validator} Balance Before: {wallets[validator]['balance']}🔥")
    wallets[validator]["balance"] = f"{validator_balance + fee}🔥"  # ✅ Validator receives fee
    print(f"DEBUG: Validator {validator} Balance After Receiving Fee: {wallets[validator]['balance']}🔥")
  
    save_wallets(wallets)
    
    transaction = {
        "from": sender,
        "to": receiver,
        "amount": f"{amount_after_fee}🔥",
        "fee": f"{fee}🔥",  # ✅ Fee is now stored in blockchain
        "validator": validator,
        "timestamp": time.time()
    }
    total_supply = sum(extract_numeric_balance(wallet["balance"]) for wallet in wallets.values())
    print(f"DEBUG: Current Total Supply = {total_supply}🔥 / Max Supply = {MAX_SUPPLY}🔥")
    
    print(f"DEBUG: Transaction to store in block: {transaction}")
    
    blockchain.add_block([transaction], validator)
    
    return f"✅ {sender} sent {amount_after_fee}🔥 to {receiver}. 💰 {fee}🔥 reward to {validator}. Transaction added in Block {len(blockchain.chain) - 1}"
