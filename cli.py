import sys
import json
import argparse

# Load balance from genesis.json based on username
def get_balance(username):
    # Correct path to the genesis.json file
    genesis_file = "C:/Users/kishan/OneDrive/Documents/EmojiBlockchain/data/genesis.json"
    
    try:
        with open(genesis_file, "r") as f:
            data = json.load(f)
            balances = data.get("balances", {})
            
            # Debug print to check if username exists in the loaded balances
            print(f"Loaded balances: {balances}")
            
            if username in balances:
                balance_str = balances[username]
                
                # Debug print to check the balance string before processing
                print(f"Balance for {username}: {balance_str}")
                
                # Manually strip out any non-numeric characters, specifically the emoji code
                numeric_balance = ''.join(c for c in balance_str if c.isdigit())
                
                # If the numeric balance is found
                if numeric_balance:
                    print(f"💰 Balance for {username}: {numeric_balance}")
                else:
                    print(f"❌ Error: Invalid balance format for {username}")
            else:
                print(f"❌ Error: No balance found for {username}")

    except FileNotFoundError:
        print(f"❌ Error: {genesis_file} not found!")
    except json.JSONDecodeError:
        print(f"❌ Error: Invalid JSON format in {genesis_file}")

def main():
    parser = argparse.ArgumentParser(description="CLI for Blockchain operations")
    parser.add_argument("command", choices=["get_balance"], help="Command to execute")
    parser.add_argument("--username", type=str, help="Username to check balance for", required=True)
    
    args = parser.parse_args()

    if args.command == "get_balance" and args.username:
        get_balance(args.username)

if __name__ == "__main__":
    main()
