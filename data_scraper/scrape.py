import requests
import json
import csv

MAIN_URL = "https://blockchain.info/block/%s?format=json"
START_BLOCK = "0000000000000000000d26984c0229c9f6962dc74db0a6d525f2f1640396f69c" # block height 520000

SAVE_DIR = "data/"
SAVE_NAME = SAVE_DIR + "%s_%s.csv"
LATEST_LOCATION = "latest"

def get_block(block_index):
    r = requests.get(MAIN_URL % block_index)
    
    try:
        return json.loads(r.text) 
    except:
        with open("error", "wb") as f:
            f.write(r.text)

        raise Exception("Text not json")

def parse_io(data):
    new_generated = 0
    output_addr_decode_errors = 0

    for tx in data["tx"]:
        tx_inputs = []
        for _in in tx["inputs"]:
            if "prev_out" not in _in:
                tx_inputs.append(["NEW GENERATED", None])
                new_generated += 1
                continue

            input_data = _in["prev_out"]
            tx_inputs.append([input_data["addr"], input_data["value"]])

        tx_outputs = []
        for _out in tx["out"]:
            if "addr" not in _out:
                tx_outputs.append([None, _out["value"]])
                output_addr_decode_errors += 1
                continue
            
            tx_outputs.append([_out["addr"], _out["value"]])

        yield (tx_inputs, tx_outputs)

    # print("NEW_GENERATED", new_generated)
    # print("FAULT DECODING OUTPUT", output_addr_decode_errors)

def extract_tx(_in, _out):
    for ii, (ia, _) in enumerate(_in):
        if _in[ii][1] == 0:
            continue
        
        for oi, (oa, _) in enumerate(_out):
            if not _out[oi][1]:
                continue
                
            if _in[ii][1] == None:
                yield [ia, oa, _out[oi][1]]
                _in[ii][1]  = 0
                _out[oi][1] = 0
            elif _in[ii][1] > _out[oi][1]:
                yield [ia, oa, _out[oi][1]]
                _in[ii][1] -= _out[oi][1]
                _out[oi][1] = 0
            else:
                yield [ia, oa, _in[ii][1]]
                _out[oi][1] -= _in[ii][1]
                _in[ii][1] = 0

                break
    
    if _in[ii][1] > 0:
        yield [ia, "FEE", _in[ii][1]]

def append_to_file(filename, iterable):
    if os.path.isfile(filename):
        os.remove(filename)

    with open(filename, 'a', newline="") as f:
        writer = csv.writer(f)  
        
        for line in iterable:
            writer.writerow(line)

def write_latest(block):
    with open(LATEST_LOCATION, 'w') as f:
        f.write(block)

def read_latest():
    with open(LATEST_LOCATION, "r") as f:
        return f.read()


if __name__ == "__main__":
    import os
    import pprint
    from itertools import chain

    if os.path.isfile(LATEST_LOCATION):
        print(read_latest())
        START_BLOCK = read_latest()

    if not os.path.isdir(SAVE_DIR):
        os.mkdir(SAVE_DIR)

    current_block = START_BLOCK
    
    while True:
        print("Starting with %s" % current_block)
        block = get_block(current_block)

        io = parse_io(block)
        transactions = chain(*map(lambda x: extract_tx(*x), io))
        
        append_to_file(SAVE_NAME % (current_block, block["time"]), transactions)

        write_latest(current_block)
        current_block = block["prev_block"]

        break