import src.algorithms.integrating as it
import src.algorithms.transforming as tr
import src.algorithms.sorting as st
import src.algorithms.cleaning as cl
from pandas import DataFrame


def get_consolidated_data(course_names: str,
                          logs: str = "",
                          directory: str = "") -> DataFrame:

    # collect data from a directory when data are extracted file by file
    if directory != '':
        log_data = it.collect_log_files(directory)
    else:
        # collect data from a unique file (one file or more files already merged)
        log_data = it.get_dataframe(logs)

    # rename columns
    log_data = tr.rename_columns(log_data)

    # --------------------
    # DATA INTEGRATION
    # --------------------
    log_data = it.add_course_id(log_data)
    log_data = it.add_course_name(log_data, course_names)
    log_data = it.add_timestamps(log_data)
    log_data = st.sort_data(log_data)
    log_data = it.add_component(log_data)
    log_data = it.add_event_name(log_data)
    log_data = it.redefine_course_area(log_data)
    log_data = it.redefine_component(log_data)
    log_data = it.redefine_event_name(log_data)
    log_data = it.add_role(log_data)
    log_data = it.add_status(log_data)

    # --------------------
    # DATA SELECTION
    # --------------------
    # select and reorder columns
    cols = ['ID', 'Unix_Time', 'Time', 'Role', 'Username',
            'courseid', 'Course_Area', 'Context', 'Component', 'Event_name', 'Duration', 'Status']
    # drop unused columns
    log_data = log_data[cols].copy()

    return log_data


if __name__ == '__main__':

    # get the file paths
    from src.paths import *
    from src.classes.records import Records

    # ----------------------------
    # GET THE CONSOLIDATED DATASET
    # ----------------------------
    # get the consolidated dataframe
    df = get_consolidated_data(course_names=example_names_path,
                               logs=example_logs_path)

    # -----------------
    # CLEAN THE DATASET
    # -----------------
    # you can clean the dataset both from automatic events and from dataset specific events
    df = cl.clean_automatic_events(df)
    df = cl.clean_specific_events(df)

    # you can save the dataset for further analysis
    df.to_csv(example_consolidated_data_path)

    # --------------------
    # GET YOUR DATA
    # --------------------
    # you can create a Records object to use its methods
    records = Records(df)
