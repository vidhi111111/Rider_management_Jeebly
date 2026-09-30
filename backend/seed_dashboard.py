from app import create_app
from app.extensions import db
from app.models import Rider, Order

app = create_app()

with app.app_context():
    Rider.query.delete()
    Order.query.delete()

    riders = [
        Rider(name="Rahul Sharma", status="available"),
        Rider(name="Aman Kumar", status="available"),
        Rider(name="Vikas Singh", status="on_order"),          
        Rider(name="Rohit Verma", status="scheduled_break"),
        Rider(name="Arjun Mehta", status="absent"),
        Rider(name="Arjun", status="available")
    ]

    orders = [
        Order(
            customer_name="Customer One",
            status="delivered"
        ),
        Order(
            customer_name="Customer Two",
            status="delivered"
        ),
        Order(
            customer_name="Customer Three",
            status="in_progress"
        ),
        Order(
            customer_name="Customer Four",
            status="in_progress"
        ),
        Order(
            customer_name="Customer Five",
            status="cancelled"
        ),
        Order(
            customer_name="Customer Five",
            status="cancelled"
        )
    ]

    db.session.add_all(riders)
    db.session.add_all(orders)
    db.session.commit()

    print("Dashboard sample data inserted successfully.")