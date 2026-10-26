
import sqlite3

import pytest

from app import anomaly_detection
from app.database import SCHEMA_PATH


def create_test_database(database_path):
    """Create an isolated temporary database for anomaly tests."""
    with sqlite3.connect(database_path) as connection:
        connection.executescript(
            SCHEMA_PATH.read_text(encoding="utf-8")
        )


def create_test_connection(database_path, foreign_keys=True):
    """Connect to the isolated test database."""
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute(
        f"PRAGMA foreign_keys = {'ON' if foreign_keys else 'OFF'}"
    )
    return connection


def setup_detector(monkeypatch, tmp_path):
    """Create a temporary database and point the detector to it."""
    database_path = tmp_path / "test_manufacturing.db"
    create_test_database(database_path)

    monkeypatch.setattr(
        anomaly_detection,
        "get_connection",
        lambda: create_test_connection(database_path),
    )

    return database_path


def seed_base_records(connection):
    """Insert valid records needed by anomaly test scenarios."""
    connection.execute(
        """
        INSERT INTO products
            (product_id, product_name, category, created_at)
        VALUES
            ('SKU-TEST-001', 'Test Product', 'Electronics', '2026-10-26')
        """
    )

    connection.execute(
        """
        INSERT INTO suppliers
            (supplier_id, supplier_name, status)
        VALUES
            ('SUP-TEST-001', 'Test Supplier', 'ACTIVE')
        """
    )

    connection.execute(
        """
        INSERT INTO material_lots
            (lot_id, supplier_id, material_name,
             quantity_received, received_date, status)
        VALUES
            ('LOT-TEST-001', 'SUP-TEST-001', 'Steel',
             10, '2026-10-01', 'AVAILABLE')
        """
    )

    connection.execute(
        """
        INSERT INTO production_orders
            (order_id, product_id, planned_quantity,
             produced_quantity, start_date, status)
        VALUES
            ('WO-TEST-001', 'SKU-TEST-001', 100,
             0, '2026-10-02', 'PLANNED')
        """
    )

    connection.execute(
        """
        INSERT INTO bom
            (product_id, material_name, quantity_required, effective_from)
        VALUES
            ('SKU-TEST-001', 'Steel', 2, '2026-01-01')
        """
    )

    connection.execute(
        """
        INSERT INTO inspection_plans
            (plan_id, product_id, inspection_name, acceptable_defect_rate)
        VALUES
            ('PLAN-TEST-001', 'SKU-TEST-001', 'Final Inspection', 0.05)
        """
    )

    connection.execute(
        """
        INSERT INTO inspection_results
            (inspection_id, order_id, plan_id, inspected_quantity,
             defect_quantity, inspected_at, result)
        VALUES
            ('INSP-TEST-001', 'WO-TEST-001', 'PLAN-TEST-001',
             10, 1, '2026-10-03', 'FAIL')
        """
    )

    connection.execute(
        """
        INSERT INTO defects
            (defect_id, inspection_id, order_id, lot_id, step_id,
             defect_type, severity, disposition, detected_at)
        VALUES
            ('DEF-TEST-001', 'INSP-TEST-001', 'WO-TEST-001',
             'LOT-TEST-001', NULL, 'Surface Defect', 'HIGH',
             'REWORK', '2026-10-03')
        """
    )


def find_anomaly(anomalies, anomaly_type):
    """Return the first anomaly of a requested type."""
    return next(
        (
            anomaly for anomaly in anomalies
            if anomaly["type"] == anomaly_type
        ),
        None,
    )


def test_clean_database_has_no_anomalies(monkeypatch, tmp_path):
    """A clean, empty database should produce no anomalies."""
    setup_detector(monkeypatch, tmp_path)

    assert anomaly_detection.detect_anomalies() == []


def test_detects_excess_material_consumption(monkeypatch, tmp_path):
    """Consumption above the received quantity should be detected."""
    database_path = setup_detector(monkeypatch, tmp_path)

    with create_test_connection(database_path) as connection:
        seed_base_records(connection)

        connection.executemany(
            """
            INSERT INTO order_material_consumption
                (order_id, lot_id, quantity_used)
            VALUES (?, ?, ?)
            """,
            [
                ("WO-TEST-001", "LOT-TEST-001", 6),
                ("WO-TEST-001", "LOT-TEST-001", 6),
            ],
        )

    anomaly = find_anomaly(
        anomaly_detection.detect_anomalies(),
        "EXCESS_MATERIAL_CONSUMPTION",
    )

    assert anomaly is not None
    assert anomaly["record_id"] == "LOT-TEST-001"
    assert anomaly["decision"] == "REJECT"


def test_detects_bom_material_not_consumed(monkeypatch, tmp_path):
    """A production order missing its required BOM material is flagged."""
    database_path = setup_detector(monkeypatch, tmp_path)

    with create_test_connection(database_path) as connection:
        seed_base_records(connection)

    anomaly = find_anomaly(
        anomaly_detection.detect_anomalies(),
        "BOM_MATERIAL_NOT_CONSUMED",
    )

    assert anomaly is not None
    assert anomaly["record_id"] == "WO-TEST-001"
    assert anomaly["decision"] == "FLAG"


def test_detects_nonexistent_lot(monkeypatch, tmp_path):
    """A defect referencing an unknown lot must be rejected."""
    database_path = setup_detector(monkeypatch, tmp_path)

    with create_test_connection(
    database_path, foreign_keys=False
) as connection:
        seed_base_records(connection)

        # Only this test connection bypasses foreign-key enforcement.

        connection.execute(
            """
            UPDATE defects
            SET lot_id = 'LOT-DOES-NOT-EXIST'
            WHERE defect_id = 'DEF-TEST-001'
            """
        )

    anomaly = find_anomaly(
        anomaly_detection.detect_anomalies(),
        "NONEXISTENT_LOT",
    )

    assert anomaly is not None
    assert anomaly["record_id"] == "DEF-TEST-001"
    assert anomaly["decision"] == "REJECT"


def test_detects_broken_traceability_chain(monkeypatch, tmp_path):
    """A defect missing its required inspection link is flagged."""
    database_path = setup_detector(monkeypatch, tmp_path)

    with create_test_connection(
    database_path, foreign_keys=False
) as connection:
        seed_base_records(connection)

        connection.execute(
            """
            UPDATE defects
            SET inspection_id = 'INSP-DOES-NOT-EXIST'
            WHERE defect_id = 'DEF-TEST-001'
            """
        )

    anomaly = find_anomaly(
        anomaly_detection.detect_anomalies(),
        "BROKEN_TRACEABILITY_CHAIN",
    )

    assert anomaly is not None
    assert anomaly["record_id"] == "DEF-TEST-001"
    assert anomaly["decision"] == "FLAG"


def test_detects_defects_exceeding_inspected_quantity(
    monkeypatch, tmp_path
):
    """Defect quantities above inspection quantities must be rejected."""
    database_path = setup_detector(monkeypatch, tmp_path)

    with create_test_connection(database_path) as connection:
        seed_base_records(connection)

        # SQLite CHECK constraints are disabled only for this test.
        connection.execute("PRAGMA ignore_check_constraints = ON")
        connection.execute(
            """
            UPDATE inspection_results
            SET defect_quantity = 11
            WHERE inspection_id = 'INSP-TEST-001'
            """
        )

    anomaly = find_anomaly(
        anomaly_detection.detect_anomalies(),
        "DEFECTS_EXCEED_INSPECTED",
    )

    assert anomaly is not None
    assert anomaly["record_id"] == "INSP-TEST-001"
    assert anomaly["decision"] == "REJECT"


def test_detects_capa_closed_before_verification(monkeypatch, tmp_path):
    """A closed CAPA without verification must be rejected."""
    database_path = setup_detector(monkeypatch, tmp_path)

    with create_test_connection(database_path) as connection:
        seed_base_records(connection)

        # Disable CHECK constraints only in this isolated test connection.
        connection.execute("PRAGMA ignore_check_constraints = ON")
        connection.execute(
            """
            INSERT INTO corrective_actions
                (capa_id, defect_id, action_description, status,
                 opened_at, closed_at, verification_result)
            VALUES
                ('CAPA-TEST-001', 'DEF-TEST-001',
                 'Investigate test defect', 'CLOSED',
                 '2026-10-03', '2026-10-04', 'FAIL')
            """
        )

    anomaly = find_anomaly(
        anomaly_detection.detect_anomalies(),
        "CAPA_CLOSED_BEFORE_VERIFICATION",
    )

    assert anomaly is not None
    assert anomaly["record_id"] == "CAPA-TEST-001"
    assert anomaly["decision"] == "REJECT"
