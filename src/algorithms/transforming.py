from pandas import DataFrame
import src.algorithms.timing as tm


def rename_columns(df: DataFrame) -> DataFrame:

    # rename columns
    df.rename(columns={'index': 'ID',
                       'Timestamp': 'Time',
                       'Email': 'Username',
                       'ACTION_VERB': 'Verb',
                       'OBJECT_TYPE': 'Object',
                       'Context': 'Path',
                       'OBJECT_NAME': 'Context'},
              inplace=True)

    return df


def convert_data_types(df: DataFrame) -> DataFrame:

    # set data types
    df['Time'] = df['Time'].astype('str')
    df['Username'] = df['Username'].astype('str')
    df['Affected_user'] = df['Affected_user'].astype('str')
    df['Event_context'] = df['Event_context'].astype('str')
    df['Component'] = df['Component'].astype('str')
    df['Event_name'] = df['Event_name'].astype('str')
    df['Description'] = df['Description'].astype('str')
    df['Origin'] = df['Origin'].astype('str')
    df['IP_address'] = df['IP_address'].astype('str')
    df['ID'] = df['ID'].astype('Int64')
    df['user_id'] = df['user_id'].astype('Int64').astype('str')
    df['course_id'] = df['course_id'].astype('Int64').astype('str')
    df['related_user_id'] = df['related_user_id'].astype('str')
    df['Unix_Time'] = df['Unix_Time'].astype('Int64')
    df['Course_Area'] = df['Course_Area'].astype('str')
    df['Year'] = df['Year'].astype('str').astype('Int64')
    df['Role'] = df['Role'].astype('str')

    return df


def make_timestamp_readable(df: DataFrame) -> DataFrame:

    df['Time'] = df.loc[:, 'Unix_Time'].map(lambda x: tm.convert_time_to_timestamp(x))

    return df
