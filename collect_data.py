import gdown
import zipfile
import shutil
import os

# The name of the folder inside of the ZIP
raw_name="mails"



print ("Clearing previous data...")

if os.path.exists("./data/data.zip"):
  os.remove("./data/data.zip")

if os.path.exists("./data/mails"):
	shutil.rmtree("./data/mails")

print("Collecting new data...")

url = 'https://drive.google.com/uc?id=18fCa9AgK7tp4ehS2DV7beEA8DEhuqvLu'

output = "./data/data.zip"

gdown.download(url, output, quiet=False) 

with zipfile.ZipFile("./data/data.zip", 'r') as zip_ref:
    zip_ref.extractall("./data/")

os.remove("./data/data.zip")

os.rename("./data/" + raw_name, "./data/mails")

print("Successfully collected the data.")