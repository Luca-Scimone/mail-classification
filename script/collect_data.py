import os
import shutil
import sys
import zipfile
import gdown

# This script should be used to download the data we are using
# for this project.
#
# ------------------------------------------------------------

if len(sys.argv) != 3:
    print("Wrong arguments.")
    print("Usage: python3 ./script/collect_data.py [URL] [FOLDER NAME]")
    exit (1)

# The URL containing the data
url = str(sys.argv[1])

raw_name = str(sys.argv[2])


print("Clearing previous data...")


folder = "./data/"
for filename in os.listdir(folder):
    file_path = os.path.join(folder, filename)
    if filename == ".keep":
        continue
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    except Exception as e:
        print('Failed to delete %s. Reason: %s' % (file_path, e))

print("Collecting new data...")

output = "./data/data.zip"

gdown.download(url, output, quiet=False)

with zipfile.ZipFile("./data/data.zip", 'r') as zip_ref:
    zip_ref.extractall("./data/")

os.remove("./data/data.zip")

os.rename("./data/" + raw_name, "./data/raw_mails")

print("Successfully collected the data.")
