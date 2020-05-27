import random

if __name__ == "__main__":
    cid_b = bytearray()
    for i in range(16):
        cid_b.append(random.randint(0, 255))
    print(cid_b.hex())
