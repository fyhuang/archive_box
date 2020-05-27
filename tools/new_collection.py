"""Tool to create a config entry for a new collection."""

import random

def make_cid():
    cid_b = bytearray()
    for i in range(16):
        cid_b.append(random.randint(0, 255))
    return cid_b.hex()

if __name__ == "__main__":
    cid = make_cid()
    print("[collections.{}]".format(cid))
    print("display_name=\"{}\"".format(cid))
    print("storage=\"local\"")
    print("local_storage.root=")
