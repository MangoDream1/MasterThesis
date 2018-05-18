import requests
import json
import csv
import os
from data_constants import *

def get_block(block_index):
    r = requests.get(MAIN_URL % block_index)
    
    try:
        return json.loads(r.text)
    except:
        with open(ERROR, "w") as f:
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

def extract_tx(io_iterable):
    miner = "UNKOWN"
    saved = None

    for _in, _out in io_iterable:
        for ii, (ia, _) in enumerate(_in):
            if _in[ii][1] == 0:
                continue
            
            for oi, (oa, _) in enumerate(_out):
                if not _out[oi][1]:
                    continue
                    
                if _in[ii][1] == None:
                    saved = [ia, oa, _out[oi][1]]
                    _in[ii][1]  = 0
                    _out[oi][1] = 0
                    miner = oa
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
            saved[-1] -= _in[ii][1] # remove fees from created amount
            yield [ia, miner, _in[ii][1]] # add fee as tx
    
    # yield adjusted mined value
    yield saved

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
    if os.path.isfile(LATEST_LOCATION):
        START_BLOCK = read_latest()

    if not os.path.isdir(SAVE_DIR):
        os.mkdir(SAVE_DIR)

    current_block = START_BLOCK
    
    while True:
        print("Starting with %s" % current_block)
        block = get_block(current_block)

        try:
            io = parse_io(block)
            transactions = extract_tx(io)

            append_to_file(SAVE_NAME % (block["height"], block["time"], block["n_tx"], current_block), transactions)
        except:
            # Save failures to seperate file
            with open(DEBUG, "a") as f:
                f.write(current_block)
                f.write("\n")

        current_block = block["prev_block"]
        write_latest(current_block)