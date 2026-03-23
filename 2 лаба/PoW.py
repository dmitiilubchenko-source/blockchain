import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, List
import time

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
    
    def mine(self, difficulity: int) -> None:
        prefix = "0" * difficulity
        self.nonce = 0
        
        while True:
            self.hash = self.calculate_hash()
            if self.hash.startswith(prefix):
                break
            self.nonce += 1
    

def create_genesis_block(difficulty: int) -> Block:
    b = Block(
        index=0,
        timestamp=utc_now_iso(),
        data="Genesis Block",
        previous_hash="0",
        nonce=0
    )

    b.mine(difficulty)
    return b

def add_block(chain: List[Block], data: Any, difficulty: int) -> Block:
    prev = chain [ -1]
    new_block = Block(
        index = prev.index +1,
        timestamp= utc_now_iso(),
        data=data,
        previous_hash=prev.hash,
        nonce=0,
    )
    
    new_block.mine(difficulty)
    
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
    
    difficulty= 4
    chain: List[Block] = [create_genesis_block(difficulty)]
    
    add_block(chain, {"from": "Dima", "to": "Putin", "amount": 15}, difficulty)
    add_block(chain, {"from": "Diana", "to": "Zelenckiy", "amount": 1}, difficulty)
    add_block(chain, {"text": "О ес детка у тебя очень грязные джинсы"}, difficulty)
    add_block(chain,[42, 52 , 67 ,69 ,100], difficulty)
    
    for block in chain:
        print("-"* 60)
        print("index:", block.index)
        print("timestamp:", block.timestamp)
        print("data:",block.data)
        print("previous_hash:",block.previous_hash)
        print("nonce:", block.nonce)
        print("hash:", block.hash)
        
    print("ЦЕПОЧКА ВАЛИДНА:", validate_chain(chain))

    print("Замеры времени:")
    
    for d in (2,3,4):
        
        b= Block(
            index=1,
            timestamp = utc_now_iso(),
            data="test",
            previous_hash="a"*64,
            nonce= 0
        )
        
        start = time.time()
        b.mine(d)
        end = time.time()
        
        print(f"difficulty={d} | time={end-start:.4f} sec")





   