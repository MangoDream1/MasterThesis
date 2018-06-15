from ThesisData.result_matrix import TX_SIZES
from ThesisData.data_constants import SAVE_NAME


FILE = SAVE_NAME % ("result_matrix", "txt")
SAVE_FILE = SAVE_NAME % ("result_matrix_percentage", "txt")

lines = []
with open(FILE, "r") as f:
    for l in f:
        lines.append([float(x) for x in l.strip().split("\t")])

with open(SAVE_FILE, "a") as f:
    for l in lines:
        for i, v in enumerate(l):
            f.write("{:4.1f}%\t".format((TX_SIZES[i] - v) / TX_SIZES[i] * 100))

        f.write("\n")
