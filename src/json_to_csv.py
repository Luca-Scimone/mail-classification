import pandas as pd
import os
import re
import csv
from os import path, write
import os
import sys
import json

header = ['Corps', 'Catégorie']
files = []
base_path = 'data/mails'
for i in os.listdir(base_path):
    full_path = '%s/%s' % (base_path, i)
    files.append(open(full_path, 'r', encoding='utf-8').read())

with open('all_mails.csv', 'w', encoding='UTF8') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for single_file in files:
        mail_dict = json.loads(single_file)
        print(mail_dict)
        for msg in mail_dict['Mail']:
            mail_corps = msg['Corps']
            mail_cat = msg['Catégorie']
        res_part = str(mail_cat).split("1")
        ind_cat= res_part[0].count('0')
        print(ind_cat)
        data = [mail_corps, str(ind_cat)]
        # write the data
        writer.writerow(data)