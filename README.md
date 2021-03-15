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

- Mails CGT (non labelisées): 
	- argument 1: https://drive.google.com/uc?id=18fCa9AgK7tp4ehS2DV7beEA8DEhuqvLu
	- argument 2: mails
- Mails anonymisés par une société tierece (non labelisés): 
	- argument 1: https://drive.google.com/uc?id=1w2JsmhgSSFbHDokavDZ7jtsUpedAwUAk
	- argument 2: OUT

One usage exemple:

```{python}
python3 ./script/collect_data.py https://drive.google.com/uc?id=1w2JsmhgSSFbHDokavDZ7jtsUpedAwUAk OUT
python3 ./data_processing/to_json.py "ISO-8859-1"
```