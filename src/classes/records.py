from pandas import DataFrame, Series


class Records(object):
    """
    The dataframe of the Records object has the following fields:
    'ID', 'Time', 'Username', 'Role', 'Course_Area', 'Component', 'Event_name', 'Year', 'Unix_Time'
    """

    def __init__(self, df):
        self.__df = df

    def get_df(self) -> DataFrame:
        """
        Return the dataframe
        """
        return self.__df

    def get_column_names(self) -> []:
        """
        Return the dataframe column names
        """
        column_names = list(self.__df.columns)

        return column_names

    def get_ids(self) -> []:
        """
        Return a sorted list of record ids
        """
        ids = sorted(self.__df.ID)

        return ids

    def get_times(self) -> []:
        """
        Return a list of record times
        """
        ids = self.__df.Time.unique()

        return ids

    def get_usernames(self) -> []:
        """
        Return a sorted list of record usernames
        """
        usernames = sorted(self.__df.Username.unique())

        return usernames

    def get_roles(self) -> []:
        """
        Return a list of record roles
        """
        roles = sorted(self.__df.Role.unique())

        return roles

    def get_courses_areas(self) -> []:
        """
        Return the sorted list of the dataframe courses and areas
        """
        courses_and_areas = sorted(self.__df.Course_Area.unique())

        return courses_and_areas

    def get_components(self) -> []:
        """
        Return a sorted list of (role-filtered) record components
        """
        components = sorted(self.__df.Component.unique())

        return components

    def get_event_names(self) -> Series:
        """
        Return the series by component of the sorted list of all the event names
        """
        event_names = self.__df.sort_values('Event_name', ascending=True).groupby('Component')['Event_name'].unique()

        return event_names

    def get_years(self) -> []:
        """
        Return a list of record years
        """
        years = sorted(self.__df.Year.unique())

        return years
