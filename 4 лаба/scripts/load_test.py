from web3 import Web3
import json
import time

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

if not w3.is_connected():
    raise Exception("Нет подключения к Ganache")

owner = w3.eth.accounts[0]
client = w3.eth.accounts[1]

contract_address = "СЮДА_ВСТАВИШЬ_АДРЕС_КОНТРАКТА"

with open("build/IoTAccessABI.json", "r", encoding="utf-8") as f:
    abi = json.load(f)

contract = w3.eth.contract(address=contract_address, abi=abi)

device_id = "device-001"

success = 0
failed = 0
times = []

for i in range(500):
    start_time = time.time()
    try:
        tx = contract.functions.recordAccess(device_id, "read").transact({
            "from": client
        })
        w3.eth.wait_for_transaction_receipt(tx)
        end_time = time.time()

        success += 1
        times.append(end_time - start_time)

    except Exception:
        failed += 1

avg_time = sum(times) / len(times) if times else 0
total_time = sum(times) if times else 1
tps = success / total_time if total_time > 0 else 0
reject_percent = (failed / 500) * 100

print("Успешных транзакций:", success)
print("Отклонённых транзакций:", failed)
print("Среднее время включения:", avg_time)
print("Пропускная способность TPS:", tps)
print("Процент отклонённых:", reject_percent)