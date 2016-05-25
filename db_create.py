from project import db
from project.models import Task, User
from datetime import date, datetime

# create the database and the db table
db.create_all()

# insert data

db.session.add(
    User(
        "admin",
        "ad@min.com",
        "admin",
        "admin"
    )
)

db.session.add(
    Task(
        "Finish this tutorial",
        date(2015, 3, 13),
        10,
        datetime.now(),
        1,
        1
    )
)

db.session.add(
    Task(
        "Bips",
        date(2044, 1, 1),
        9,
        datetime.now(),
        1,
        1
    )
)

db.session.commit()
