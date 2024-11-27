import pytest
from app.db.models import Traffic, Customer
from app.db.init_db import SessionLocal
from fastapi.testclient import TestClient
from app.api.main import app
from datetime import datetime

client = TestClient(app)

@pytest.fixture
def setup_db():
    db = SessionLocal()
    db.query(Customer).delete()
    db.query(Traffic).delete()
    db.commit()

    customers = [
        Customer(id=1, name="John Doe"),
        Customer(id=2, name="Jane Smith"),
        Customer(id=3, name="Alice Johnson"),
        Customer(id=4, name="Bob Brown"),
    ]
    traffic_data = [
        Traffic(customer_id=1, ip="192.168.218.159", date=datetime(2022, 1, 5, 10, 15), received_traffic=150.00),
        Traffic(customer_id=2, ip="192.168.5.110", date=datetime(2022, 7, 15, 13, 45), received_traffic=200.00),
        Traffic(customer_id=3, ip="192.168.214.201", date=datetime(2022, 2, 25, 18, 30), received_traffic=250.00),
        Traffic(customer_id=4, ip="192.168.224.118", date=datetime(2024, 3, 7, 12, 0), received_traffic=300.00),
        Traffic(customer_id=2, ip="192.168.218.159", date=datetime(2024, 3, 15, 14, 0), received_traffic=120.00),
        Traffic(customer_id=4, ip="192.168.5.110", date=datetime(2024, 3, 18, 15, 0), received_traffic=400.00),
        Traffic(customer_id=1, ip="192.168.214.201", date=datetime(2023, 1, 10, 10, 30), received_traffic=180.00),
        Traffic(customer_id=3, ip="192.168.224.118", date=datetime(2023, 2, 28, 14, 0), received_traffic=220.00),
        Traffic(customer_id=2, ip="192.168.218.159", date=datetime(2023, 3, 1, 16, 15), received_traffic=175.00),
        Traffic(customer_id=4, ip="192.168.5.110", date=datetime(2023, 3, 10, 17, 45), received_traffic=300.00),
    ]
    db.add_all(customers)
    db.add_all(traffic_data)
    db.commit()
    yield db
    db.close()


# Тест фильтрации по заказчику (customer_id)
def test_traffic_by_customer_id(setup_db):
    response = client.get("/traffic?customer_id=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(item["customer_name"] == "John Doe" for item in data)


# Тест фильтрации по периоду (start_date, end_date)
def test_traffic_by_date_range(setup_db):
    response = client.get("/traffic?start_date=2023-01-01 00:00:00&end_date=2024-12-31 23:59:59")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    for item in data:
        date = datetime.fromisoformat(item["date"])
        assert date >= datetime(2023, 1, 1, 0, 0, 0)
        assert date <= datetime(2024, 12, 31, 23, 59, 59)


# Тетт фильтрации по IP-адресу
def test_traffic_by_ip(setup_db):
    response = client.get("/traffic?ip=192.168.218.159")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(item["ip"] == "192.168.218.159" for item in data)


# Тест отсутствия данных для несуществующего заказчика
def test_no_traffic_for_nonexistent_customer(setup_db):
    response = client.get("/traffic?customer_id=9999")
    assert response.status_code == 200
    data = response.json()
    assert data == []


# Тест получения всех данных о трафике
def test_get_all_traffic(setup_db):
    response = client.get("/traffic")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0


# Тест фильтрации по заказчику и периоду (start_date, end_date)
def test_traffic_by_customer_and_date_range(setup_db):
    response = client.get("/traffic?customer_id=2&start_date=2023-01-01 00:00:00&end_date=2024-12-31 23:59:59")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    for item in data:
        assert item["customer_name"] == "Jane Smith"
        date = datetime.fromisoformat(item["date"])
        assert date >= datetime(2023, 1, 1, 0, 0, 0)
        assert date <= datetime(2024, 12, 31, 23, 59, 59)


# Тест фильтрации по всем параметрам (customer_id, date, ip)
def test_traffic_by_customer_date_range_and_ip(setup_db):
    response = client.get("/traffic?customer_id=3&start_date=2022-01-01 00:00:00&end_date=2023-12-31 23:59:59&ip=192.168.214.201")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    for item in data:
        assert item["customer_name"] == "Alice Johnson"
        date = datetime.fromisoformat(item["date"])
        assert date >= datetime(2022, 1, 1, 0, 0, 0)
        assert date <= datetime(2023, 12, 31, 23, 59, 59)
        assert item["ip"] == "192.168.214.201"


# Тест проверки некорректного формата даты
def test_invalid_date_format(setup_db):
    response = client.get("/traffic?start_date=2023-03-01 16:15&end_date=2023-03-01 18:00")
    assert response.status_code == 422  # Ошибка валидации формата даты
    assert "start_date" in response.text


# Тест фильтрации по пустым параметрам (без указания параметров)
def test_empty_query_params(setup_db):
    response = client.get("/traffic?")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0  # Должны быть данные в базе, даже если параметры не указаны


# Тест фильтрации по IP, который отсутствует в базе
def test_traffic_by_nonexistent_ip(setup_db):
    response = client.get("/traffic?ip=192.168.123.123")
    assert response.status_code == 200
    data = response.json()
    assert data == []


# фильтрация по неверному диапазону дат (start_date больше end_date)
def test_invalid_date_range(setup_db):
    response = client.get("/traffic?start_date=2024-03-01 00:00:00&end_date=2023-03-01 00:00:00")
    assert response.status_code == 400  # Ошибка, так как start_date не может быть больше end_date


# фильтрация комбинированной фильтрации по заказчику, IP и некорректному диапазону дат
def test_traffic_with_invalid_date_combination(setup_db):
    response = client.get("/traffic?customer_id=2&start_date=2023-03-01 00:00:00&end_date=2023-02-01 00:00:00&ip=192.168.218.159")
    assert response.status_code == 400  # Неверный диапазон дат


# только по одному параметру, например, только по IP
def test_traffic_by_only_ip(setup_db):
    response = client.get("/traffic?ip=192.168.218.159")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(item["ip"] == "192.168.218.159" for item in data)


#  по диапазону дат и отсутствием данных
def test_traffic_no_data_in_date_range(setup_db):
    response = client.get("/traffic?start_date=2025-01-01 00:00:00&end_date=2025-12-31 23:59:59")
    assert response.status_code == 200
    data = response.json()
    assert data == []
