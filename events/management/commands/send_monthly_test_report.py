from __future__ import unicode_literals
import csv
import logging
import os
from datetime import date, timedelta
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from events.models import StudentMaster


class Command(BaseCommand):

    help = 'Generate and email previous month Gujarat test report.'
    def handle(self, *args, **options):
        # 1. GET CONFIGURATION FROM SETTINGS
        recipient = getattr(settings,'MONTHLY_TEST_REPORT_RECIPIENT',None)
        cc_recipients = getattr(settings,'MONTHLY_TEST_REPORT_CC',[])

        if not recipient:
            raise CommandError('MONTHLY_TEST_REPORT_RECIPIENT is not configured ''in settings.py')
        if not isinstance(cc_recipients, (list, tuple)):
            raise CommandError('MONTHLY_TEST_REPORT_CC must be a list or tuple in settings.py')

        institution_ids = getattr(settings,'INSTITUTION_IDS',[])

        if not institution_ids:
            raise CommandError('INSTITUTION_IDS is not configured in settings.py')
        
        # Remove duplicate institution IDs
        institution_ids = list(dict.fromkeys(institution_ids))

        # 2. PROJECT PATHS
        project_root = os.path.dirname(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(
                        os.path.abspath(__file__)
                    )
                )
            )
        )

        log_dir = os.path.join(project_root,'logs')
        report_dir = os.path.join(project_root,'monthly_reports')

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        if not os.path.exists(report_dir):
            os.makedirs(report_dir)

        # 3. LOGGING
        log_file = os.path.join(log_dir,'monthly_test_report.log')
        logger = logging.getLogger('monthly_test_report')
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.FileHandler(log_file)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        try:
            logger.info('==================================================')
            logger.info('Monthly Gujarat test report started')
            logger.info('Recipient: %s',recipient)
            logger.info('CC recipients: %s', ', '.join(cc_recipients))
            logger.info('Institution count: %d',len(institution_ids))

            # 4. CALCULATE PREVIOUS MONTH
            today = date.today()
            # First day of current month
            first_day_current_month = today.replace(day=1)
            # Last day of previous month
            last_day_previous_month = (first_day_current_month -timedelta(days=1))
            # First day of previous month
            first_day_previous_month = (last_day_previous_month.replace(day=1))
            start_date = first_day_previous_month.strftime('%Y-%m-%d')
            end_date = first_day_current_month.strftime('%Y-%m-%d')
            report_month = first_day_previous_month.strftime('%Y-%m')
            logger.info('Report month: %s',report_month)
            logger.info('Start date: %s 00:00:00',start_date)
            logger.info('End date: %s 00:00:00',end_date)
            self.stdout.write('Report period: {} to {}'.format(start_date,end_date))

            # 5. SPOKEN DB - DJANGO ORM
            logger.info('Fetching Spoken DB using Django ORM')
            spoken_queryset = (StudentMaster.objects.select_related('student__user','batch__department','batch__academic','batch__academic__institution_type').filter(batch__academic_id__in=institution_ids))
            spoken_data = {}

            for student_master in spoken_queryset:
                student = student_master.student
                user = student.user
                batch = student_master.batch
                department = batch.department
                academic = batch.academic
                institute_type = academic.institution_type
                email = user.email

                if not email:
                    continue

                email = email.strip().lower()
                spoken_data[email] = {
                    'Email Id': email,
                    'Department': department.name,
                    'Institute name': academic.institution_name,
                    'Institute Code': academic.academic_code,
                    'Institute Type': institute_type.name
                }

            logger.info('Spoken ORM records: %d',len(spoken_data))
            self.stdout.write('Spoken records: {}'.format(len(spoken_data)))

            # 6. MOODLE DATABASE QUERY
            logger.info('Fetching Gujarat data')
            institution_ids_sql = ','.join(str(institution_id)for institution_id in institution_ids)
            moodle_query = """
                SELECT
                    user.institution AS "Institute name",
                    quiz.name AS "Course Name",
                    DATE(FROM_UNIXTIME(data.timemodified))
                        AS "Test Date",
                    user.department AS "Department",
                    user.firstname AS "First Name",
                    user.lastname AS "Last Name",
                    user.email AS "Email Id",
                    FORMAT(data.grade, 2) AS "Score"
                FROM mdl_quiz_grades AS data
                JOIN mdl_user AS user
                    ON data.userid = user.id
                JOIN mdl_quiz AS quiz
                    ON data.quiz = quiz.id
                WHERE
                    data.timemodified >=
                        UNIX_TIMESTAMP(%s)
                    AND data.timemodified <
                        UNIX_TIMESTAMP(%s)
                    AND user.institution IN ({})
                ORDER BY user.email
            """.format(
                institution_ids_sql
            )
            moodle_connection = connections['moodle']

            with moodle_connection.cursor() as cursor:
                cursor.execute(
                    moodle_query,
                    [
                        start_date + ' 00:00:00',
                        end_date + ' 00:00:00'
                    ]
                )

                columns = [
                    column[0]
                    for column in cursor.description
                ]

                moodle_rows = cursor.fetchall()

            logger.info('Gujarat records: %d',len(moodle_rows))
            self.stdout.write('Gujarat records: {}'.format(len(moodle_rows)))

            # 7. FINAL TSV FILE
            output_file = os.path.join(report_dir,'monthly_Gujarat_test_report_{}.tsv'.format(report_month))
            final_columns = [
                'Institute name',
                'Course Name',
                'Test Date',
                'Department',
                'First Name',
                'Last Name',
                'Email Id',
                'Score',
                'Institute Type'
            ]

            report_count = 0
            unmatched_count = 0

            logger.info('Creating TSV: %s',output_file)
            with open(output_file,'w',newline='') as output:
                writer = csv.DictWriter(
                    output,
                    fieldnames=final_columns,
                    delimiter='\t'
                )
                writer.writeheader()

                # 8. MERGE MOODLE + SPOKEN USING EMAIL
                for row in moodle_rows:
                    moodle = dict(zip(columns,row))
                    email = moodle.get('Email Id')

                    if email:
                        email = email.strip().lower()

                    # Match Moodle email with Spoken email
                    spoken = spoken_data.get(email)

                    # Default Moodle values
                    final_row = {
                        'Institute name': moodle.get('Institute name',''),
                        'Course Name': moodle.get('Course Name',''),
                        'Test Date': moodle.get('Test Date',''),
                        'Department': moodle.get('Department',''),
                        'First Name': moodle.get('First Name',''),
                        'Last Name': moodle.get('Last Name',''),
                        'Email Id': email or '',
                        'Score': moodle.get('Score',''),
                        'Institute Type': ''
                    }
                    # Replace Moodle Institute + Department
                    # with Spoken DB values
                    if spoken:
                        final_row['Institute name'
                        ] = spoken['Institute name'
                        ]
                        final_row['Department'
                        ] = spoken['Department'
                        ]
                        final_row['Institute Type'
                        ] = spoken['Institute Type'
                        ]

                    else:
                        unmatched_count += 1
                        logger.warning('No Spoken DB match for email: %s',email)
                    writer.writerow(final_row)
                    report_count += 1
            logger.info('TSV created successfully')
            logger.info('Final report records: %d',report_count)
            logger.info('Unmatched records: %d',unmatched_count)
            self.stdout.write('Final records: {}'.format(report_count))
            self.stdout.write('Unmatched records: {}'.format(unmatched_count))

            # 9. SEND EMAIL
            subject = ('Monthly Gujarat Test Data - {}'.format(report_month))
            body = """
Dear Team,

Please find attached the Gujarat test report for {}.

Report period:
{} to {}

Total test records: {}

Unmatched records: {}

Regards,
Spoken Tutorial
""".format(
                report_month,
                start_date,
                end_date,
                report_count,
                unmatched_count
            )

            logger.info('Sending report email to: %s',recipient)
            logger.info('CC recipients: %s',', '.join(cc_recipients))
            email_message = EmailMessage(
                subject=subject,
                body=body,
                to=[recipient],
                cc=cc_recipients
            )

            email_message.attach_file(output_file)
            email_message.send()
            logger.info('Email sent successfully')
            logger.info('Monthly Gujarat test report completed successfully')
            logger.info('==================================================')
            self.stdout.write(self.style.SUCCESS('Monthly Gujarat test report completed successfully.'))
            self.stdout.write('Report file: {}'.format(output_file))

        except Exception as exc:

            logger.exception('Monthly Gujarat test report failed: %s',str(exc))
            self.stdout.write(self.style.ERROR('Monthly Gujarat test report failed: {}'.format(str(exc))))
            raise CommandError('Monthly Gujarat test report failed: {}'.format(str(exc)))