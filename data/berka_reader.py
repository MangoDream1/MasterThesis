import csv
from Objects.Transaction import Transaction

FILE = "data/berka_data/trans.asc"

def get_transactions():

    txs = []
    with open(FILE, "r") as f:
        reader = csv.reader(f, delimiter=';', quotechar='"')
        
        next(reader)
        
        for x in reader:
            if x[4] == "VKLAD":
                continue
                
            _, fr, timestamp, _, _, amount, _, _, _, to = x
            
            amount = float(amount)
            
            txs.append(Transaction(to, fr, amount, timestamp))

    return txs