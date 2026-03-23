import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, List

def sha256_hex(text:str)-> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def utc_now_iso()-> str:
    return datetime.now(timezone.utc).isoformat()

@dataclass
class Block:
    index: int
    timestamp: str
    data: any
    previous_hash:str
    nonce: int = 0
    hash: str = field(init= False)
    
    def __post_init__(self) -> None:
        self.hash = self.calculate_hash()
        
    def calculate_hash(self) -> str:
        payload = {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
        }
        
        raw = json.dumps(payload, ensure_ascii=False, sort_keys= True, separators =(",",":"))
        return sha256_hex(raw)

if __name__ == "__main__":
    b = Block(
        index = 0,
        timestamp= utc_now_iso(),
        data= "Genesis Block",
        previous_hash="0",
    )
    print("hash:",b.hash)

def create_genesis_block()-> Block:
    return Block(
        index= 0, 
        timestamp = utc_now_iso(),
        data = "Genesis Block",
        previous_hash= "0",
        nonce = 0
    )
    
def add_block(chain: List[Block], data: Any) -> Block:
    prev = chain [ -1]
    new_block = Block(
        index = prev.index +1,
        timestamp= utc_now_iso(),
        data=data,
        previous_hash=prev.hash,
        nonce=0,
    )
    chain.append(new_block)
    return new_block

def validate_chain(chain: List[Block])->bool:
    if not chain:
        return True
    
    if chain[0].previous_hash !="0":
        return False
    if chain[0].hash != chain[0].calculate_hash():
        return False
    
    for i in range (1, len(chain)):
        cur = chain[i]
        prev = chain[ i -1]
        
        if cur.hash != cur.calculate_hash():
            return False
        
        if cur.previous_hash != prev.hash:
            return False
        
        if cur.index != prev.index + 1:
            return False
        
    return True

if __name__ =="__main__":
    chain: List[Block] = [create_genesis_block()]
    
    add_block(chain,{"from": "Dima", "to": "Putin", "amount": 15})
    add_block(chain,{"from": "Diana", "to": "Zelenckiy", "amount": 1})
    add_block(chain,"О ес детка у тебя очень грязные джинсы")
    add_block(chain,[42, 52 , 67 ,69 ,100])
    
    for block in chain:
        print("-"* 60)
        print("index:", block.index)
        print("timestamp:", block.timestamp)
        print("data:",block.data)
        print("previous_hash:",block.previous_hash)
        print("nonce:", block.nonce)
        print("hash:", block.hash)
print("ЦЕПОЧКА ВАЛИДНА:", validate_chain(chain))

# ПроверОчка
chain[2].data = "ПОДМЕНА ДАННЫХ"
print("После подмены цепочка валидна:", validate_chain(chain))
   