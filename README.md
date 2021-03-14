# PI

## Usage

### Starting the Conda Environment

In order to start the conda environment: 

```
conda env create --file environment.yml
conda activate pi_env
```

To update the conda environement:

```
conda env update
```

### Getting the data

To load the emails:

```{python}
python3 ./script/collect_data.py [URL] [FOLDER NAME]
python3 ./data_processing/to_json.py [ENCODING]
``` 

Available datasets:

- Mails CGT: 
	- argument 1: https://drive.google.com/uc?id=18fCa9AgK7tp4ehS2DV7beEA8DEhuqvLu
	- argument 2: mails
- Mails labélisés: 
	- argument 1: https://drive.google.com/uc?id=1w2JsmhgSSFbHDokavDZ7jtsUpedAwUAk
	- argument 2: OUT

One usage exemple:

```{python}
python3 ./script/collect_data.py https://drive.google.com/uc?id=1w2JsmhgSSFbHDokavDZ7jtsUpedAwUAk OUT
python3 ./data_processing/to_json.py "ISO-8859-1"
```


### To modify the data

Go to https://drive.google.com/drive/folders/1aHmq-LpAzD4c9_43hIL9QHL1y8LL6GKL?usp=sharing.

Delete the previous version of mails.zip and add the new one.

Get the shared link of mails.zip

In the ```collect_data.py``` script modify line 15 with the new URL:

```{python}
# The URL containing the data
url = 'https://drive.google.com/uc?id=18fCa9AgK7tp4ehS2DV7beEA8DEhuqvLu'
```