from src.classes.records import Records
import src.algorithms.integrating as it
from pandas import DataFrame


def get_startdate_enddate(df: DataFrame,
                          file_path: str):
    """
    Remove values that are inconsistent with the start and end dates. You can query the database or manually add them.

    Database query:
        select id, startdate, enddate
        from prefix_course
        where id <> 1

    Returns: The dataframe purged of records previously or lately recorded in relation to course dates.
    """

    course_dates = it.get_dataframe(file_path, columns=['id', 'startdate', 'enddate'])

    for idx in range(len(course_dates)):
        courseid = course_dates.iloc[idx]['id']
        startdate = course_dates.iloc[idx]['startdate']
        enddate = course_dates.iloc[idx]['enddate']
        to_remove = list((df.loc[(df['courseid'] == courseid) &
                                 ((df['Unix_Time'] < startdate) | (df['Unix_Time'] > enddate))]).index)
        df.drop(to_remove, axis=0, inplace=True)
        df = df.reset_index(drop=True)

    return df


def extract_records(records: Records,
                    course_area: [str] = None,
                    role: [str] = None,
                    username: [str] = None,
                    filepath: str = "") -> Records:

    """
    Return the filtered records by course_area, role and/or username and sorted by the specified field.

    Args:
        records: object of the class Records to analyse
        course_area: course(s) or area(s) of the platform
        role: 'Student', 'Teacher', 'Manager', etc.
        username: user id's
        filepath: path to the course dates file

    Returns:
        Object of the class Records
    """

    # attributes to filter
    filters = dict([('Course_Area', course_area),
                    ('Role', role),
                    ('Username', username)
                    ])

    # columns in the dataframe
    columns = [i for i in filters if filters[i] is not None]

    # get the df
    df = records.get_df()

    for column in columns:
        # for each column filter the values
        df = df.loc[df[column].isin(filters.get(column))]

    # get only the values between start_date and end_date
    if filepath != "":
        df = get_startdate_enddate(df.copy(), filepath)

    # create a Records object for the extracted values
    records = Records(df.copy())

    return records
