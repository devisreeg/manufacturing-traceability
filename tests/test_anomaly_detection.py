import sqlite3

from app import anomaly_detection
from app.database import SCHEMA_PATH


def create_test_database(database_path):
    """Create a separate temporary database for testing."""
    with sqlite3.connect(database_path) as connection:
        connection.executescript(
            SCHEMA_PATH.read_text(encoding="utf-8")
        )


def create_test_connection(database_path):
    """Connect to the temporary test database."""
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def test_detect_anomalies_returns_empty_list_for_clean_data(
    monkeypatch, tmp_path
):
    """A clean database should contain no anomalies."""
    database_path = tmp_path / "test_manufacturing.db"

    create_test_database(database_path)

    monkeypatch.setattr(
        anomaly_detection,
        "get_connection",
        lambda: create_test_connection(database_path),
    )

    anomalies = anomaly_detection.detect_anomalies()

    assert anomalies == []


def test_detects_excess_material_consumption(
    monkeypatch, tmp_path
):
    """Detect when material consumption exceeds received quantity."""
    database_path = tmp_path / "test_anomaly.db"

    create_test_database(database_path)

    monkeypatch.setattr(
        anomaly_detection,
        "get_connection",
        lambda: create_test_connection(database_path),
    )

    with create_test_connection(database_path) as connection:
        # Create a product.
        connection.execute(
    """
    INSERT INTO products
        (product_id, product_name, category, created_at)
    VALUES
        ('TEST-PROD-001', 'Test Product', 'Electronics',
         '2026-10-26')
    """
)

                # Create a supplier.
        connection.execute(
            """
            INSERT INTO suppliers
                (supplier_id, supplier_name, status)
            VALUES
                ('TEST-SUP-001', 'Test Supplier', 'ACTIVE')
            """
        )

                # Receive 10 units of material.
        connection.execute(
            """
            INSERT INTO material_lots
                (lot_id, supplier_id, material_name,
                 quantity_received, received_date, status)
            VALUES
                ('TEST-LOT-001', 'TEST-SUP-001', 'Steel',
                 10, '2026-10-01', 'AVAILABLE')
            """
        )

        # Create a production order.
        connection.execute(
            """
            INSERT INTO production_orders
                (order_id, product_id, planned_quantity,
                 produced_quantity, start_date, status)
            VALUES
                ('TEST-ORDER-001', 'TEST-PROD-001',
                 100, 0, '2026-10-02', 'PLANNED')
            """
        )

        # Consume 12 units even though only 10 were received.
        connection.executemany(
            """
            INSERT INTO order_material_consumption
                (order_id, lot_id, quantity_used)
            VALUES (?, ?, ?)
            """,
            [
                ("TEST-ORDER-001", "TEST-LOT-001", 6),
                ("TEST-ORDER-001", "TEST-LOT-001", 6),
            ],
        )

    # Run anomaly detection.
    anomalies = anomaly_detection.detect_anomalies()

    # Confirm that excess consumption was detected.
    assert any(
        anomaly["type"] == "EXCESS_MATERIAL_CONSUMPTION"
        and anomaly["record_id"] == "TEST-LOT-001"
        for anomaly in anomalies
    )