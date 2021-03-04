import gdown
import zipfile
import shutil
import os

# This script should be used to download the data we are using
# for this project.
#
# ------------------------------------------------------------


# The name of the folder inside of the ZIP
raw_name = "mails"
# The URL containing the data
url = 'https://drive.google.com/uc?id=18fCa9AgK7tp4ehS2DV7beEA8DEhuqvLu'


print("Clearing previous data...")

if os.path.exists("./data/data.zip"):
    os.remove("./data/data.zip")

if os.path.exists("./data/raw_mails"):
    shutil.rmtree("./data/raw_mails")

if os.path.exists("./data/mails"):
    shutil.rmtree("./data/mails")

print("Collecting new data...")

output = "./data/data.zip"

gdown.download(url, output, quiet=False)

with zipfile.ZipFile("./data/data.zip", 'r') as zip_ref:
    zip_ref.extractall("./data/")

os.remove("./data/data.zip")

os.rename("./data/" + raw_name, "./data/raw_mails")

print("Successfully collected the data.")
