import src.algorithms.integrating as it
import src.algorithms.transforming as tr
import src.algorithms.duration as dt
import src.algorithms.sorting as st
from src.classes.records import Records
from pandas import DataFrame


def get_consolidated_data(extracted_logs: str) -> DataFrame:

    # collect data
    data_logs = it.get_dataframe(extracted_logs)
    data_logs = data_logs.reset_index()
    data_logs = tr.rename_columns(data_logs)

    # --------------------
    # DATA INTEGRATION
    # --------------------
    data_logs = it.add_course_id(data_logs)
    data_logs = it.add_timestamps(data_logs)
    data_logs = it.add_component(data_logs)
    data_logs = it.add_event_name(data_logs)
    data_logs = it.course_area_categorisation(data_logs)
    data_logs = it.component_redefinition(data_logs)
    # course_logs = it.event_name_redefinition(course_logs)

    # --------------------
    # DATA SELECTION
    # --------------------
    # select and reorder columns
    cols = ['ID', 'Unix_Time', 'Time', 'Course', 'Username', 'Component', 'Event_name']
    # drop unused columns
    # course_logs = course_logs[cols].copy()

    # --------------------
    # EVENT DURATION
    # --------------------
    # create a Records object to use its methods
    # course_logs = Records(course_logs)
    # to calculate the duration values must be sorted by username and ID
    # course_logs = st.sort_records(course_logs, sort_by=['Username', 'ID'])
    # get the standard duration for all values of the dataframe
    # df_duration = dt.get_basic_duration(course_logs)

    # dani_logs = it.get_dataframe('datasets/df_prepared.csv')
    # dani_logs = Records(dani_logs)

    return data_logs


if __name__ == '__main__':

    from src.paths import *

    df = get_consolidated_data(extracted_logs=course_logs_path)
