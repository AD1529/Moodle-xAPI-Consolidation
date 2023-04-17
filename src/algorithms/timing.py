from datetime import datetime


def convert_time_to_timestamp(date: str) -> int:
    """
    This function creates a datetime object from the given string and convert it in a timestamp. This function can
    be customised according to your date format.

    Args:
        date: the string of the date

    Returns: the corresponding time stamp.

    """

    # date is converted in a date and time string format
    date_to_string = datetime.strptime(date, "%Y-%m-%dT%X%z")
    # date and time string format is converted in unix timestamp
    time_to_timestamp = int(datetime.timestamp(date_to_string))

    return time_to_timestamp
