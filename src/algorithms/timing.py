from datetime import datetime


def convert_time_to_timestamp(dt: str) -> int:
    """
    Create a datetime object from the given string and convert it in a timestamp. This function should
    be customised according to your datetime format.

    Args:
        dt: the string of the datetime

    Returns: the corresponding timestamp.

    """

    # date is converted in a date and time string format
    date_to_string = datetime.strptime(dt, "%Y-%m-%d %X%z")
    # date and time string format is converted in unix timestamp
    time_to_timestamp = int(datetime.timestamp(date_to_string))

    return time_to_timestamp
