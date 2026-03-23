from web3 import Web3
import json

RPC_URL = "http://127.0.0.1:7545"
w3 = Web3(Web3.HTTPProvider(RPC_URL))

if not w3.is_connected():
    raise Exception("Нет подключения к Ganache")

owner = w3.eth.accounts[0]
client = w3.eth.accounts[1]
bad_client = w3.eth.accounts[2]

contract_address = "0xc68F2F7E056A037F638a59C5310b05ab805429d3"

with open("build/IoTAccessABI.json", "r", encoding="utf-8") as f:
    abi = json.load(f)

contract = w3.eth.contract(address=contract_address, abi=abi)

device_id = "device-001"

print("1. Регистрируем устройство...")
tx1 = contract.functions.registerDevice(device_id).transact({
    "from": owner
})
w3.eth.wait_for_transaction_receipt(tx1)
print("Устройство зарегистрировано")

print("2. Выдаём доступ клиенту...")
tx2 = contract.functions.grantAccess(device_id, client).transact({
    "from": owner
})
w3.eth.wait_for_transaction_receipt(tx2)
print("Доступ выдан")

print("3. Клиент выполняет действие open...")
tx3 = contract.functions.recordAccess(device_id, "open").transact({
    "from": client
})
w3.eth.wait_for_transaction_receipt(tx3)
print("Событие записано")

print("4. Проверяем попытку доступа без прав...")
try:
    tx4 = contract.functions.recordAccess(device_id, "read").transact({
        "from": bad_client
    })
    w3.eth.wait_for_transaction_receipt(tx4)
    print("Ошибка: доступ почему-то разрешён")
except Exception:
    print("Несанкционированный доступ отклонён")

print("5. Получаем историю...")
count = contract.functions.getHistoryCount(device_id).call()
print("Количество событий:", count)

for i in range(count):
    item = contract.functions.getHistoryItem(device_id, i).call()
    print(f"Событие #{i}:", item)