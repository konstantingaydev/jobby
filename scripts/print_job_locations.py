import sqlite3
import os
DB = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db.sqlite3')
conn = sqlite3.connect(DB)
cur = conn.cursor()
try:
    cur.execute('SELECT id, title, location FROM jobs_job')
    rows = cur.fetchall()
    if not rows:
        print('No jobs found in jobs_job table')
    else:
        for r in rows:
            print(r)
finally:
    conn.close()
