from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Base, Customer, Traffic
from datetime import datetime

DATABASE_URL = "sqlite:///data/traffic_data.db"

engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def initialize_db():
    session = None
    try:
        Base.metadata.create_all(engine)
        print("Таблицы созданы успешно.")

        session = Session()

        customers = [
            Customer(name="John Doe"),
            Customer(name="Jane Smith"),
            Customer(name="Alice Johnson"),
            Customer(name="Bob Brown"),
            Customer(name="Charlie Brown"),
            Customer(name="David White"),
            Customer(name="Emily Green"),
            Customer(name="Frank Black"),
        ]
        session.add_all(customers)
        session.commit()
        print("Клиенты добавлены успешно.")

        traffic_data = [
            Traffic(customer_id=1, ip="192.168.218.159", date=datetime(2022, 1, 5, 10, 15), received_traffic=150.00),
            Traffic(customer_id=2, ip="192.168.5.110", date=datetime(2022, 7, 15, 13, 45), received_traffic=200.00),
            Traffic(customer_id=3, ip="192.168.214.201", date=datetime(2022, 2, 25, 18, 30), received_traffic=250.00),
        ]
        session.add_all(traffic_data)
        session.commit()
        print("Трафик добавлен успешно.")
    except Exception as e:
        print(f"Ошибка при инициализации базы данных: {e}")
    finally:
        if session:
            session.close()

if __name__ == "__main__":
    initialize_db()
