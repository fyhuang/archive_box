import random

def new_id() -> str:
    id_bytes = bytearray()
    for i in range(12):
        id_bytes.append(random.randint(0, 255))
    return id_bytes.hex()
