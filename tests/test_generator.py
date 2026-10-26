import sqlite3

from app.database import initialize_database
from app.generator import generate_data


def test_generated_data_has_records(tmp_path, monkeypatch):
    test_database = tmp_path / "test_manufacturing.db"

    monkeypatch.setattr(
        "app.database.DATABASE_PATH",
        test_database,
    )

    initialize_database()
    generate_data(scale="small")

    with sqlite3.connect(test_database) as connection:
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
