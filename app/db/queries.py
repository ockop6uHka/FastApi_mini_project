from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func
from app.db.models import Traffic, Customer
from datetime import datetime

DATABASE_URL = "sqlite:///data/traffic_data.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


def get_total_traffic(customer_id=None, start_date=None, end_date=None, ip=None):
    session = Session()
    query = session.query(
        Traffic.customer_id,
        Customer.name.label("customer_name"),
        Traffic.ip,
        Traffic.date,
        func.sum(Traffic.received_traffic).label("total_traffic")
    ).join(Traffic, Customer.id == Traffic.customer_id).group_by(
        Traffic.customer_id, Traffic.ip, Traffic.date, Customer.name
    )

    if customer_id:
        query = query.filter(Traffic.customer_id == customer_id)

    if start_date:
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
            query = query.filter(Traffic.date >= start_date)
        except ValueError:
            raise ValueError("Invalid date format for start_date. Use 'YYYY-MM-DD HH:MM:SS'.")

    if end_date:
        try:
            end_date = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
            query = query.filter(Traffic.date <= end_date)
        except ValueError:
            raise ValueError("Invalid date format for end_date. Use 'YYYY-MM-DD HH:MM:SS'.")

    if ip:
        query = query.filter(Traffic.ip == ip)

    results = query.all()
    session.close()
    return results

