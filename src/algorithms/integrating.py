import pandas as pd
from pandas import DataFrame
import src.algorithms.timing as tm


def get_dataframe(file_path: str, columns: [] = None) -> DataFrame:

    df = pd.read_csv(file_path, sep=',')

    # add column names if missing
    try:
        value_type = int(df.columns[0])
        if isinstance(value_type, int):
            df = pd.read_csv(file_path, sep=',', header=None)
            df.columns = columns
    except ValueError:
        pass

    return df


def add_course_id(df: DataFrame) -> DataFrame:
    items = df['RelatedActivities'].values

    courses = []
    for item in items:
        if "course/view.php" in item:
            course = item.split('/course/view.php?id=')[1].split("'")[0]
        else:
            course = str(0)
        courses.append(course)

    df['Course'] = courses

    return df


def add_timestamps(df: DataFrame) -> DataFrame:

    df['Unix_Time'] = df.loc[:, 'Time'].map(lambda x: tm.convert_time_to_timestamp(x))

    return df


def add_component(df: DataFrame) -> DataFrame:

    df['Component'] = [x.split('\\')[1] for x in df['Path']]

    return df


def add_event_name(df: DataFrame) -> DataFrame:

    df['Event_name'] = [x.split('event\\')[1] for x in df['Path']]

    return df


def course_area_categorisation(df: DataFrame) -> DataFrame:

    # authentication
    df.loc[df['Event_name'] == 'user_loggedin', 'Course_Area'] = 'Authentication'
    df.loc[df['Event_name'] == 'user_loggedout', 'Course_Area'] = 'Authentication'

    # overall site
    df.loc[df['Event_name'].str.contains('course_category'), 'Course_Area'] = 'Moodle Site'
    df.loc[df['Event_name'] == 'courses_searched', 'Course_Area'] = 'Moodle Site'
    df.loc[(df['Event_name'] == 'course_viewed') & (df['Course'] == 0), 'Course_Area'] = 'Moodle Site'
    # df.loc[df['Event context'] == 'Forum: Site announcements', 'Course_Area'] = 'Moodle Site'
    df.loc[df['Event_name'] == 'notification_viewed', 'Course_Area'] = 'Moodle Site'
    df.loc[(df['Event_name'] == 'user_report_viewed') &
           (df['Component'] == 'mod_forum'), 'Course_Area'] = 'Moodle Site'

    # profile
    df.loc[df['Event_name'].str.contains('dashboard'), 'Course_Area'] = 'Profile'
    df.loc[df['Event_name'] == 'user_password_updated', 'Course_Area'] = 'Profile'
    df.loc[df['Event_name'] == 'user_updated', 'Course_Area'] = 'Profile'
    df.loc[(df['Event_name'] == 'user_profile_viewed') & (df['Course'] == 0), 'Course_Area'] = 'Profile'
    df.loc[(df['Event_name'] == 'course_user_report_viewed') & (df['Course'] == 0), 'Course_Area'] = 'Profile'

    # social interaction
    df.loc[(df['Event_name'].str.contains('(?i)message')) &
           (df['Component'] != 'mod_chat'), 'Course'] = 'Social interaction'
    # df.loc[(df['Event name'] == 'Notification sent') &
    #        (df['Affected user'] != df['User full name']), 'Course'] = 'Social interaction'

    return df


def component_redefinition(df: DataFrame) -> DataFrame:

    # course activity completion updated
    ccu = list(df.loc[df['Event_name'] == 'course_module_completion_updated'].index)
    for idx in ccu:
        text = df.loc[idx, 'RelatedActivities'].split('/')
        df.loc[idx, 'Component'] = 'mod_' + text[text.index('mod') + 1]

    # assignment
    df.loc[df['Component'].str.contains('assignsubmission'), 'Component'] = 'Assignment'
    df.loc[(df['Component'] == 'mod_assign'), 'Component'] = 'Assignment'

    # attendance
    df.loc[(df['Component'] == 'mod_attendance'), 'Component'] = 'Attendance'

    # authentication
    df.loc[df['Event_name'] == 'user_loggedin', 'Component'] = 'Login'
    df.loc[df['Event_name'] == 'user_loggedout', 'Component'] = 'Logout'

    # big blue button
    df.loc[df['Component'] == 'mod_bigbluebuttonbn', 'Component'] = 'Big Blue Button'

    # book
    df.loc[df['Component'] == 'mod_book', 'Component'] = 'Book'
    df.loc[df['Component'] == 'booktool_print', 'Component'] = 'Book'

    # chat
    df.loc[df['Component'] == 'mod_chat', 'Component'] = 'Chat'

    # checklist
    df.loc[df['Component'] == 'mod_checklist', 'Component'] = 'Checklist'

    # choice
    df.loc[df['Component'] == 'mod_choice', 'Component'] = 'Choice'

    # course home
    df.loc[(df['Course'] != 0) & (df['Event_name'] == 'course_viewed'), 'Component'] = 'Course home'

    # courses list
    df.loc[df['Event_name'] == 'course_category_viewed', 'Component'] = 'Courses list'
    df.loc[df['Event_name'] == 'courses_searched', 'Component'] = 'Courses list'

    # dashboard
    df.loc[df['Event_name'].str.contains('dashboard'), 'Component'] = 'Dashboard'

    # database
    df.loc[df['Component'] == 'mod_data', 'Component'] = 'Database'

    # enrollment
    df.loc[df['Event_name'].str.contains('user_enrolment'), 'Component'] = 'Enrollment'

    # feedback
    df.loc[df['Component'] == 'mod_feedback', 'Component'] = 'Feedback'

    # file
    df.loc[df['Component'] == 'mod_resource', 'Component'] = 'File'

    # folder
    df.loc[df['Component'] == 'mod_folder', 'Component'] = 'Folder'

    # forum
    df.loc[df['Component'] == 'mod_forum', 'Component'] = 'Forum'

    # glossary
    df.loc[df['Component'] == 'mod_glossary', 'Component'] = 'Glossary'

    # grades
    df.loc[df['Event_name'] == 'grade_report_viewed', 'Component'] = 'Grades'
    df.loc[df['Event_name'] == 'course_user_report_viewed', 'Component'] = 'Grades'
    df.loc[df['Event_name'] == 'grade_item_updated', 'Component'] = 'Grades'
    df.loc[df['Event_name'] == 'grade_item_created', 'Component'] = 'Grades'

    # group choice
    df.loc[df['Component'] == 'mod_choicegroup', 'Component'] = 'Group choice'

    # groups
    df.loc[(df['Event_name'].str.contains('group|Grouping')) &
           (df['Event_name'] != 'group_message_sent'), 'Component'] = 'Groups'

    # h5p
    df.loc[df['Component'] == 'mod_h5pactivity', 'Component'] = 'H5P'

    # imscp
    df.loc[df['Component'] == 'mod_imscp', 'Component'] = 'IMS content package'

    # label
    df.loc[(df['Component'] == 'mod_label'), 'Component'] = 'Label'

    # lesson
    df.loc[(df['Component'] == 'mod_lesson'), 'Component'] = 'Lesson'

    # lti
    df.loc[(df['Component'] == 'mod_lti'), 'Component'] = 'External tool'

    # messaging
    df.loc[(df['Event_name'].str.contains('(?i)message')) & (df['Component'] != 'mod_chat'), 'Component'] = 'Messaging'

    # notification
    df.loc[df['Event_name'].str.contains('notification'), 'Component'] = 'Notification'

    # page
    df.loc[(df['Component'] == 'mod_page'), 'Component'] = 'Page'

    # questionnaire
    df.loc[(df['Component'] == 'mod_questionnaire'), 'Component'] = 'Questionnaire'

    # quiz
    # df.loc[(df['Event name'].str.contains('Question')) & (df['Component'] == 'System'), 'Component'] = 'Quiz'
    df.loc[(df['Component'] == 'mod_quiz'), 'Component'] = 'Quiz'

    # recent activity
    df.loc[df['Event_name'] == 'recent_activity_viewed', 'Component'] = 'Recent activity'

    # role
    df.loc[df['Event_name'].str.contains('role'), 'Component'] = 'Role'

    # scorm
    df.loc[(df['Component'] == 'mod_scorm'), 'Component'] = 'SCORM package'

    # site home
    df.loc[(df['Course'] == 0) | (df['Course'] == 1) & (df['Event_name'] == 'course_viewed'), 'Component'] = 'Site home'

    # url
    df.loc[(df['Component'] == 'mod_url'), 'Component'] = 'URL'

    # user profile
    df.loc[df['Event_name'] == 'user_list_viewed', 'Component'] = 'User profile'
    df.loc[df['Event_name'] == 'user_updated', 'Component'] = 'User profile'
    df.loc[df['Event_name'] == 'user_created', 'Component'] = 'User profile'
    df.loc[df['Event_name'] == 'User profile viewed'] = 'User profile'

    # wiki
    df.loc[(df['Component'] == 'mod_wiki'), 'Component'] = 'Wiki'

    # wooclap
    df.loc[(df['Component'] == 'mod_wooclap'), 'Component'] = 'Wooclap'

    return df


def event_name_redefinition(df: DataFrame):

    # the complete list of events is available on AMOS translator (https://lang.moodle.org/local/amos/view.php)
    # by simple removing underscore: as an example 'assessable_submitted' -> 'assessablesubmitted'
    # this list can be modified according to your needs.

    # assignment
    df.loc[(df['Event_name'] == 'assessable_submitted'), 'Event_name'] = 'A submission has been submitted.'

    # course
    df.loc[(df['Event_name'] == 'course_viewed'), 'Event_name'] = 'Course viewed'

    # enrollment
    df.loc[(df['Event_name'] == 'user_enrolment_created'), 'Event_name'] = 'User enrolled in course'

    # login
    df.loc[(df['Event_name'] == 'user_loggedin'), 'Event_name'] = 'User has logged in'
    df.loc[(df['Event_name'] == 'user_loggedout'), 'Event_name'] = 'User logged out'

    # module
    df.loc[(df['Event_name'] == 'course_module_viewed'), 'Event_name'] = 'Course module viewed'

    # quiz
    df.loc[(df['Event_name'] == 'attempt_viewed'), 'Event_name'] = 'Quiz attempt viewed'
    df.loc[(df['Event_name'] == 'attempt_reviewed'), 'Event_name'] = 'Quiz attempt reviewed'
    df.loc[(df['Event_name'] == 'attempt_submitted'), 'Event_name'] = 'Quiz attempt submitted'

    return df
