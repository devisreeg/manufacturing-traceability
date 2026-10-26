from app.database import get_connection


def test_foreign_key_integrity():
    with get_connection() as connection:
        violations = connection.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

    assert len(violations) == 0


def test_all_defects_have_corrective_actions():
    with get_connection() as connection:
        missing_actions = connection.execute(
            """
            SELECT COUNT(*)
            FROM defects d
            LEFT JOIN corrective_actions ca
                ON d.defect_id = ca.defect_id
            WHERE ca.defect_id IS NULL
            """
        ).fetchone()[0]

    assert missing_actions == 0


def test_inspection_quantities_are_valid():
    with get_connection() as connection:
        invalid_records = connection.execute(
            """
            SELECT COUNT(*)
            FROM inspection_results
            WHERE inspected_quantity < 0
               OR defect_quantity < 0
               OR defect_quantity > inspected_quantity
            """
        ).fetchone()[0]

    assert invalid_records == 0
