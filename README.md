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
python3 ./data_processing/to_json.py [ENCODING -- exemple: utf-8, ISO-8859-1]
``` 

Available datasets:

- Mails CGT (non labelisées): 
	- argument 1: https://drive.google.com/uc?id=18fCa9AgK7tp4ehS2DV7beEA8DEhuqvLu
	- argument 2: mails
- Mails anonymisés par une société tierece (non labelisés): 
	- argument 1: https://drive.google.com/uc?id=1w2JsmhgSSFbHDokavDZ7jtsUpedAwUAk
	- argument 2: OUT
- Mails anonymisés par notre script (partielement labelisés)
	- argument 1: https://drive.google.com/uc?id=1O1qOK8nWRa3hTVSxUnPAYJN5Di_am9bi
	- argument 2: raw_mails

One usage exemple:

```{python}
python3 ./script/collect_data.py https://drive.google.com/uc?id=1O1qOK8nWRa3hTVSxUnPAYJN5Di_am9bi raw_mails
python3 ./data_processing/to_json.py "utf-8"
```