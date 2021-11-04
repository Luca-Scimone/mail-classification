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

with open('all_mails_labeled.csv', 'w', encoding='UTF8') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for single_file in files:
        mail_dict = json.loads(single_file)
        for msg in mail_dict['Mail']:
            mail_corps = msg['Corps']
            mail_cat = msg['Catégorie'][0]
        cat = list(mail_cat.keys())[list(mail_cat.values()).index(1)]
        data = [mail_corps, str(cat)]
        writer.writerow(data)
