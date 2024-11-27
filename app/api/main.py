from fastapi import FastAPI, Query
from app.db.queries import get_total_traffic
from app.db.init_db import initialize_db
import logging

logging.basicConfig(
    level=logging.INFO,  # Уровень логирования: DEBUG, INFO, WARNING, ERROR
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)
initialize_db()

app = FastAPI()


@app.get("/traffic")
def traffic(
        customer_id: int = Query(None),
        start_date: str = Query(None),
        end_date: str = Query(None),
        ip: str = Query(None),
):
    logger.info(
        f"Received query with params: customer_id={customer_id}, start_date={start_date}, end_date={end_date}, ip={ip}")
    try:
        results = get_total_traffic(customer_id, start_date, end_date, ip)
    except ValueError as e:
        logger.error(f"Error in query parameters: {e}")
        return {"error": str(e)}

    logger.info(f"Query returned {len(results)} rows")

    return [
        {
            "customer_id": row.customer_id,
            "customer_name": row.customer_name,
            "ip": row.ip,
            "date": row.date.isoformat(),
            "total_traffic": row.total_traffic,
        }
        for row in results
    ]
