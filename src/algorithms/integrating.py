import pandas as pd
from pandas import DataFrame
import numpy as np
import src.algorithms.timing as tm
import src.algorithms.transforming as tr
import glob


def collect_log_files(directory_path: str) -> DataFrame:
    """
    It is possible to have a number of course files instead of a single one.
    The selected directory must contain all related files.

    Args:
        directory_path: The path of the directory that contains all the files.

    Returns: The dataframe containing the logs of the all the course files inserted in the directory.
    """

    logs = pd.DataFrame()

    for file_path in glob.glob(directory_path + '*.csv'):
        # get the log data of the file
        file_logs = get_dataframe(file_path)
        # concatenate the file logs to all the logs
        logs = pd.concat([logs, file_logs], axis=0)

    # reset the index
    logs = logs.reset_index(drop=True)

    return logs


def get_dataframe(file_path: str, columns: [] = None) -> DataFrame:
    """
    Read the dataframe and add columns if missing.

    Args:
        file_path: The path of the dataframe object.
        columns: The list of column names.

    Returns:
        The dataframe with column names.
    """

    df = pd.read_csv(file_path, sep=',')

    # add column names if missing
    try:
        value_type = int(df.columns[0])
        if isinstance(value_type, int):
            df = pd.read_csv(file_path, sep=',', header=None)
            df.columns = columns
    except ValueError:
        pass

    # create the index in case is missing
    df.reset_index(inplace=True)

    return df


def add_course_id(df: DataFrame) -> DataFrame:
    """
    Add the course id by extracting it from the RelatedActivities field.
    """

    items = df['RelatedActivities'].values

    ids = []
    for item in items:
        if "course/view.php" in item:
            courseid = item.split('/course/view.php?id=')[1].split("'")[0]
        else:
            courseid = str(0)
        ids.append(courseid)

    df['courseid'] = ids

    # set data type
    df['courseid'] = df['courseid'].astype('Int64')

    return df


def add_course_name(df: DataFrame, course_names: str) -> DataFrame:
    """
    Add the name of the course based on the courseid and name listed in the course_names file. Please be aware
    that actions performed in courses not listed in the file will be removed during cleaning.
    If you only know the course id of the course, you can retrieve the course name by running the command:
    courses_names = df.loc[df.Path.str.contains('course_viewed')][['courseid', 'Context']].drop_duplicates()

    Args:
        df: The dataframe object.
        course_names: The path of the course names file.

    Returns:
        The dataframe with the field course name.

    """

    # get data
    course_names = get_dataframe(course_names, columns=['id', 'coursename'])
    # set data type
    course_names['id'] = course_names['id'].astype('Int64')
    course_names['coursename'] = course_names['coursename'].astype('str')
    names = course_names['coursename']

    for name in names:
        courseid = course_names.loc[course_names['coursename'] == name]['id'].values[0]
        df.loc[df['courseid'] == courseid, 'Course_Area'] = name

    return df


def add_timestamps(df: DataFrame) -> DataFrame:
    """
    Add the column 'Unix_Time' to the dataframe containing the converted value of the time in a timestamp so that it
    can be used by other functions.
    """

    df['Unix_Time'] = df.loc[:, 'Time'].map(lambda x: tm.convert_time_to_timestamp(x))

    return df


def add_component(df: DataFrame) -> DataFrame:
    """
    Add the component field to the dataframe.
    """

    df['Component'] = [x.split('\\')[1] for x in df['Path']]

    return df


def add_event_name(df: DataFrame) -> DataFrame:
    """
    Add the event_name field to the dataframe.
    """

    df['Event_name'] = [x.split('event\\')[1] for x in df['Path']]

    return df


def redefine_course_area(df: DataFrame) -> DataFrame:
    """
    Add the Course_Area field to those records that identify actions performed in the site outside a course and that
    miss a value.
    """

    # authentication
    df.loc[df['Event_name'] == 'user_loggedin', 'Course_Area'] = 'Authentication'
    df.loc[df['Event_name'] == 'user_loggedout', 'Course_Area'] = 'Authentication'

    # overall site
    df.loc[(df['Event_name'] == 'course_viewed') & (df['courseid'] == 1), 'Course_Area'] = 'Moodle Site'
    df.loc[(df['Event_name'] == 'user_created'), 'Course_Area'] = 'Moodle Site'
    df.loc[(df['Event_name'] == 'user_deleted'), 'Course_Area'] = 'Moodle Site'
    df.loc[(df['Event_name'] == 'role_updated'), 'Course_Area'] = 'Moodle Site'
    df.loc[(df['Event_name'] == 'role_assigned') & (df['courseid'] == 1), 'Course_Area'] = 'Moodle Site'
    df.loc[(df['Event_name'] == 'role_unassigned') & (df['courseid'] == 1), 'Course_Area'] = 'Moodle Site'
    df.loc[(df['Event_name'] == 'user_enrolment_deleted') & (df['courseid'] == 1), 'Course_Area'] = 'Moodle Site'
    df.loc[(df['Event_name'] == 'user_enrolment_updated') & (df['courseid'] == 1), 'Course_Area'] = 'Moodle Site'
    df.loc[df['Event_name'].str.contains('course_category'), 'Course_Area'] = 'Moodle Site'
    df.loc[df['Event_name'] == 'courses_searched', 'Course_Area'] = 'Moodle Site'
    df.loc[df['Event_name'].str.contains('notification'), 'Course_Area'] = 'Moodle Site'
    df.loc[(df['Event_name'] == 'user_report_viewed') &
           (df['Component'] == 'mod_forum') & (df['courseid'] == 0), 'Course_Area'] = 'Moodle Site'

    # profile
    df.loc[df['Event_name'].str.contains('dashboard'), 'Course_Area'] = 'Profile'
    df.loc[(df['Event_name'] == 'user_profile_viewed') & (df['courseid'] == 0), 'Course_Area'] = 'Profile'
    df.loc[(df['Event_name'] == 'grade_report_viewed') & (df['courseid'] == 0), 'Course_Area'] = 'Profile'
    df.loc[df['Event_name'] == 'user_password_updated', 'Course_Area'] = 'Profile'
    df.loc[df['Event_name'] == 'user_updated', 'Course_Area'] = 'Profile'

    # social interaction
    df.loc[(df['Event_name'].str.contains('(?i)message')) &
           (df['Component'] != 'mod_chat'), 'Course_Area'] = 'Social interaction'

    return df


def redefine_component(df: DataFrame) -> DataFrame:
    """
    The component field can be labelled with the 'System' value even though the log is clearly generated when the user
    is performing an action on a specific module. Sometimes some records are recorded on different components even
    though they are related to the same component. This function redefines the component field.

    """

    # course activity completion updated
    ccu = list(df.loc[df['Event_name'] == 'course_module_completion_updated'].index)
    for idx in ccu:
        text = df.loc[idx, 'RelatedActivities'].split('/')
        df.loc[idx, 'Component'] = 'mod_' + text[text.index('mod') + 1]

    df.loc[df['Component'].str.contains('https'), 'Component'] = 'DELETE'

    # assignment
    df.loc[df['Component'] == 'assignsubmission_file', 'Component'] = 'File submissions'
    df.loc[df['Component'] == 'assignsubmission_onlinetext', 'Component'] = 'Online text submissions'
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
    df.loc[(df['courseid'] != 0) & (df['Event_name'] == 'course_viewed'), 'Component'] = 'Course home'

    # courses list
    df.loc[df['Event_name'] == 'course_category_viewed', 'Component'] = 'Courses list'
    df.loc[df['Event_name'] == 'courses_searched', 'Component'] = 'Courses list'

    # dashboard
    df.loc[df['Event_name'].str.contains('dashboard'), 'Component'] = 'Dashboard'

    # database
    df.loc[df['Component'] == 'mod_data', 'Component'] = 'Database'

    # enrollment
    df.loc[df['Event_name'].str.contains('user_enrolment'), 'Component'] = 'Enrolment'

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
    df.loc[df['Event_name'] == 'group_member_added', 'Component'] = 'Groups'
    df.loc[df['Event_name'] == 'group_member_removed', 'Component'] = 'Groups'
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
    df.loc[(df['Event_name'].str.contains('Question')) & (df['Component'] == 'core'), 'Component'] = 'Quiz'
    df.loc[(df['Component'] == 'mod_quiz'), 'Component'] = 'Quiz'

    # recent activity
    df.loc[df['Event_name'] == 'recent_activity_viewed', 'Component'] = 'Recent activity'

    # role
    df.loc[df['Event_name'].str.contains('role'), 'Component'] = 'Role'

    # scorm
    df.loc[(df['Component'] == 'mod_scorm'), 'Component'] = 'SCORM package'

    # site home
    df.loc[(df['courseid'] == 1) & (df['Event_name'] == 'course_viewed'), 'Component'] = 'Site home'

    # system
    df.loc[df['Event_name'] == 'user_created', 'Component'] = 'System'

    # url
    df.loc[(df['Component'] == 'mod_url'), 'Component'] = 'URL'

    # user profile
    df.loc[df['Event_name'] == 'user_list_viewed', 'Component'] = 'Profile'
    df.loc[df['Event_name'] == 'user_updated', 'Component'] = 'User profile'
    df.loc[df['Event_name'] == 'user_profile_viewed', 'Component'] = 'User profile'

    # wiki
    df.loc[(df['Component'] == 'mod_wiki'), 'Component'] = 'Wiki'

    # wooclap
    df.loc[(df['Component'] == 'mod_wooclap'), 'Component'] = 'Wooclap'

    return df


def redefine_event_name(df: DataFrame) -> DataFrame:
    """
    Transform the path extracted from the statement.extension in the extended readable format. This function can be
    modified according to your needs. The complete list of events is available on https://yoursite/report/eventlist/index.php

    """

    # assignment
    df.loc[(df['Event_name'] == 'assessable_submitted'), 'Event_name'] = 'A submission has been submitted.'
    df.loc[(df['Event_name'] == 'feedback_viewed'), 'Event_name'] = 'Feedback viewed'
    df.loc[(df['Event_name'] ==
            'remove_submission_form_viewed'), 'Event_name'] = 'Remove submission confirmation viewed.'
    df.loc[(df['Event_name'] ==
            'submission_confirmation_form_viewed'), 'Event_name'] = 'Submission confirmation form viewed.'
    df.loc[(df['Event_name'] == 'submission_duplicated'), 'Event_name'] = 'The user duplicated their submission.'
    df.loc[(df['Event_name'] == 'submission_form_viewed'), 'Event_name'] = 'Submission form viewed.'
    df.loc[(df['Event_name'] == 'submission_graded'), 'Event_name'] = 'The submission has been graded.'
    df.loc[(df['Event_name'] ==
            'submission_status_viewed'), 'Event_name'] = 'The status of the submission has been viewed.'
    df.loc[(df['Event_name'] == 'assessable_uploaded') &
           (df['Component'] == 'File submissions'), 'Event_name'] = 'A file has been uploaded.'
    df.loc[(df['Event_name'] == 'assessable_uploaded') &
           (df['Component'] == 'Online text submissions'), 'Event_name'] = 'An online text has been uploaded.'
    df.loc[(df['Event_name'] == 'submission_viewed') &
           (df.Component == 'Assignment'), 'Event_name'] = 'Submission viewed.'
    df.loc[df['Component'] == 'File submissions', 'Component'] = 'Assignment'
    df.loc[df['Component'] == 'Online text submissions', 'Component'] = 'Assignment'
    df.loc[(df['Event_name'] == 'submission_created') &
           (df.Component == 'Assignment'), 'Event_name'] = 'Submission created.'
    df.loc[(df['Event_name'] == 'submission_updated') &
           (df.Component == 'Assignment'), 'Event_name'] = 'Submission updated.'

    # attendance
    df.loc[(df['Event_name'] == 'attendance_taken_by_student'), 'Event_name'] = 'Attendance taken by student'
    df.loc[(df['Event_name'] == 'session_report_viewed'), 'Event_name'] = 'Session report viewed'

    # big blue button
    df.loc[(df['Event_name'] == 'activity_viewed'), 'Event_name'] = 'Activity viewed'
    df.loc[(df['Event_name'] == 'bigbluebuttonbn_activity_management_viewed'), 'Event_name'] \
        = 'BigBlueButtonBN activity management viewed'
    df.loc[(df['Event_name'] == 'live_session_event'), 'Event_name'] = 'Live session event'
    df.loc[(df['Event_name'] == 'meeting_created'), 'Event_name'] = 'Meeting created'
    df.loc[(df['Event_name'] == 'meeting_ended'), 'Event_name'] = 'Meeting ended'
    df.loc[(df['Event_name'] == 'meeting_joined'), 'Event_name'] = 'Meeting joined'
    df.loc[(df['Event_name'] == 'meeting_left'), 'Event_name'] = 'Meeting left'
    df.loc[(df['Event_name'] == 'recording_deleted'), 'Event_name'] = 'Recording deleted'
    df.loc[(df['Event_name'] == 'recording_edited'), 'Event_name'] = 'Recording edited'
    df.loc[(df['Event_name'] == 'recording_imported'), 'Event_name'] = 'Recording imported'
    df.loc[(df['Event_name'] == 'recording_protected'), 'Event_name'] = 'Recording protected'
    df.loc[(df['Event_name'] == 'recording_published'), 'Event_name'] = 'Recording published'
    df.loc[(df['Event_name'] == 'recording_unprotected'), 'Event_name'] = 'Recording unprotected'
    df.loc[(df['Event_name'] == 'recording_unpublished'), 'Event_name'] = 'Recording unpublished'
    df.loc[(df['Event_name'] == 'recording_viewed'), 'Event_name'] = 'Recording viewed'

    # book
    df.loc[(df['Event_name'] == 'book_printed'), 'Event_name'] = 'Book printed'
    df.loc[(df['Event_name'] == 'chapter_viewed'), 'Event_name'] = 'Chapter viewed'
    df.loc[(df['Event_name'] == 'chapter_printed'), 'Event_name'] = 'Chapter printed'

    # category
    df.loc[(df['Event_name'] == 'course_category_viewed'), 'Event_name'] = 'Category viewed'
    df.loc[(df['Event_name'] == 'search_results_viewed'), 'Event_name'] = 'Search results viewed'

    # chat
    df.loc[(df['Event_name'] == 'sessions_viewed'), 'Event_name'] = 'Sessions viewed'

    # checklist
    df.loc[(df['Event_name'] == 'checklist_completed'), 'Event_name'] = 'Checklist complete'
    df.loc[(df['Event_name'] == 'student_checks_updated'), 'Event_name'] = 'Student checks updated'

    # choice
    df.loc[(df['Event_name'] == 'answer_created'), 'Event_name'] = 'Choice answer added'
    df.loc[(df['Event_name'] == 'answer_deleted'), 'Event_name'] = 'Choice answer deleted'

    # comment
    df.loc[(df['Event_name'] == 'comment_created'), 'Event_name'] = 'Comment created'
    df.loc[(df['Event_name'] == 'comment_deleted'), 'Event_name'] = 'Comment deleted'

    # course
    df.loc[(df['Event_name'] == 'course_viewed'), 'Event_name'] = 'Course viewed'
    df.loc[(df['Event_name'] == 'course_completed'), 'Event_name'] = 'Course completed'
    df.loc[(df['Event_name'] == 'course_information_viewed'), 'Event_name'] = 'Course summary viewed'
    df.loc[(df['Event_name'] == 'course_module_completion_updated'), 'Event_name'] = 'Course activity completion updated'
    df.loc[(df['Event_name'] == 'course_resources_list_viewed'), 'Event_name'] = 'Course module instance list viewed'
    df.loc[(df['Event_name'] == 'courses_searched'), 'Event_name'] = 'Courses searched'
    df.loc[(df['Event_name'] == 'course_user_report_viewed'), 'Event_name'] = 'Course user report viewed'
    df.loc[(df['Event_name'] == 'course_module_instance_list_viewed'), 'Event_name'] = 'Course module instance list viewed'
    df.loc[(df['Event_name'] == 'course_module_viewed'), 'Event_name'] = 'Course module viewed'

    # dashboard
    df.loc[(df['Event_name'] == 'dashboard_reset'), 'Event_name'] = 'Dashboard reset'
    df.loc[(df['Event_name'] == 'dashboard_viewed'), 'Event_name'] = 'Dashboard viewed'

    # database
    df.loc[(df['Event_name'] == 'record_created'), 'Event_name'] = 'Record created'
    df.loc[(df['Event_name'] == 'record_deleted'), 'Event_name'] = 'Record deleted'
    df.loc[(df['Event_name'] == 'record_updated'), 'Event_name'] = 'Record updated'

    # enrollment
    df.loc[(df['Event_name'] == 'user_enrolment_created'), 'Event_name'] = 'User enrolled in course'
    df.loc[(df['Event_name'] == 'user_enrolment_deleted'), 'Event_name'] = 'User unenrolled from course'
    df.loc[(df['Event_name'] == 'user_enrolment_updated'), 'Event_name'] = 'User enrolment updated'

    # feedback
    df.loc[(df['Event_name'] == 'response_deleted'), 'Event_name'] = 'Response deleted'
    df.loc[(df['Event_name'] == 'response_submitted') &
           (df['Component'] == 'Feedback'), 'Event_name'] = 'Response submitted'

    # folder
    df.loc[(df['Event_name'] == 'all_files_downloaded'), 'Event_name'] = 'Zip archive of folder downloaded'

    # forum
    df.loc[(df['Event_name'] == 'assessable_uploaded') &
           (df['Component'] == 'Forum'), 'Event_name'] = 'Some content has been posted.'
    df.loc[(df['Event_name'] == 'course_searched'), 'Event_name'] = 'Course searched'
    df.loc[(df['Event_name'] == 'discussion_created'), 'Event_name'] = 'Discussion created'
    df.loc[(df['Event_name'] == 'discussion_deleted'), 'Event_name'] = 'Discussion deleted'
    df.loc[(df['Event_name'] == 'discussion_subscription_created'), 'Event_name'] = 'Discussion subscription created'
    df.loc[(df['Event_name'] == 'discussion_subscription_deleted'), 'Event_name'] = 'Discussion subscription deleted'
    df.loc[(df['Event_name'] == 'discussion_deleted'), 'Event_name'] = 'Discussion deleted'
    df.loc[(df['Event_name'] == 'discussion_viewed'), 'Event_name'] = 'Discussion viewed'
    df.loc[(df['Event_name'] == 'post_created'), 'Event_name'] = 'Post created'
    df.loc[(df['Event_name'] == 'post_deleted'), 'Event_name'] = 'Post deleted'
    df.loc[(df['Event_name'] == 'post_updated'), 'Event_name'] = 'Post updated'
    df.loc[(df['Event_name'] == 'readtracking_disabled'), 'Event_name'] = 'Read tracking disabled'
    df.loc[(df['Event_name'] == 'readtracking_enabled'), 'Event_name'] = 'Read tracking enabled'
    df.loc[(df['Event_name'] == 'subscription_created'), 'Event_name'] = 'Subscription created'
    df.loc[(df['Event_name'] == 'subscription_deleted'), 'Event_name'] = 'Subscription deleted'
    df.loc[(df['Event_name'] == 'user_report_viewed'), 'Event_name'] = 'User report viewed'

    # glossary
    df.loc[(df['Event_name'] == 'entry_created'), 'Event_name'] = 'Entry has been created'
    df.loc[(df['Event_name'] == 'entry_deleted'), 'Event_name'] = 'Entry has been deleted'
    df.loc[(df['Event_name'] == 'entry_updated'), 'Event_name'] = 'Entry has been updated'
    df.loc[(df['Event_name'] == 'entry_viewed'), 'Event_name'] = 'Entry has been viewed'

    # grade
    df.loc[(df['Event_name'] == 'grade_item_created'), 'Event_name'] = 'Grade item created'
    df.loc[(df['Event_name'] == 'grade_item_updated'), 'Event_name'] = 'Grade item updated'
    df.loc[(df['Event_name'] == 'grade_report_viewed') &
           (df.courseid == 0), 'Event_name'] = 'Grade overview report viewed'
    df.loc[(df['Event_name'] == 'grade_report_viewed') &
           (df.courseid != 0), 'Event_name'] = 'Grade user report viewed'

    # group
    df.loc[(df['Event_name'] == 'group_member_added'), 'Event_name'] = 'Group member added'
    df.loc[(df['Event_name'] == 'group_member_removed'), 'Event_name'] = 'Group member removed'

    # group choice
    df.loc[(df['Event_name'] == 'choice_removed'), 'Event_name'] = 'Choice removed'
    df.loc[(df['Event_name'] == 'choice_updated'), 'Event_name'] = 'Choice made'

    # h5p
    df.loc[(df['Event_name'] == 'report_viewed'), 'Event_name'] = 'Report viewed'
    df.loc[(df['Event_name'] == 'statement_received'), 'Event_name'] = 'xAPI statement received'

    # lesson
    df.loc[(df['Event_name'] == 'content_page_viewed'), 'Event_name'] = 'Content page viewed'
    df.loc[(df['Event_name'] == 'lesson_ended'), 'Event_name'] = 'Lesson ended'
    df.loc[(df['Event_name'] == 'lesson_restarted'), 'Event_name'] = 'Lesson restarted'
    df.loc[(df['Event_name'] == 'lesson_resumed'), 'Event_name'] = 'Lesson resumed'
    df.loc[(df['Event_name'] == 'lesson_started'), 'Event_name'] = 'Lesson started'
    df.loc[(df['Event_name'] == 'question_answered'), 'Event_name'] = 'Question answered'
    df.loc[(df['Event_name'] == 'question_viewed'), 'Event_name'] = 'Question viewed'

    # login
    df.loc[(df['Event_name'] == 'user_loggedin'), 'Event_name'] = 'User has logged in'
    df.loc[(df['Event_name'] == 'user_loggedout'), 'Event_name'] = 'User logged out'

    # message
    df.loc[(df['Event_name'] == 'group_message_sent'), 'Event_name'] = 'Group message sent'
    df.loc[(df['Event_name'] == 'message_sent'), 'Event_name'] = 'Message sent'
    df.loc[(df['Event_name'] == 'message_deleted'), 'Event_name'] = 'Message deleted'
    df.loc[(df['Event_name'] == 'message_viewed'), 'Event_name'] = 'Message viewed'

    # module
    df.loc[(df['Event_name'] == 'course_module_viewed'), 'Event_name'] = 'Course module viewed'

    # notification
    df.loc[(df['Event_name'] == 'notification_sent'), 'Event_name'] = 'Notification sent'
    df.loc[(df['Event_name'] == 'notification_viewed'), 'Event_name'] = 'Notification viewed'

    # profile
    df.loc[(df['Event_name'] == 'user_profile_viewed'), 'Event_name'] = 'User profile viewed'
    df.loc[(df['Event_name'] == 'user_updated'), 'Event_name'] = 'User updated'

    # questionnaire
    df.loc[(df['Event_name'] == 'all_responses_viewed'), 'Event_name'] = 'All Responses report viewed'
    df.loc[(df['Event_name'] == 'attempt_resumed'), 'Event_name'] = 'Attempt resumed'
    df.loc[(df['Event_name'] == 'attempt_saved'), 'Event_name'] = 'Responses saved'
    df.loc[(df['Event_name'] == 'attempt_submitted') &
           (df.Component == 'Questionnaire'), 'Event_name'] = 'Responses submitted'
    df.loc[(df['Event_name'] == 'response_viewed'), 'Event_name'] = 'Individual Responses report viewed'

    # quiz
    df.loc[(df['Event_name'] == 'attempt_abandoned'), 'Event_name'] = 'Quiz attempt abandoned'
    df.loc[(df['Event_name'] == 'attempt_reviewed'), 'Event_name'] = 'Quiz attempt reviewed'
    df.loc[(df['Event_name'] == 'attempt_started'), 'Event_name'] = 'Quiz attempt started'
    df.loc[(df['Event_name'] == 'attempt_submitted') &
           (df.Component == 'Quiz'), 'Event_name'] = 'Quiz attempt submitted'
    df.loc[(df['Event_name'] == 'attempt_summary_viewed'), 'Event_name'] = 'Quiz attempt summary viewed'
    df.loc[(df['Event_name'] == 'attempt_viewed'), 'Event_name'] = 'Quiz attempt viewed'

    # recent activity
    df.loc[(df['Event_name'] == 'recent_activity_viewed'), 'Event_name'] = 'Recent activity viewed'

    # role
    df.loc[(df['Event_name'] == 'role_assigned'), 'Event_name'] = 'Role assigned'
    df.loc[(df['Event_name'] == 'role_unassigned'), 'Event_name'] = 'Role unassigned'
    df.loc[(df['Event_name'] == 'role_updated'), 'Event_name'] = 'Role updated'

    # scheduler
    df.loc[(df['Event_name'] == 'booking_added'), 'Event_name'] = 'Scheduler booking added'
    df.loc[(df['Event_name'] == 'booking_form_viewed'), 'Event_name'] = 'Scheduler booking form viewed'
    df.loc[(df['Event_name'] == 'booking_removed'), 'Event_name'] = 'Scheduler booking removed'

    # scorm
    df.loc[(df['Event_name'] == 'sco_launched'), 'Event_name'] = 'Sco launched'
    df.loc[(df['Event_name'] == 'scoreraw_submitted'), 'Event_name'] = 'Submitted SCORM raw score'
    df.loc[(df['Event_name'] == 'status_submitted'), 'Event_name'] = 'Submitted SCORM status'

    # survey
    df.loc[(df['Event_name'] == 'response_submitted') &
           (df['Component'] == 'Survey'), 'Event_name'] = 'Survey response submitted'

    # tour
    df.loc[(df['Event_name'] == 'tour_ended'), 'Event_name'] = 'Tour ended'
    df.loc[(df['Event_name'] == 'tour_started'), 'Event_name'] = 'Tour started'

    # user
    df.loc[(df['Event_name'] == 'user_created'), 'Event_name'] = 'User created'
    df.loc[(df['Event_name'] == 'user_deleted'), 'Event_name'] = 'User deleted'
    df.loc[(df['Event_name'] == 'user_list_viewed'), 'Event_name'] = 'User list viewed'

    # wiki
    df.loc[(df['Event_name'] == 'comments_viewed') & (df['Component'] == 'Wiki'), 'Event_name'] = 'Comments viewed'
    df.loc[(df['Event_name'] == 'page_created'), 'Event_name'] = 'Wiki page created'
    df.loc[(df['Event_name'] == 'page_deleted'), 'Event_name'] = 'Wiki page deleted'
    df.loc[(df['Event_name'] == 'page_diff_viewed'), 'Event_name'] = 'Wiki diff viewed'
    df.loc[(df['Event_name'] == 'page_history_viewed'), 'Event_name'] = 'Wiki history viewed'
    df.loc[(df['Event_name'] == 'page_map_viewed'), 'Event_name'] = 'Wiki page map viewed'
    df.loc[(df['Event_name'] == 'page_updated'), 'Event_name'] = 'Wiki page updated'
    df.loc[(df['Event_name'] == 'page_version_deleted'), 'Event_name'] = 'Wiki page version deleted'
    df.loc[(df['Event_name'] == 'page_version_restored'), 'Event_name'] = 'Wiki page version restored'
    df.loc[(df['Event_name'] == 'page_version_viewed'), 'Event_name'] = 'Wiki page version viewed'
    df.loc[(df['Event_name'] == 'page_viewed'), 'Event_name'] = 'Wiki page viewed'

    # workshop
    df.loc[(df['Event_name'] == 'assessable_uploaded') &
           (df['Component'] == 'Workshop'), 'Event_name'] = 'A submission has been uploaded.'
    df.loc[(df['Event_name'] == 'submission_assessed'), 'Event_name'] = 'Submission assessed'
    df.loc[(df['Event_name'] == 'submission_created') &
           (df.Component == 'Workshop'), 'Event_name'] = 'Submission created'
    df.loc[(df['Event_name'] == 'submission_deleted'), 'Event_name'] = 'Submission deleted'
    df.loc[(df['Event_name'] == 'submission_reassessed'), 'Event_name'] = 'Submission re-assessed'
    df.loc[(df['Event_name'] == 'submission_updated') &
           (df.Component == 'Workshop'), 'Event_name'] = 'Submission updated'
    df.loc[(df['Event_name'] == 'submission_viewed') &
           (df.Component == 'Workshop'), 'Event_name'] = 'Submission viewed'

    return df


def add_role(df: DataFrame) -> DataFrame:
    """
    A role is a collection of permissions defined for the whole system that can be assigned to specific users in
    specific contexts. When a user logs in, they are considered "authenticated." Users can be teachers or students
    only within a course. A user can have multiple roles, representing as both a teacher and a student in different
    courses. The complete list of roles is available at the page: your_moodle_site/admin/roles/manage.php. This
    function can be extended according to specific requirements.

    Please be aware that any system roles (suche as admin, manager, course-creator, or specifically created role) apply
    to the assigned users throughout the entire system, including the front page and all the courses. A user can be a
    teacher in a course and a student in another course. A manager can only be a manager.
    """

    df["Role"] = np.nan

    courseids = df.loc[df.Course_Area.notnull()]['courseid'].unique()
    for courseid in courseids:
        if courseid != 0 and courseid != 1:
            roles = df.loc[df.courseid == courseid].loc[df.Component == 'Role']
            role_list = {}
            for idx in range(len(roles)):
                key = roles.iloc[idx]['Username']
                role = roles.iloc[idx]['Context']
                verb = roles.iloc[idx]['Verb']
                role_list.setdefault(key, [])
                if verb == 'has been assigned' and role not in role_list[key]:
                    role_list[key].append(role)
                if verb == 'has been unassigned' and role in role_list[key]:
                    role_list[key].remove(role)

            for item in role_list.items():
                user_logs = list((df.loc[df.Username == item[0]].loc[df.courseid == courseid]).index)
                for user_log in user_logs:
                    role = item[1]
                    if not role:
                        df.iat[user_log, df.columns.get_loc('Role')] = 'Guest'
                    else:
                        if len(role) == 1:
                            df.iat[user_log, df.columns.get_loc('Role')] = role[0]
                        else:
                            df.iat[user_log, df.columns.get_loc('Role')] = role

            usernames = df.loc[df.courseid == courseid].Username.unique()
            for username in usernames:
                if username not in role_list.keys():
                    df.loc[(df.Username == username) & (df.courseid == courseid), 'Role'] = 'Guest'

        df.loc[df['Role'].isnull(), 'Role'] = 'Authenticated user'

    # how to find multiple roles
    # df[df["Role"].apply(lambda d: isinstance(d, list))]

    df = tr.convert_role(df)

    return df


def add_status(df: DataFrame) -> DataFrame:
    """
    Identify actions performed on deleted modules or deleted users

    Returns two values: DELETED or Available.
    """

    df.loc[(df.Context == 'not available') | (df.Description == 'deleted'), 'Status'] = 'DELETED'

    df.loc[df['Status'].isnull(), 'Status'] = 'Available'

    return df
