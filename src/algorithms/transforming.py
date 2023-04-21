from pandas import DataFrame


def rename_columns(df: DataFrame) -> DataFrame:
    """
    Rename the fields of the extracted logs csv file. Modify the function according to your names.
    """

    # rename columns
    df.rename(columns={'index': 'ID',
                       'Email': 'Username',
                       'timestamp': 'Time',
                       'ACTION_VERB': 'Verb',
                       'OBJECT_NAME': 'Context',
                       'OBJECT_TYPE': 'Object',
                       'OBJECT_DESCRIPTION': 'Description',
                       'Context': 'Path'},
              inplace=True)

    return df


def convert_role(df: DataFrame) -> DataFrame:
    """
    Rename the role names according to your needs.
    """

    df.loc[df.Role == 'student role', 'Role'] = 'Student'
    df.loc[df.Role == 'editingteacher role', 'Role'] = 'Teacher'
    df.loc[df.Role == 'teacher role', 'Role'] = 'Non-editing Teacher'
    df.loc[df.Role == 'administratif role', 'Role'] = 'Administrative'

    return df
