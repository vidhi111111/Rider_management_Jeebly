from sqlalchemy import inspect, text
from app import create_app
from app.extensions import db


app = create_app()

with app.app_context():
    inspector = inspect(db.engine)
    columns = {
        column["name"]
        for column in inspector.get_columns("rider")
    }

    if "mobile" not in columns:
        db.session.execute(
            text(
                "ALTER TABLE rider "
                "ADD COLUMN mobile VARCHAR(10)"
            )
        )

    if "email" not in columns:
        db.session.execute(
            text(
                "ALTER TABLE rider "
                "ADD COLUMN email VARCHAR(120)"
            )
        )

    if "vehicle" not in columns:
        db.session.execute(
            text(
                "ALTER TABLE rider "
                "ADD COLUMN vehicle VARCHAR(100)"
            )
        )

    if "availability" not in columns:
        db.session.execute(
            text(
                "ALTER TABLE rider "
                "ADD COLUMN availability VARCHAR(30)"
            )
        )

    if "date" not in columns:
        db.session.execute(
            text(
                "ALTER TABLE rider "
                "ADD COLUMN date DATE"
            )
        )

    if "profile_image" not in columns:
        db.session.execute(
            text(
                "ALTER TABLE rider "
                "ADD COLUMN profile_image VARCHAR(255)"
            )
        )

    db.session.execute(
        text(
            "UPDATE rider "
            "SET availability = 'available' "
            "WHERE availability IS NULL"
        )
    )

    db.session.execute(
        text(
            "UPDATE rider "
            "SET vehicle = 'Not Assigned' "
            "WHERE vehicle IS NULL"
        )
    )

    db.session.execute(
        text(
            "UPDATE rider "
            "SET date = CURRENT_DATE "
            "WHERE date IS NULL"
        )
    )

    db.session.commit()

    print("Rider table updated successfully.")