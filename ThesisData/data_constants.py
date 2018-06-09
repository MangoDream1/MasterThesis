import os

FILE_PATH = os.path.dirname(os.path.realpath(__file__))
SAVE_DIR = os.path.join(FILE_PATH, "data")

SAVE_NAME = os.path.join(SAVE_DIR, "%s.%s")