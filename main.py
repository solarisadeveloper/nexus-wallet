import requests
import json
import os
from web3 import Web3
from eth_account import Account

# Configuration
BTC_BASE_URL = "https://api.blockcypher.com/v1/btc/main"
LTC_BASE_URL = "https://api.blockcypher.com/v1/ltc/main"
ETH_BASE_URL = "https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID"  # Replace with your Infura ID

# Replace with your BlockCypher API token
BLOCKCYPHER_API_TOKEN = "2122e5d642cb4d919332c721469dbbfb"

# Function to get a consistent API token
def get_api_token(coin):
    if coin in ("btc", "ltc"):
        return BLOCKCYPHER_API_TOKEN
    else:
        return None  # No API token needed for Ethereum (Infura)

# Function to create a new wallet
def create_wallet(coin):
    if coin == "btc":
        url = f"{BTC_BASE_URL}/addrs?token={get_api_token(coin)}"
        response = requests.post(url)
        if response.status_code == 201:
            data = response.json()
            address = data.get("address", "")
            private_key = data.get("private", "")  # Get the private key
            save_phrase(coin, address, private_key)  # Save phrase to a file
            print(f"New {coin.upper()} wallet address: {address}")
            return address
        else:
            print(f"Failed to create {coin.upper()} wallet: {response.text}")
            return None
    elif coin == "ltc":
        url = f"{LTC_BASE_URL}/addrs?token={get_api_token(coin)}"
        response = requests.post(url)
        if response.status_code == 201:
            data = response.json()
            address = data.get("address", "")
            private_key = data.get("private", "")  # Get the private key
            save_phrase(coin, address, private_key)  # Save phrase to a file
            print(f"New {coin.upper()} wallet address: {address}")
            return address
        else:
            print(f"Failed to create {coin.upper()} wallet: {response.text}")
            return None
    elif coin == "eth":
        w3 = Web3(Web3.HTTPProvider(ETH_BASE_URL))
        account = w3.eth.account.create()
        address = account.address
        private_key = account.privateKey.hex()  # Get the private key
        save_phrase(coin, address, private_key)  # Save phrase to a file
        print(f"New {coin.upper()} wallet address: {address}")
        return address
    else:
        print(f"Unsupported coin: {coin}")
        return None

# Function to save phrase (address and private key) to a file
def save_phrase(coin, address, private_key):
    os.makedirs("phrases", exist_ok=True)  # Create phrases folder if it doesn't exist
    with open(f"phrases/{coin}.txt", "w") as f:
        f.write(f"Address: {address}\nPrivate Key: {private_key}")

# Function to get phrase (address and private key) from a file
def get_phrase(coin):
    try:
        with open(f"phrases/{coin}.txt", "r") as f:
            lines = f.readlines()
            address = lines[0].split(":")[1].strip()
            private_key = lines[1].split(":")[1].strip()
            return address, private_key
    except FileNotFoundError:
        print(f"No wallet found for {coin.upper()}. Create one first.")
        return None, None

# Function to fund a wallet
def fund_wallet(coin, address, amount):
    if coin == "btc":
        url = f"{BTC_BASE_URL}/addrs/{address}/payments?token={get_api_token(coin)}"
        payload = {
            "amount": int(amount * 1e8)  # Assuming amount is in BTC, convert to Satoshis
        }
        response = requests.post(url, json=payload)
        if response.status_code == 201:
            print(f"Wallet {address} funded successfully.")
            update_balance(coin, address)  # Update the balance file
            return True
        else:
            print(f"Failed to fund wallet: {response.text}")
            return False
    elif coin == "ltc":
        url = f"{LTC_BASE_URL}/addrs/{address}/payments?token={get_api_token(coin)}"
        payload = {
            "amount": int(amount * 1e8)  # Assuming amount is in LTC, convert to Litoshis
        }
        response = requests.post(url, json=payload)
        if response.status_code == 201:
            print(f"Wallet {address} funded successfully.")
            update_balance(coin, address)  # Update the balance file
            return True
        else:
            print(f"Failed to fund wallet: {response.text}")
            return False
    elif coin == "eth":
        print("Funding an Ethereum wallet requires a different process. Consider using an exchange.")
        return False
    else:
        print(f"Unsupported coin: {coin}")
        return None

# Function to fetch balance of a wallet
def get_wallet_balance(coin, address):
    if coin == "btc":
        url = f"{BTC_BASE_URL}/addrs/{address}/balance?token={get_api_token(coin)}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            balance = data.get("final_balance", 0)  # Balance in satoshis
            print(f"Wallet {address} Balance: {balance / 1e8} {coin.upper()}")
            update_balance(coin, address)  # Update the balance file
            return balance
        else:
            print(f"Failed to fetch balance for {address}")
            return 0
    elif coin == "ltc":
        url = f"{LTC_BASE_URL}/addrs/{address}/balance?token={get_api_token(coin)}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            balance = data.get("final_balance", 0)  # Balance in Litoshis
            print(f"Wallet {address} Balance: {balance / 1e8} {coin.upper()}")
            update_balance(coin, address)  # Update the balance file
            return balance
        else:
            print(f"Failed to fetch balance for {address}")
            return 0
    elif coin == "eth":
        w3 = Web3(Web3.HTTPProvider(ETH_BASE_URL))
        balance = w3.eth.get_balance(address)
        print(f"Wallet {address} Balance: {balance / 1e18} {coin.upper()}")  # Convert Wei to ETH
        update_balance(coin, address)  # Update the balance file
        return balance
    else:
        print(f"Unsupported coin: {coin}")
        return None

# Function to update balance in a file
def update_balance(coin, address):
    os.makedirs("balances", exist_ok=True)  # Create balances folder if it doesn't exist
    balance = get_wallet_balance(coin, address)  # Get the balance first
    with open(f"balances/{coin}.txt", "w") as f:  # Overwrite existing file
        f.write(f"Address: {address}\nBalance: {balance}")

# Function to send funds
def send_funds(coin, from_address, private_key, to_address, amount):
    if coin == "btc":
        # Step 1: Create a new transaction skeleton
        tx_skeleton_url = f"{BTC_BASE_URL}/txs/new?token={get_api_token(coin)}"
        tx_payload = {
            "inputs": [{"addresses": [from_address]}],
            "outputs": [{"addresses": [to_address], "value": int(amount * 1e8)}]
        }
        tx_response = requests.post(tx_skeleton_url, json=tx_payload)

        if tx_response.status_code != 201:
            print(f"Error creating transaction: {tx_response.text}")
            return

        tx_skeleton = tx_response.json()

        # Step 2: Sign the transaction (using the private key)
        tx_skeleton["tosign"] = [private_key]  # Simplified signing

        # Step 3: Send the transaction
        tx_send_url = f"{BTC_BASE_URL}/txs/send?token={get_api_token(coin)}"
        tx_send_response = requests.post(tx_send_url, json=tx_skeleton)

        if tx_send_response.status_code == 201:
            print("Transaction sent successfully!")
            txid = tx_send_response.json().get("txid")
            print(f"Transaction ID: {txid}")
            update_balance(coin, from_address)  # Update balance after sending
            return txid
        else:
            print(f"Error sending transaction: {tx_send_response.text}")
            return None
    elif coin == "ltc":
        # Step 1: Create a new transaction skeleton
        tx_skeleton_url = f"{LTC_BASE_URL}/txs/new?token={get_api_token(coin)}"
        tx_payload = {
            "inputs": [{"addresses": [from_address]}],
            "outputs": [{"addresses": [to_address], "value": int(amount * 1e8)}]
        }
        tx_response = requests.post(tx_skeleton_url, json=tx_payload)

        if tx_response.status_code != 201:
            print(f"Error creating transaction: {tx_response.text}")
            return

        tx_skeleton = tx_response.json()

        # Step 2: Sign the transaction (using the private key)
        tx_skeleton["tosign"] = [private_key]  # Simplified signing

        # Step 3: Send the transaction
        tx_send_url = f"{LTC_BASE_URL}/txs/send?token={get_api_token(coin)}"
        tx_send_response = requests.post(tx_send_url, json=tx_skeleton)

        if tx_send_response.status_code == 201:
            print("Transaction sent successfully!")
            txid = tx_send_response.json().get("txid")
            print(f"Transaction ID: {txid}")
            update_balance(coin, from_address)  # Update balance after sending
            return txid
        else:
            print(f"Error sending transaction: {tx_send_response.text}")
            return None
    elif coin == "eth":
        w3 = Web3(Web3.HTTPProvider(ETH_BASE_URL))
        nonce = w3.eth.get_transaction_count(from_address)
        transaction = {
            'nonce': nonce,
            'to': to_address,
            'value': w3.toWei(amount, 'ether'),
            'gas': 21000,  # Adjust if needed
            'gasPrice': w3.eth.gas_price,
        }
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Transaction sent successfully with hash: {tx_hash.hex()}")
        update_balance(coin, from_address)  # Update balance after sending
        return tx_hash.hex()
    else:
        print(f"Unsupported coin: {coin}")
        return None

# Function to view transaction details
def view_transaction_details(coin, txid):
    if coin == "btc":
        url = f"{BTC_BASE_URL}/txs/{txid}?token={get_api_token(coin)}"
        response = requests.get(url)
        if response.status_code == 200:
            print(response.json())
        else:
            print(f"Error fetching transaction details: {response.text}")
    elif coin == "ltc":
        url = f"{LTC_BASE_URL}/txs/{txid}?token={get_api_token(coin)}"
        response = requests.get(url)
        if response.status_code == 200:
            print(response.json())
        else:
            print(f"Error fetching transaction details: {response.text}")
    elif coin == "eth":
        w3 = Web3(Web3.HTTPProvider(ETH_BASE_URL))
        try:
            transaction = w3.eth.get_transaction(txid)
            print(transaction)
        except Exception as e:
            print(f"Error fetching transaction details: {e}")
    else:
        print(f"Unsupported coin: {coin}")

# Main script
if __name__ == "__main__":
    while True:
        print("\nCrypto Wallet Manager")
        print("1. Create a new wallet")
        print("2. Fund a wallet")
        print("3. Get wallet balance")
        print("4. Send funds")
        print("5. View Transaction Details")
        print("6. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            coin = input("Enter coin (btc/ltc/eth): ").lower()
            create_wallet(coin)
        elif choice == "2":
            coin = input("Enter coin (btc/ltc/eth): ").lower()
            address, _ = get_phrase(coin)  # Get address from file
            if address:
                amount = float(input("Enter amount to fund: "))
                fund_wallet(coin, address, amount)
            else:
                print(f"No {coin.upper()} wallet found. Create one first.")
        elif choice == "3":
            coin = input("Enter coin (btc/ltc/eth): ").lower()
            address, _ = get_phrase(coin)  # Get address from file
            if address:
                get_wallet_balance(coin, address)
            else:
                print(f"No {coin.upper()} wallet found. Create one first.")
        elif choice == "4":
            coin = input("Enter coin (btc/ltc/eth): ").lower()
            from_address, private_key = get_phrase(coin)  # Get address and private key
            if from_address and private_key:
                to_address = input("Enter receiving wallet address: ").strip()
                amount = float(input("Enter amount to send: "))
                txid = send_funds(coin, from_address, private_key, to_address, amount)
            else:
                print(f"No {coin.upper()} wallet found. Create one first.")
        elif choice == "5":
            coin = input("Enter coin (btc/ltc/eth): ").lower()
            txid = input("Enter transaction ID: ").strip()
            view_transaction_details(coin, txid)
        elif choice == "6":
            break
        else:
            print("Invalid choice!")
