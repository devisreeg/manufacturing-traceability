
from app.database import get_connection


def detect_anomalies():
    """Detect manufacturing data-quality anomalies."""
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
                "type": "INVALID_DEFECT_QUANTITY",
                "record_id": row["inspection_id"],
                "details": (
                    f"Defect quantity {row['defect_quantity']} exceeds "
                    f"inspected quantity {row['inspected_quantity']}."
                ),
                "severity": "HIGH",
            })

        # 2. Closed CAPA without successful verification.
        rows = connection.execute(
            """
            SELECT capa_id, status, closed_at, verification_result
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
                "type": "INVALID_CLOSED_CAPA",
                "record_id": row["capa_id"],
                "details": (
                    "CAPA is closed without a valid closure timestamp "
                    "and successful verification."
                ),
                "severity": "HIGH",
            })

        # 3. Material consumption exceeds received quantity.
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
                "details": (
                    f"Used {row['total_used']} units but only "
                    f"{row['quantity_received']} were received."
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
                f"Record: {anomaly['record_id']}"
            )
            print(f"Details: {anomaly['details']}")
            print("-" * 60)

    print(f"Total anomalies detected: {len(anomalies)}")


if __name__ == "__main__":
    print_anomalies()
