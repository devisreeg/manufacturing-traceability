import argparse
import random
from datetime import date, timedelta

from app.database import get_connection, initialize_database


SEED = 20261022


def generate_data(scale="small"):
    rng = random.Random(SEED)

    if scale == "small":
        product_count = 20
        supplier_count = 10
        lot_count = 100
        order_count = 200
        inspections_per_order = 4
    else:
        product_count = 200
        supplier_count = 50
        lot_count = 2000
        order_count = 5000
        inspections_per_order = 4

    today = date(2026, 10, 26)
    defect_types = [
        "DIMENSION_ERROR",
        "SURFACE_DAMAGE",
        "MATERIAL_FAILURE",
        "ASSEMBLY_ERROR",
        "PROCESS_DRIFT",
    ]

    with get_connection() as connection:
        cursor = connection.cursor()

        # Clear previous generated data in dependency order.
        cursor.execute("DELETE FROM event_history")
        cursor.execute("DELETE FROM corrective_actions")
        cursor.execute("DELETE FROM defects")
        cursor.execute("DELETE FROM inspection_results")
        cursor.execute("DELETE FROM inspection_plans")
        cursor.execute("DELETE FROM process_steps")
        cursor.execute("DELETE FROM order_material_consumption")
        cursor.execute("DELETE FROM production_orders")
        cursor.execute("DELETE FROM material_lots")
        cursor.execute("DELETE FROM bom")
        cursor.execute("DELETE FROM machines")
        cursor.execute("DELETE FROM suppliers")
        cursor.execute("DELETE FROM products")

        # 1. Products
        products = [
            (
                f"SKU-{i:06d}",
                f"Manufactured Product {i:03d}",
                rng.choice(["ELECTRONICS", "MECHANICAL", "AUTOMOTIVE"]),
                today.isoformat(),
            )
            for i in range(1, product_count + 1)
        ]
        cursor.executemany(
            """INSERT INTO products
               (product_id, product_name, category, created_at)
               VALUES (?, ?, ?, ?)""",
            products,
        )

        # 2. Suppliers
        suppliers = [
            (f"SUP-{i:04d}", f"Supplier {i:03d}", "ACTIVE")
            for i in range(1, supplier_count + 1)
        ]
        cursor.executemany(
            """INSERT INTO suppliers
               (supplier_id, supplier_name, status)
               VALUES (?, ?, ?)""",
            suppliers,
        )

        # 3. Bills of materials (BOM)
        bom_rows = []
        for product_id, _, _, _ in products:
            material_name = f"MATERIAL-{rng.randint(1, 30):03d}"
            bom_rows.append(
                (
                    product_id,
                    material_name,
                    float(rng.randint(1, 5)),
                    "2026-01-01",
                )
            )

        cursor.executemany(
            """INSERT INTO bom
               (product_id, material_name, quantity_required, effective_from)
               VALUES (?, ?, ?, ?)""",
            bom_rows,
        )

        # 4. Material lots
        # Guarantee at least one lot for every material required by the BOM.
        lots = []
        required_materials = sorted({
            row[1] for row in bom_rows
        })

        for index, material_name in enumerate(required_materials):
            supplier_id = suppliers[index % supplier_count][0]
            received_date = today - timedelta(
                days=rng.randint(1, 250)
            )

            lots.append(
                (
                    f"LOT-{supplier_id}-2026-{index + 1:06d}",
                    supplier_id,
                    material_name,
                    10000.0,
                    received_date.isoformat(),
                    "AVAILABLE",
                )
            )

        # Add more lots for realistic dataset volume.
        for i in range(len(lots) + 1, lot_count + 1):
            supplier_id = suppliers[(i - 1) % supplier_count][0]
            material_name = f"MATERIAL-{rng.randint(1, 30):03d}"
            received_date = today - timedelta(
                days=rng.randint(1, 250)
            )

            lots.append(
                (
                    f"LOT-{supplier_id}-2026-{i:06d}",
                    supplier_id,
                    material_name,
                    float(rng.randint(100, 1000)),
                    received_date.isoformat(),
                    "AVAILABLE",
                )
            )

        cursor.executemany(
            """INSERT INTO material_lots
               (lot_id, supplier_id, material_name, quantity_received,
                received_date, status)
               VALUES (?, ?, ?, ?, ?, ?)""",
            lots,
        )

        # 5. Machines
        machines = [
            (f"MCH-{i:03d}", f"Production Machine {i:02d}", "ACTIVE")
            for i in range(1, 11)
        ]
        cursor.executemany(
            """INSERT INTO machines (machine_id, machine_name, status)
               VALUES (?, ?, ?)""",
            machines,
        )

        # 6. Inspection plans
        plans = []
        for i, (product_id, _, _, _) in enumerate(products, start=1):
            plans.append(
                (
                    f"PLAN-{i:06d}",
                    product_id,
                    "Final Quality Inspection",
                    0.03,
                )
            )

        cursor.executemany(
            """INSERT INTO inspection_plans
               (plan_id, product_id, inspection_name, acceptable_defect_rate)
               VALUES (?, ?, ?, ?)""",
            plans,
        )

        product_to_plan = {
            product[0]: plans[index][0]
            for index, product in enumerate(products)
        }

        # 7. Production orders, material consumption, process steps,
        #    inspections, defects and corrective actions.
        order_rows = []
        consumption_rows = []
        step_rows = []
        inspection_rows = []
        defect_rows = []
        capa_rows = []
        event_rows = []
            
        remaining_by_lot = {
            lot[0]: float(lot[3])
            for lot in lots
        }

        for i in range(1, order_count + 1):
            product = products[(i - 1) % product_count]
            product_id = product[0]
            order_id = f"WO-2026-{i:06d}"

            planned_quantity = rng.randint(50, 200)
            produced_quantity = planned_quantity
            start_date = today - timedelta(days=rng.randint(1, 180))
            end_date = start_date + timedelta(days=rng.randint(0, 3))

            order_rows.append(
                (
                    order_id,
                    product_id,
                    planned_quantity,
                    produced_quantity,
                    start_date.isoformat(),
                    end_date.isoformat(),
                    "COMPLETED",
                )
            )

            # Link one real material lot to this order.
                       # Select a lot matching this product's required BOM material.
            required_material = next(
                row[1] for row in bom_rows
                if row[0] == product_id
            )

            matching_lots = [
                lot for lot in lots
                if lot[2] == required_material
                and remaining_by_lot[lot[0]] >= 10
            ]

            if not matching_lots:
                raise ValueError(
                    f"No sufficient lot found for BOM material "
                    f"{required_material} in order {order_id}."
                )

            lot = matching_lots[(i - 1) % len(matching_lots)]
            lot_id = lot[0]

            available_quantity = remaining_by_lot[lot_id]
            quantity_used = float(
                rng.randint(10, min(50, int(available_quantity)))
            )

            remaining_by_lot[lot_id] -= quantity_used

            consumption_rows.append(
                (order_id, lot_id, quantity_used)
            )
            
            # A process step records the machine used by the order.
            machine = machines[(i - 1) % len(machines)]
            step_id = f"STEP-{i:06d}"

            step_rows.append(
                (
                    step_id,
                    order_id,
                    machine[0],
                    "ASSEMBLY",
                    start_date.isoformat(),
                    end_date.isoformat(),
                    "COMPLETED",
                )
            )

            # Four inspection records per production order.
            for j in range(1, inspections_per_order + 1):
                inspection_id = f"INSP-{i:06d}-{j:02d}"
                inspected_quantity = max(1, planned_quantity // inspections_per_order)

                # Deterministic random defect counts, with some clean inspections.
                if rng.random() < 0.20:
                    defect_quantity = rng.randint(
                        1, min(3, inspected_quantity)
                    )
                else:
                    defect_quantity = 0

                result = "FAIL" if defect_quantity > 0 else "PASS"

                inspection_rows.append(
                    (
                        inspection_id,
                        order_id,
                        product_to_plan[product_id],
                        inspected_quantity,
                        defect_quantity,
                        end_date.isoformat(),
                        result,
                    )
                )

                if defect_quantity > 0:
                    defect_id = f"DEF-2026-{len(defect_rows) + 1:06d}"
                    defect_type = rng.choice(defect_types)
                    severity = rng.choice(
                        ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
                    )
                    disposition = rng.choice(["REWORK", "SCRAP", "PENDING"])

                    defect_rows.append(
                        (
                            defect_id,
                            inspection_id,
                            order_id,
                            lot_id,
                            step_id,
                            defect_type,
                            severity,
                            disposition,
                            end_date.isoformat(),
                        )
                    )

                    capa_id = f"CAPA-2026-{len(capa_rows) + 1:06d}"

                    # Open actions remain open; closed actions must be verified.
                    if rng.random() < 0.60:
                        capa_status = "CLOSED"
                        closed_at = (end_date + timedelta(days=1)).isoformat()
                        verification_result = "PASS"
                    else:
                        capa_status = "OPEN"
                        closed_at = None
                        verification_result = None

                    capa_rows.append(
                        (
                            capa_id,
                            defect_id,
                            f"Investigate and correct {defect_type}",
                            capa_status,
                            end_date.isoformat(),
                            closed_at,
                            verification_result,
                        )
                    )

            event_rows.append(
                (
                    "ProductionOrder",
                    order_id,
                    "ORDER_COMPLETED",
                    f"Produced {produced_quantity} units",
                    end_date.isoformat(),
                )
            )

        cursor.executemany(
            """INSERT INTO production_orders
               (order_id, product_id, planned_quantity, produced_quantity,
                start_date, end_date, status)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            order_rows,
        )

        cursor.executemany(
            """INSERT INTO order_material_consumption
               (order_id, lot_id, quantity_used)
               VALUES (?, ?, ?)""",
            consumption_rows,
        )

        cursor.executemany(
            """INSERT INTO process_steps
               (step_id, order_id, machine_id, step_name, started_at,
                ended_at, status)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            step_rows,
        )

        cursor.executemany(
            """INSERT INTO inspection_results
               (inspection_id, order_id, plan_id, inspected_quantity,
                defect_quantity, inspected_at, result)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            inspection_rows,
        )

        if defect_rows:
            cursor.executemany(
                """INSERT INTO defects
                   (defect_id, inspection_id, order_id, lot_id, step_id,
                    defect_type, severity, disposition, detected_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                defect_rows,
            )

        if capa_rows:
            cursor.executemany(
                """INSERT INTO corrective_actions
                   (capa_id, defect_id, action_description, status,
                    opened_at, closed_at, verification_result)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                capa_rows,
            )

        cursor.executemany(
            """INSERT INTO event_history
               (entity_type, entity_id, event_type, event_details, event_time)
               VALUES (?, ?, ?, ?, ?)""",
            event_rows,
        )

    print("Data generation completed successfully.")
    print(f"Products: {len(products)}")
    print(f"Suppliers: {len(suppliers)}")
    print(f"Material lots: {len(lots)}")
    print(f"Production orders: {len(order_rows)}")
    print(f"Inspections: {len(inspection_rows)}")
    print(f"Defects: {len(defect_rows)}")
    print(f"Corrective actions: {len(capa_rows)}")
    print(f"Seed: {SEED}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate manufacturing traceability demo data."
    )
    parser.add_argument(
        "--scale",
        choices=["small", "full"],
        default="small",
        help="Use small data for development or full challenge volume.",
    )
    args = parser.parse_args()

    initialize_database()
    generate_data(scale=args.scale)

