import sqlite3

from app.database import get_connection


def validate_database():
    """Run data-quality checks on the manufacturing database."""
    checks = []

    with get_connection() as connection:
        # 1. Check foreign-key relationships.
        foreign_key_errors = connection.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        checks.append(
            (
                "Foreign-key integrity",
                len(foreign_key_errors) == 0,
                len(foreign_key_errors),
            )
        )

        # 2. Every defect must reference an existing inspection.
        orphan_defects = connection.execute(
            """
            SELECT COUNT(*)
            FROM defects d
            LEFT JOIN inspection_results i
                ON d.inspection_id = i.inspection_id
            WHERE i.inspection_id IS NULL
            """
        ).fetchone()[0]

        checks.append(
            (
                "Defects linked to inspections",
                orphan_defects == 0,
                orphan_defects,
            )
        )

        # 3. Every defect must reference an existing production order.
        orphan_orders = connection.execute(
            """
            SELECT COUNT(*)
            FROM defects d
            LEFT JOIN production_orders p
                ON d.order_id = p.order_id
            WHERE p.order_id IS NULL
            """
        ).fetchone()[0]

        checks.append(
            (
                "Defects linked to production orders",
                orphan_orders == 0,
                orphan_orders,
            )
        )

        # 4. A closed corrective action must have successful verification.
        invalid_capa = connection.execute(
            """
            SELECT COUNT(*)
            FROM corrective_actions
            WHERE status = 'CLOSED'
              AND (
                  closed_at IS NULL
                  OR verification_result IS NULL
                  OR verification_result != 'PASS'
              )
            """
        ).fetchone()[0]

        checks.append(
            (
                "Closed CAPAs verified successfully",
                invalid_capa == 0,
                invalid_capa,
            )
        )

        # 5. Inspection defect quantity must not exceed inspected quantity.
        invalid_inspections = connection.execute(
            """
            SELECT COUNT(*)
            FROM inspection_results
            WHERE inspected_quantity <= 0
               OR defect_quantity < 0
               OR defect_quantity > inspected_quantity
            """
        ).fetchone()[0]

        checks.append(
            (
                "Inspection quantities valid",
                invalid_inspections == 0,
                invalid_inspections,
            )
        )

        # 6. Material consumption must not exceed the received lot quantity.
        excessive_consumption = connection.execute(
            """
            SELECT COUNT(*)
            FROM (
                SELECT
                    l.lot_id,
                    l.quantity_received,
                    COALESCE(SUM(c.quantity_used), 0) AS total_used
                FROM material_lots l
                LEFT JOIN order_material_consumption c
                    ON l.lot_id = c.lot_id
                GROUP BY l.lot_id, l.quantity_received
                HAVING total_used > l.quantity_received
            )
            """
        ).fetchone()[0]

        checks.append(
            (
                "Material consumption within received quantity",
                excessive_consumption == 0,
                excessive_consumption,
            )
        )

        # 7. Every defect must have at least one corrective action.
        defects_without_capa = connection.execute(
            """
            SELECT COUNT(*)
            FROM defects d
            LEFT JOIN corrective_actions c
                ON d.defect_id = c.defect_id
            WHERE c.capa_id IS NULL
            """
        ).fetchone()[0]

        checks.append(
            (
                "Every defect has a corrective action",
                defects_without_capa == 0,
                defects_without_capa,
            )
        )

    print("\nMANUFACTURING DATA VALIDATION")
    print("=" * 55)

    passed = 0

    for name, is_valid, issue_count in checks:
        status = "PASS" if is_valid else "FAIL"
        print(f"[{status}] {name} | Issues: {issue_count}")

        if is_valid:
            passed += 1

    print("=" * 55)
    print(f"Checks passed: {passed}/{len(checks)}")

    return all(is_valid for _, is_valid, _ in checks)


if __name__ == "__main__":
    success = validate_database()

    if not success:
        raise SystemExit(1)