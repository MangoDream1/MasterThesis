import os

MAIN_URL = "https://blockchain.info/block/%s?format=json"
START_BLOCK = "0000000000000000000d26984c0229c9f6962dc74db0a6d525f2f1640396f69c" # block height 520000

FILE_PATH = os.path.dirname(os.path.realpath(__file__))
SAVE_DIR = os.path.join(FILE_PATH, "data")
DEBUG = os.path.join(FILE_PATH, "debug")
ERROR = os.path.join(FILE_PATH, "debug")
SAVE_NAME = os.path.join(SAVE_DIR, "%s_%s_%s_%s.csv") # height, epoch time, n_tx (not including fees, multi transactions), block_id
LATEST_LOCATION = os.path.join(FILE_PATH, "latest")