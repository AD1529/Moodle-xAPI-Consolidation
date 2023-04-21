from pandas import DataFrame


def sort_data(df: DataFrame) -> DataFrame:
    """
    Sort values based on the given fields. This function first verifies that logs are accessible from earliest to
    newest.  Due to the fact that a number of functions rely on the sequence of logs, it is crucial that the sequence
    be in the correct order to prevent biased results.
    """

    max_time = df.Unix_Time.iloc[-1]
    min_time = df.Unix_Time.iloc[0]
    if max_time < min_time:
        df = df[::-1].copy()
        df = df.reset_index(drop=True)
        df['ID'] = df.index

    df = df.sort_values(by=['Unix_Time', 'ID'])
    df = df.reset_index(drop=True)
    df['ID'] = df.index

    df.sort_values(by=['Username', 'ID'])
    df = df.reset_index(drop=True)
    df['ID'] = df.index

    return df
