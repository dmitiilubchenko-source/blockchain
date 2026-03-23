from web3 import Web3
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

abi_path = os.path.join(BASE_DIR, "build", "IoTAccessABI.json")
bytecode_path = os.path.join(BASE_DIR, "build", "IoTAccessByteCode.txt")

RPC_URL = "http://127.0.0.1:7545"
w3 = Web3(Web3.HTTPProvider(RPC_URL))

print("RPC:", RPC_URL)
print("Connected:", w3.is_connected())

if not w3.is_connected():
    raise Exception("Нет подключения к Ganache")

with open(abi_path, "r", encoding="utf-8") as f:
    abi = json.load(f)

with open(bytecode_path, "r", encoding="utf-8") as f:
    bytecode = f.read().strip()

account = w3.eth.accounts[0]
contract = w3.eth.contract(abi=abi, bytecode=bytecode)

print("Deploying contract...")

tx_hash = contract.constructor().transact({
    "from": account,
    "gas": 6000000
})

receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print("Contract deployed at address:")
print(receipt.contractAddress)