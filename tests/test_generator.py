
from app.database import get_connection
from app.generator import generate_data


def test_generated_data_has_records():
    generate_data(scale="small")

    with get_connection() as connection:
        product_count = connection.execute(
            "SELECT COUNT(*) FROM products"
        ).fetchone()[0]

        supplier_count = connection.execute(
            "SELECT COUNT(*) FROM suppliers"
        ).fetchone()[0]

        order_count = connection.execute(
            "SELECT COUNT(*) FROM production_orders"
        ).fetchone()[0]

    assert product_count > 0
    assert supplier_count > 0
    assert order_count > 0
