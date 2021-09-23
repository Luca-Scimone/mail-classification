import pandas as pd
import os
from os import path


if not os.path.exists('data_csv'):
    os.makedirs('data_csv')
    print("Created Directory : ", 'data_csv')
else:
    print("Directory already existed : ", 'data_csv')
num_mails = 0
for filename in os.listdir('data/mails'):
    num_mails +=1
    with open(os.path.join('data/mails', filename), 'r') as f: # open in readonly mode
        # do your stuff
        df = pd.read_json (f)
        complete = os.path.join('data_csv', 'mail' + str(num_mails))
        df.to_csv (complete)