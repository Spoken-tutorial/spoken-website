import MySQLdb
import time
from config import *

# connecting with dj8 db
db1 = MySQLdb.connect(host = DB_HOST, user = DB_USER, passwd = DB_PASS, \
  db = MDB_NAME)

db2 = MySQLdb.connect(host = DB_HOST, user = DB_USER, passwd = DB_PASS, \
  db = DB_NAME)

cur1 = db1.cursor()
cur2 = db2.cursor()

cur1.execute("SELECT email From mdl_user Group BY email Having Count(*) > 1")
emails = cur1.fetchall()
error_log_file_head = open(LOG_ROOT + 'mdlusername-change-error-log.txt',"w")
success_log_file_head = open(LOG_ROOT + 'mdlusername-change-success-log.txt',"w")

count = 0
for email in emails:
  inner_query = "select id from OTC.mdl_user where email='" + email[0] + "' order by id DESC"
  main_query = "select mdluser_id from django_spoken_v2.events_testattendance where mdluser_id in (" + inner_query + ") order by mdluser_id DESC"
  cur2.execute(main_query)
  test_user = cur2.fetchone()
  if not test_user:
    cur1.execute(inner_query + " limit 1")
    test_user = cur1.fetchone()
  cur1.execute("select id, username from OTC.mdl_user where email='" + email[0] + "' order by id DESC")
  mdl_users = cur1.fetchall()
  for mdl_user in mdl_users:
    if test_user and test_user[0] == mdl_user[0]:
      print 'Test user:', mdl_user[0]
      continue
    username = mdl_user[1]
    if username.lower() == email[0].lower():
      email_split = email[0].split('@')
      email_split[0] = email_split[0] + str(count)
      count += 1
      username = email_split[0]
      print len(email_split), "*************"
    print username
    cur1.execute("update mdl_user set email='" + username + "' where id=" + str(mdl_user[0]))
    db1.commit()
    #print "update mdl_user set email='" + username + "' where id=" + str(mdl_user[0])
    print 'Updated user:', mdl_user[0]
#  break
#for row in rows:
#  cur.execute("SELECT username, email FROM mdl_user WHERE ")
