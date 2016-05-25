from views import db
from _config import DATABASE_PATH

import sqlite3
# from datetime import datetime

# with sqlite3.connect(DATABASE_PATH) as connection:
#     c = connection.cursor()

#     # Temporarily change name of tasks table
#     c.execute("""ALTER TABLE tasks RENAME TO old_tasks""")

#     # create new db with updated schema
#     # only affects the tasks table as we changed its name
#     db.create_all()

#     # retrieve data from old_tasks table
#     c.execute(
#         """SELECT name, due_date, priority, status
#         FROM old_tasks
#         ORDER BY task_id ASC"""
#     )

#     # save all rows as a list of tuples.
#     # Set posted_date to now and user_id to 1
#     data = [
#         (row[0],
#          row[1],
#          row[2],
#          row[3],
#          datetime.now(),
#          1
#          ) for row in c.fetchall()
#     ]

#     # insert data into tasks table
#     c.executemany(
#         """
#         INSERT INTO tasks (
#             name,
#             due_date,
#             priority,
#             status,
#             posted_date,
#             user_id)
#         VALUES (?, ?, ?, ?, ?, ?)
#         """, data
#     )

#     # delete old tasks table
#     c.execute("""DROP TABLE old_tasks""")

with sqlite3.connect(DATABASE_PATH) as connection:
    c = connection.cursor()

    # Temporarily change name of tasks table
    # c.execute("""ALTER TABLE users RENAME TO old_users""")

    # create new db with updated schema
    # only affects the users table as we changed its name
    # db.create_all()

    # retrieve data from old_users table
    c.execute(
        """SELECT name, email, password
        FROM old_users
        ORDER BY id ASC"""
    )

    # save all rows as a list of tuples.
    # Set role to user
    data = [(row[0], row[1], row[2], 'user') for row in c.fetchall()]

    # insert data into users table
    c.executemany(
        """
        INSERT INTO users (
            name,
            email,
            password,
            role)
        VALUES (?, ?, ?, ?)
        """, data
    )

    # delete old tasks table
    c.execute("""DROP TABLE old_users""")
