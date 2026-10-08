from sqlalchemy import inspect, text
from app import create_app
from app.extensions import db


app = create_app()

with app.app_context():

    # check rider table columns
    inspector = inspect(db.engine)

    columns = {
        column["name"]
        for column in inspector.get_columns("rider")
    }

    # add mobile column if it does not exist
    if "mobile" not in columns:
        db.session.execute(
            text(
                "ALTER TABLE rider "
                "ADD COLUMN mobile VARCHAR(10)"
            )
        )

    # add email column if it does not exist
    if "email" not in columns:
        db.session.execute(
            text(
                "ALTER TABLE rider "
                "ADD COLUMN email VARCHAR(120)"
            )
        )

    # add vehicle column if it does not exist
    if "vehicle" not in columns:
        db.session.execute(
            text(
                "ALTER TABLE rider "
                "ADD COLUMN vehicle VARCHAR(100)"
            )
        )

    # add availability column if it does not exist
    if "availability" not in columns:
        db.session.execute(
            text(
                "ALTER TABLE rider "
                "ADD COLUMN availability VARCHAR(30)"
            )
        )

    # add date column if it does not exist
    if "date" not in columns:
        db.session.execute(
            text(
                "ALTER TABLE rider "
                "ADD COLUMN date DATE"
            )
        )

    # add profile image column if it does not exist
    if "profile_image" not in columns:
        db.session.execute(
            text(
                "ALTER TABLE rider "
                "ADD COLUMN profile_image VARCHAR(255)"
            )
        )

    # update existing rider data for testing
    rider_data = [
        {
            "id": 1,
            "mobile": "9876543210",
            "email": "rahul.sharma@gmail.com",
            "vehicle": "Bike",
            "status": "available",
            "availability": "available",
            "date": "2026-10-08"
        },
        {
            "id": 2,
            "mobile": "9876543211",
            "email": "aman.kumar@gmail.com",
            "vehicle": "Scooter",
            "status": "available",
            "availability": "unavailable",
            "date": "2026-10-07"
        },
        {
            "id": 3,
            "mobile": "9876543212",
            "email": "vikas.singh@gmail.com",
            "vehicle": "Bike",
            "status": "on_order",
            "availability": "available",
            "date": "2026-10-06"
        },
        {
            "id": 4,
            "mobile": "9876543213",
            "email": "rohit.verma@gmail.com",
            "vehicle": "Car",
            "status": "scheduled_break",
            "availability": "unavailable",
            "date": "2026-10-05"
        },
        {
            "id": 5,
            "mobile": "9876543214",
            "email": "arjun.mehta@gmail.com",
            "vehicle": "Bike",
            "status": "absent",
            "availability": "unavailable",
            "date": "2026-10-04"
        },
        {
            "id": 6,
            "mobile": "9876543215",
            "email": "arjun.rider@gmail.com",
            "vehicle": "Scooter",
            "status": "available",
            "availability": "available",
            "date": "2026-10-03"
        }
    ]

    # update rider details
    for rider in rider_data:
        db.session.execute(
            text(
                """
                UPDATE rider
                SET
                    mobile = :mobile,
                    email = :email,
                    vehicle = :vehicle,
                    status = :status,
                    availability = :availability,
                    date = :date
                WHERE id = :id
                """
            ),
            rider
        )

    # set default values for any other riders
    db.session.execute(
        text(
            """
            UPDATE rider
            SET availability = 'available'
            WHERE availability IS NULL
            """
        )
    )

    db.session.execute(
        text(
            """
            UPDATE rider
            SET vehicle = 'Not Assigned'
            WHERE vehicle IS NULL
            """
        )
    )

    db.session.execute(
        text(
            """
            UPDATE rider
            SET date = CURRENT_DATE
            WHERE date IS NULL
            """
        )
    )

    db.session.commit()

    print("Rider table updated successfully.")
    print("Rider test data updated successfully.")