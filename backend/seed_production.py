from app import create_app
from app.extensions import db
from app.models import Rider

app = create_app()

with app.app_context():
    riders = [
        Rider(name="Rahul Sharma", status="available"),
        Rider(name="Aman Kumar", status="available"),
        Rider(name="Vikas Singh", status="on_order"),
        Rider(name="Rohit Verma", status="scheduled_break"),
        Rider(name="Arjun Mehta", status="absent"),
        Rider(name="Arjun", status="available")
    ]

    db.session.add_all(riders)
    db.session.commit()

    print("Riders inserted successfully.")