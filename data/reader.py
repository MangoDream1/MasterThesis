import os
import csv
import subprocess

from Objects.Transaction import Transaction
from data.data_constants import SAVE_DIR

def select(item_index, lbound, ubound, size):
    selection = []
    for block_file in os.scandir(SAVE_DIR):
        info = block_file.name.split("_")

        if int(info[item_index]) >= lbound and int(info[item_index]) <= ubound:
            selection.append(block_file.name)

        if size and len(selection) >= size:
            return selection

    return selection

def select_on_block_height(lbound, ubound, size):
    return select(0, lbound, ubound, size)

def select_on_timestamp(lbound, ubound, size):
    return select(1, lbound, ubound, size)

def read_lines_selection(selection, exclude_miner_receive=False):
    for fname in selection:
        block_number, timestamp, _, _ = fname.split("_")
        path = os.path.join(SAVE_DIR, fname)
        
        if exclude_miner_receive:
            last_line = subprocess.check_output(["tail", "-1", path]) # last line always miner generation line
            miner = last_line.decode("utf8").strip().split(",")[1]

        with open(path, "r") as f:
            reader = csv.reader(f)

            for line in reader:
                if exclude_miner_receive and line[1] == miner:
                    continue

                yield line + [timestamp, block_number]

def create_transactions(selection, **kwargs):
    for line in read_lines_selection(selection, **kwargs):
        yield Transaction(*line)

# TODO: data statistics; all data