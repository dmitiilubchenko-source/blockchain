import json
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List

def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

# --- Реализация дерева Меркла ---

def get_merkle_root(txs: List['Transaction']) -> str:
    """Вычисляет корень дерева Меркла для списка транзакций."""
    if not txs:
        return sha256_hex("empty_block")

    hashes = [sha256_hex(json.dumps(tx.to_dict(), sort_keys=True)) for tx in txs]

    while len(hashes) > 1:
        if len(hashes) % 2 != 0:
            hashes.append(hashes[-1]) 
        
        new_level = []
        for i in range(0, len(hashes), 2):
            combined = hashes[i] + hashes[i+1]
            new_level.append(sha256_hex(combined))
        hashes = new_level

    return hashes[0]

balances = {
    "alice": 20,
    "bob": 0,
    "carol": 5
}

@dataclass
class Transaction:
    from_: str
    to: str
    amount: int
    payload: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "from": self.from_,
            "to": self.to,
            "amount": self.amount,
            "payload": self.payload
        }

@dataclass
class Block:
    index: int
    timestamp: str
    transactions: List[Transaction]
    previous_hash: str
    nonce: int = 0
    merkle_root: str = field(init=False)
    hash: str = field(init=False)

    def __post_init__(self):
        self.merkle_root = get_merkle_root(self.transactions)
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        payload = {
            "index": self.index,
            "timestamp": self.timestamp,
            "merkle_root": self.merkle_root, 
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
        }
        raw = json.dumps(payload, sort_keys=True)
        return sha256_hex(raw)

    def verify_merkle_root(self) -> bool:
        return self.merkle_root == get_merkle_root(self.transactions)

def apply_transaction(tx, balances):
    if tx.from_ not in balances or tx.to not in balances:
        raise Exception("Неизвестный аккаунт")
    if balances[tx.from_] < tx.amount:
        raise Exception("Недостаточно средств")
    if "min_balance" in tx.payload:
        if balances[tx.from_] <= tx.payload["min_balance"]:
            raise Exception("Условия перевода не выполнено")
    balances[tx.from_] -= tx.amount
    balances[tx.to] += tx.amount

def add_block(chain, txs, balances):
    snapshot = balances.copy()
    prev = chain[-1]
    try:
        for tx in txs:
            apply_transaction(tx, balances)  
    except Exception as e:
        balances.clear() 
        balances.update(snapshot)
        print("ROLLBACK", e)
        return False

    new_block = Block(
        index=prev.index + 1,
        timestamp=utc_now_iso(),
        transactions=txs,
        previous_hash=prev.hash,
        nonce=0
    )
    chain.append(new_block)
    return True

def create_genesis_block() -> Block:
    return Block(index=0, timestamp=utc_now_iso(), transactions=[], previous_hash="0")



if __name__ == "__main__":
    chain = [create_genesis_block()]

    txs1 = [Transaction("alice", "bob", 5), Transaction("bob", "carol", 2)]
    add_block(chain, txs1, balances)

    current_block = chain[-1]
    print(f"Блок {current_block.index} создан.")
    print(f"Merkle Root: {current_block.merkle_root}")
    print(f"Проверка корня Меркла: {'Успешно' if current_block.verify_merkle_root() else 'Ошибка'}")

    print("Попытка взлома (изменение суммы транзакции в памяти)")
    current_block.transactions[0].amount = 1000 
    
    print(f"Проверка корня Меркла после подмены: {'Успешно' if current_block.verify_merkle_root() else 'ОШИБКА ЦЕЛОСТНОСТИ'}")