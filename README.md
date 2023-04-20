# Lip6-Moodle-LRS
This repository contains the template for consolidating Moodle log data extracted from a LRS.

## Quick start
### Collect your data
You first need to collect your data:

--- Il faut ajouter ici tout ce qui concerne l'extraction de Yves

Export all files into *CSV* format.

### Access your data
Place all *CSV* files in `src/datasets`. 
Replace paths in `src/paths.py`. 

### Get your consolidated data
Run `main.py`.

According to your needs, you can modify *get_consolidated_data* function call.
If you want to get more fields, modify the variable *columns*.


## Get course data
Once the data has been consolidated, you can extract data from specific courses.

### Get specific data
You have first to create the object *Records* to use its methods. 
Then, to extract specific data, you can specify the following parameters: 'year', 'course_area', 'role', 'username'. 
Note that you may choose more than one entry, and that each entry must be provided as a list.
The entire dataset is returned if you make no selections.

### Clean the dataset
You can either clean the entire dataset or each course individually by modifying the function *clean_records* in
`src/algorithms/cleaning.py` according to your specific needs.

```bash
records = cl.clean_records(records)
or
course_A = cl.clean_records(course_A)
```
### Example

```bash
from src.classes.records import Records
import src.algorithms.cleaning as cl
import src.algorithms.extracting as ex
import pandas as pd
from src.paths import course_dates_path

# ------------
# GET DATA
# ------------
# get the consolidated dataframe
df_path = 'datasets/df_consolidated.csv'
df = pd.read_csv(df_path)

# create a Records object to use its methods
records = Records(df)

# ----------------------
# GET COURSES TO ANALYSE
# ----------------------
# select specific attributes to get the desired values
course_A = ex.extract_records(records, course_area=['Course A'], role=['Student'], course_dates=course_dates_path)
course_B = ex.extract_records(records, year=[2021], username=['Student 01'])

# -----------------
# CLEAN THE DATASET
# -----------------
# you can either clean the entire dataset or each course individually
# records = cl.clean_specific_records(records)
course_A = cl.clean_specific_records(course_A)
```

## License

This project is licensed under the terms of the GNU General Public License v3.0.

If you use the library in an academic setting, please cite the following papers:
