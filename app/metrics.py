from app.database import get_connection


def calculate_metrics():
    """Calculate manufacturing production and quality metrics."""

    with get_connection() as connection:

        production = connection.execute("""
            SELECT
                COUNT(*) AS total_orders,
                COALESCE(SUM(planned_quantity), 0) AS planned_units,
                COALESCE(SUM(produced_quantity), 0) AS produced_units
            FROM production_orders
        """).fetchone()

        inspections = connection.execute("""
            SELECT
                COUNT(*) AS inspection_count,
                COALESCE(SUM(inspected_quantity), 0) AS inspected_units,
                COALESCE(SUM(defect_quantity), 0) AS defect_units
            FROM inspection_results
        """).fetchone()

        defects = connection.execute("""
            SELECT
                COUNT(*) AS total_defect_cases,
                COALESCE(SUM(CASE
                    WHEN disposition = 'SCRAP' THEN 1 ELSE 0
                END), 0) AS scrap_cases,
                COALESCE(SUM(CASE
                    WHEN disposition = 'REWORK' THEN 1 ELSE 0
                END), 0) AS rework_cases,
                COALESCE(SUM(CASE
                    WHEN severity = 'CRITICAL' THEN 1 ELSE 0
                END), 0) AS critical_cases
            FROM defects
        """).fetchone()

        capa = connection.execute("""
            SELECT
                COUNT(*) AS total_actions,
                COALESCE(SUM(CASE
                    WHEN status = 'OPEN' THEN 1 ELSE 0
                END), 0) AS open_actions,
                COALESCE(SUM(CASE
                    WHEN status = 'IN_PROGRESS' THEN 1 ELSE 0
                END), 0) AS in_progress_actions,
                COALESCE(SUM(CASE
                    WHEN status = 'PENDING_VERIFICATION' THEN 1 ELSE 0
                END), 0) AS pending_verification,
                COALESCE(SUM(CASE
                    WHEN status = 'CLOSED' THEN 1 ELSE 0
                END), 0) AS closed_actions
            FROM corrective_actions
        """).fetchone()

    inspected_units = inspections["inspected_units"]
    defect_units = inspections["defect_units"]

    defect_rate = (
        defect_units / inspected_units * 100
        if inspected_units else 0.0
    )

    return {
        "total_orders": production["total_orders"],
        "planned_units": production["planned_units"],
        "produced_units": production["produced_units"],
        "inspection_count": inspections["inspection_count"],
        "inspected_units": inspected_units,
        "defect_units": defect_units,
        "defect_rate_percent": round(defect_rate, 2),
        "total_defect_cases": defects["total_defect_cases"],
        "scrap_cases": defects["scrap_cases"],
        "rework_cases": defects["rework_cases"],
        "critical_cases": defects["critical_cases"],
        "total_capa": capa["total_actions"],
        "open_capa": capa["open_actions"],
        "in_progress_capa": capa["in_progress_actions"],
        "pending_verification_capa": capa["pending_verification"],
        "closed_capa": capa["closed_actions"],
    }


def print_metrics():
    """Print a formatted manufacturing quality report."""

    metrics = calculate_metrics()

    print("\nMANUFACTURING QUALITY METRICS")
    print("=" * 45)

    for name, value in metrics.items():
        print(f"{name.replace('_', ' ').title():30}: {value}")

    print("=" * 45)


if __name__ == "__main__":
    print_metrics()