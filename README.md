# Moodle-XAPI-Consolidation
This repository contains the template for consolidating Moodle log data extracted from an LRS in xAPI format.

## Table of contents
* [Collect your data](#collect-your-data)
* * [Data structure](#data-structure)
* [Access your data](#access-your-data)
* [Get your consolidated data](#get-your-consolidated-data)
* * [Example](#example)
* [License](#license)
* [Acknowledgments](#acknowledgements)
* [Contacts](#contact--s-)

## Quick start
This section contains a description of the data structure expected by the algorithms, as well as instructions on how 
collecting your data from the LRS, accessing and consolidating them.

### Collect your data
You first need to collect your data from the LRS.
--- Yves

#### Data structure
The template requires two files to function properly: one with the extracted logs and another with the names of the courses.

The logs file should contain at least the following columns:
*  statement.timestamp - _timestamp_ 
*  statement.actor.name - _Email_ (this field can be any field that represents the actor: _email_, _id_, _name_, _username_)
*  statement.verb.display.en - _ACTION_VERB_ 
*  statement.object.definition.id - _OBJECT_ID_
*  statement.object.definition.name.en - _OBJECT_NAME_
*  statement.object.definition.type - _OBJECT_TYPE_
*  statement.object.definition.description.en - _OBJECT_DESCRIPTION_
*  statement.contextActivities.grouping - _RelatedActivities_
*  statement.context.extensions.event_name - _Context_

Please be aware that you can use various names depending on your needs, but you have to rename them by respecting the fields in the `src.algorithms.transforming.py` file.

The name's file should contain two columns: the name of the courses and their id. The `src/datasets` folder contains examples of the expected files. 

Export all files into *CSV* format.

### Access your data
You have the option of exporting multiple files, one for each course, or a single file for one or multiple courses.
Single *CSV* file should be placed in `src/datasets` folder. Multiple course files should be placed in 
the `src/datasets/directory` folder.

Replace names in `src/paths.py` file. 

### Get your consolidated data
Make sure that you have all the necessary libraries, modules, and packages installed on your machine.
```bash
pip install -r requirements.txt
```
Run `main.py`.

Please be aware, that if you use a unique directory with multiple files, you have to modify the `get_consolidated_data` function call as follows: 
    
`df = get_consolidated_data(directory=directory_path, course_names=course_names_path)`

According to your needs, you can modify the `get_consolidated_data` function.

## Get course data
Once the data has been consolidated, you can extract data from specific courses.

### Clean the dataset
You can clean the dataset by modifying functions in `src/algorithms/cleaning.py` file according to your needs.

### Get specific data
You have first to create the object *Records* to use its methods. 
Then, to extract specific data, you can specify the following parameters: 'course_area', 'role', 'username'. 
Note that you may choose more than one entry, and that each entry must be provided as a list.
The entire dataset is returned if you make no selections.

You can also specify the 'dates_path' containing the course dates to remove values that don't fall within the start and 
end dates.
You can add start and end dates manually or by querying the database:
```SQL
SELECT id, shortname, startdate, enddate 
FROM mdl_course
where id <> 1
```

### Example

```bash
from src.classes.records import Records
import src.algorithms.extracting as ex
import pandas as pd
from src.paths import example_dates_path

# ------------
# GET DATA
# ------------
# get the consolidated dataframe
df_path = 'src/datasets/df_consolidated.csv'
df = pd.read_csv(df_path)

# create a Records object to use its methods
records = Records(df)

# ----------------------
# GET COURSES TO ANALYSE
# ----------------------
# select specific attributes to get the desired values
course_A = ex.extract_records(records, course_area=['Course A'], role=['Student'], filepath=example_dates_path)
course_B = ex.extract_records(records, username=['Student 01'])
```

## License

This project is licensed under the terms of the GNU General Public License v3.0.

If you use the template in an academic setting, please cite the following papers:

> Authors' name

```tex
TO BE ADDED
```

## Acknowledgements

## Contact(s)
[Daniela Rotelli](mailto:daniela.rotelli@phd.unipi.it) - Department of Computer Science - University of Pisa (Italy)

[Yves Noël](mailto:yves.noel@sorbonne-universite.fr) - Lab Lip6 - MOCAH team - Sorbonne Université - Paris (France)
