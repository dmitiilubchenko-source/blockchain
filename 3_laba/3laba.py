import json
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List

def sha256_hex(text:str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def utc_now_iso()-> str:
    return datetime.now(timezone.utc).isoformat()

balances= {
    "alice": 20,
    "bob": 0,
    "carol":5
}

@dataclass
class Transaction:
    from_:str
    to:str
    amount: int
    payload: Dict[str, Any]= field(default_factory=dict)
    
    def to_dict(self)-> Dict[str,Any]:
        return{
            "from": self.from_,
            "to": self.to,
            "amount": self.amount,
            "payload": self.payload
        }
  
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
   
def add_block(chain, txs, difficulty, balances):
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

    new_block= Block(
        index= prev.index+1,
        timestamp=utc_now_iso(),
        transactions=txs,
        previous_hash=prev.hash,
        nonce=0
    )
    chain.append(new_block)
    return True

@dataclass
class Block:
    index: int
    timestamp: str
    transactions: List[Transaction]
    previous_hash: str
    nonce:int= 0
    hash: str = field(init=False)

    def __post_init__(self):
        self.hash = self.calculate_hash()

    def calculate_hash(self)-> str:
        payload={
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce":self.nonce,
        }

        raw = json.dumps(payload, sort_keys= True)
        return sha256_hex(raw)

def create_genesis_block() -> Block:
    b = Block(
        index= 0,
        timestamp= utc_now_iso(),
        transactions=[],
        previous_hash="0",
        nonce= 0
    )   
    return b

if __name__ == "__main__":

    chain = [create_genesis_block()]

    print("Начальные балансы:", balances)

    txs1 = [
        Transaction("alice", "bob", 5, {}),
        Transaction("bob", "carol", 2, {})
    ]
    add_block(chain, txs1, 1, balances)
    print("После блока 1:", balances)

    txs2 = [
        Transaction("alice", "carol", 3, {"min_balance": 10})
    ]
    add_block(chain, txs2, 1, balances)
    print("После блока 2:", balances)

    txs3 = [
        Transaction("bob", "alice", 100, {})
    ]
    add_block(chain, txs3, 1, balances)
    print("После блока 3:", balances)

    print("Количество блоков:", len(chain))