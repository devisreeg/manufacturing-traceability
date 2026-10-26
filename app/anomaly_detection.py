
from app.database import get_connection


def detect_anomalies():
    """Detect manufacturing data-quality and traceability anomalies."""
    anomalies = []

    with get_connection() as connection:

        # 1. Defect quantity exceeds inspected quantity.
        rows = connection.execute(
            """
            SELECT inspection_id, inspected_quantity, defect_quantity
            FROM inspection_results
            WHERE defect_quantity > inspected_quantity
            """
        ).fetchall()

        for row in rows:
            anomalies.append({
                "type": "DEFECTS_EXCEED_INSPECTED",
                "record_id": row["inspection_id"],
                "decision": "REJECT",
                "details": (
                    f"Defect quantity {row['defect_quantity']} exceeds "
                    f"inspected quantity {row['inspected_quantity']}."
                ),
                "severity": "HIGH",
            })

        # 2. Closed CAPA without successful verification.
        rows = connection.execute(
            """
            SELECT capa_id
            FROM corrective_actions
            WHERE status = 'CLOSED'
              AND (
                  closed_at IS NULL
                  OR verification_result IS NULL
                  OR verification_result != 'PASS'
              )
            """
        ).fetchall()

        for row in rows:
            anomalies.append({
                "type": "CAPA_CLOSED_BEFORE_VERIFICATION",
                "record_id": row["capa_id"],
                "decision": "REJECT",
                "details": (
                    "CAPA is closed without a valid closure timestamp "
                    "and successful verification."
                ),
                "severity": "HIGH",
            })

        # 3. Required BOM material was not consumed.
        rows = connection.execute(
            """
            SELECT po.order_id, b.material_name
            FROM production_orders po
            JOIN bom b
                ON b.product_id = po.product_id
            WHERE NOT EXISTS (
                SELECT 1
                FROM order_material_consumption c
                JOIN material_lots l
                    ON l.lot_id = c.lot_id
                WHERE c.order_id = po.order_id
                  AND l.material_name = b.material_name
            )
            """
        ).fetchall()

        for row in rows:
            anomalies.append({
                "type": "BOM_MATERIAL_NOT_CONSUMED",
                "record_id": row["order_id"],
                "decision": "FLAG",
                "details": (
                    f"Required BOM material '{row['material_name']}' "
                    "was not consumed for this production order."
                ),
                "severity": "HIGH",
            })

        # 4. Material consumption exceeds received quantity.
        rows = connection.execute(
            """
            SELECT
                l.lot_id,
                l.quantity_received,
                SUM(c.quantity_used) AS total_used
            FROM material_lots l
            JOIN order_material_consumption c
                ON l.lot_id = c.lot_id
            GROUP BY l.lot_id, l.quantity_received
            HAVING SUM(c.quantity_used) > l.quantity_received
            """
        ).fetchall()

        for row in rows:
            anomalies.append({
                "type": "EXCESS_MATERIAL_CONSUMPTION",
                "record_id": row["lot_id"],
                "decision": "REJECT",
                "details": (
                    f"Used {row['total_used']} units but only "
                    f"{row['quantity_received']} were received."
                ),
                "severity": "HIGH",
            })

        # 5. Defect references a nonexistent material lot.
        rows = connection.execute(
            """
            SELECT d.defect_id
            FROM defects d
            LEFT JOIN material_lots l
                ON d.lot_id = l.lot_id
            WHERE d.lot_id IS NOT NULL
              AND l.lot_id IS NULL
            """
        ).fetchall()

        for row in rows:
            anomalies.append({
                "type": "NONEXISTENT_LOT",
                "record_id": row["defect_id"],
                "decision": "REJECT",
                "details": (
                    "Defect references a material lot that does not exist."
                ),
                "severity": "HIGH",
            })

        # 6. Defect is missing a required inspection/order/product link.
        rows = connection.execute(
            """
            SELECT d.defect_id
            FROM defects d
            LEFT JOIN inspection_results i
                ON d.inspection_id = i.inspection_id
            LEFT JOIN production_orders po
                ON d.order_id = po.order_id
            LEFT JOIN products p
                ON po.product_id = p.product_id
            WHERE i.inspection_id IS NULL
               OR po.order_id IS NULL
               OR p.product_id IS NULL
            """
        ).fetchall()

        for row in rows:
            anomalies.append({
                "type": "BROKEN_TRACEABILITY_CHAIN",
                "record_id": row["defect_id"],
                "decision": "FLAG",
                "details": (
                    "Defect cannot be traced through its inspection, "
                    "production order, and product."
                ),
                "severity": "HIGH",
            })

    return anomalies


def print_anomalies():
    anomalies = detect_anomalies()

    print("\nMANUFACTURING ANOMALY DETECTION")
    print("=" * 60)

    if not anomalies:
        print("No anomalies detected.")
    else:
        for anomaly in anomalies:
            print(
                f"[{anomaly['severity']}] "
                f"{anomaly['type']} | "
                f"Decision: {anomaly['decision']} | "
                f"Record: {anomaly['record_id']}"
            )
            print(f"Details: {anomaly['details']}")
            print("-" * 60)

    print(f"Total anomalies detected: {len(anomalies)}")


if __name__ == "__main__":
    print_anomalies()
