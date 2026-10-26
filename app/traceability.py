from app.database import get_connection


def get_defect_traceability(defect_id=None):
    """Trace defects back to their production and material sources."""

    query = """
        SELECT
            d.defect_id,
            d.defect_type,
            d.severity,
            d.disposition,
            d.detected_at,
            i.inspection_id,
            i.inspected_quantity,
            i.defect_quantity,
            i.result AS inspection_result,
            p.order_id,
            p.product_id,
            pr.product_name,
            l.lot_id,
            l.material_name,
            s.supplier_id,
            s.supplier_name,
            ps.step_id,
            ps.step_name,
            m.machine_id,
            m.machine_name,
            ca.capa_id,
            ca.action_description,
            ca.status AS capa_status,
            ca.opened_at AS capa_opened_at,
            ca.closed_at AS capa_closed_at,
            ca.verification_result
        FROM defects d
        JOIN inspection_results i
            ON d.inspection_id = i.inspection_id
        JOIN production_orders p
            ON d.order_id = p.order_id
        JOIN products pr
            ON p.product_id = pr.product_id
        LEFT JOIN material_lots l
            ON d.lot_id = l.lot_id
        LEFT JOIN suppliers s
            ON l.supplier_id = s.supplier_id
        LEFT JOIN process_steps ps
            ON d.step_id = ps.step_id
        LEFT JOIN machines m
            ON ps.machine_id = m.machine_id
        LEFT JOIN corrective_actions ca
            ON d.defect_id = ca.defect_id
    """

    parameters = ()

    if defect_id is not None:
        query += " WHERE d.defect_id = ?"
        parameters = (defect_id,)

    query += " ORDER BY d.detected_at DESC, d.defect_id"

    with get_connection() as connection:
        rows = connection.execute(query, parameters).fetchall()

    return [dict(row) for row in rows]


def print_defect_traceability(defect_id=None):
    """Display traceability information for defects."""

    records = get_defect_traceability(defect_id)

    if not records:
        print("No matching defects found.")
        return

    for record in records:
        print("\n" + "=" * 55)
        print(f"Defect ID       : {record['defect_id']}")
        print(f"Defect Type     : {record['defect_type']}")
        print(f"Severity        : {record['severity']}")
        print(f"Disposition     : {record['disposition']}")
        print(f"Detected At     : {record['detected_at']}")

        print("\n--- Inspection ---")
        print(f"Inspection ID   : {record['inspection_id']}")
        print(f"Inspected Units : {record['inspected_quantity']}")
        print(f"Defect Units    : {record['defect_quantity']}")
        print(f"Result          : {record['inspection_result']}")

        print("\n--- Production ---")
        print(f"Order ID        : {record['order_id']}")
        print(f"Product ID      : {record['product_id']}")
        print(f"Product Name    : {record['product_name']}")

        print("\n--- Material & Supplier ---")
        print(f"Material Lot    : {record['lot_id']}")
        print(f"Material        : {record['material_name']}")
        print(f"Supplier ID     : {record['supplier_id']}")
        print(f"Supplier Name   : {record['supplier_name']}")

        print("\n--- Process & Machine ---")
        print(f"Process Step    : {record['step_name']}")
        print(f"Machine ID      : {record['machine_id']}")
        print(f"Machine Name    : {record['machine_name']}")
        print("\n--- Corrective Action (CAPA) ---")
        print(f"CAPA ID         : {record['capa_id']}")
        print(f"Action          : {record['action_description']}")
        print(f"Status          : {record['capa_status']}")
        print(f"Opened At       : {record['capa_opened_at']}")
        print(f"Closed At       : {record['capa_closed_at']}")
        print(f"Verification    : {record['verification_result']}")

    print("\n" + "=" * 55)
    print(f"Total defect records: {len(records)}")


if __name__ == "__main__":
    print_defect_traceability()