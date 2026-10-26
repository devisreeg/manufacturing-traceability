import streamlit as st
import pandas as pd

from app.database import get_connection
from app.metrics import calculate_metrics
from app.traceability import get_defect_traceability


st.set_page_config(
    page_title="Manufacturing Quality Dashboard",
    page_icon="🏭",
    layout="wide"
)


@st.cache_data(ttl=10)
def load_table(query):
    """Load query results into a DataFrame."""
    with get_connection() as connection:
        return pd.read_sql_query(query, connection)


def main():
    st.title("Manufacturing Traceability & Quality Dashboard")
    st.caption(
        "Monitor production, investigate defects, "
        "and track corrective and preventive actions."
    )

    # Load the calculated metrics
    metrics = calculate_metrics()

    st.header("Production Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Production Orders", metrics["total_orders"])
    col2.metric("Planned Units", f'{metrics["planned_units"]:,}')
    col3.metric("Produced Units", f'{metrics["produced_units"]:,}')
    col4.metric("Inspection Records", metrics["inspection_count"])

    st.divider()

    st.header("Quality Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Inspected Units",
        f'{metrics["inspected_units"]:,}'
    )
    col2.metric(
        "Defect Units",
        f'{metrics["defect_units"]:,}'
    )
    col3.metric(
        "Defect Rate",
        f'{metrics["defect_rate_percent"]:.2f}%'
    )
    col4.metric(
        "Critical Defects",
        metrics["critical_cases"]
    )

    st.subheader("Defect Disposition")

    disposition_data = pd.DataFrame({
        "Disposition": ["Scrap", "Rework"],
        "Cases": [
            metrics["scrap_cases"],
            metrics["rework_cases"]
        ]
    })

    st.bar_chart(
        disposition_data.set_index("Disposition")
    )

    # CAPA overview
    st.divider()
    st.header("Corrective and Preventive Actions (CAPA)")

    capa_col1, capa_col2, capa_col3, capa_col4 = st.columns(4)

    capa_col1.metric("Total CAPA", metrics["total_capa"])
    capa_col2.metric("Open", metrics["open_capa"])
    capa_col3.metric(
        "In Progress",
        metrics["in_progress_capa"]
    )
    capa_col4.metric("Closed", metrics["closed_capa"])

    capa_data = pd.DataFrame({
        "Status": [
            "Open",
            "In Progress",
            "Pending Verification",
            "Closed"
        ],
        "Actions": [
            metrics["open_capa"],
            metrics["in_progress_capa"],
            metrics["pending_verification_capa"],
            metrics["closed_capa"]
        ]
    })

    st.bar_chart(capa_data.set_index("Status"))

    # Defect traceability
    st.divider()
    st.header("Defect Traceability")

    defects = get_defect_traceability()

    if defects:
        defect_df = pd.DataFrame(defects)

        st.write(
            "Search for a defect to trace it back to its "
            "inspection, production order, material lot, "
            "supplier, process step, and machine."
        )

        defect_ids = defect_df["defect_id"].dropna().tolist()

        selected_defect = st.selectbox(
            "Select a Defect ID",
            ["All defects"] + defect_ids
        )

        if selected_defect == "All defects":
            filtered_df = defect_df
        else:
            filtered_df = defect_df[
                defect_df["defect_id"] == selected_defect
            ]

        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )

        if selected_defect != "All defects":
            st.subheader("Selected Defect Details")

            record = filtered_df.iloc[0]

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Defect Information**")
                st.write(f"Defect ID: {record['defect_id']}")
                st.write(f"Type: {record['defect_type']}")
                st.write(f"Severity: {record['severity']}")
                st.write(f"Disposition: {record['disposition']}")

                st.markdown("**Inspection Information**")
                st.write(f"Inspection ID: {record['inspection_id']}")
                st.write(f"Inspection Result: {record['inspection_result']}")
                st.write(f"Inspected Units: {record['inspected_quantity']}")
                st.write(f"Defect Units: {record['defect_quantity']}")

            with col2:
                st.markdown("**Production Information**")
                st.write(f"Order ID: {record['order_id']}")
                st.write(f"Product: {record['product_name']}")

                st.markdown("**Material and Supplier**")
                st.write(f"Lot ID: {record['lot_id']}")
                st.write(f"Material: {record['material_name']}")
                st.write(f"Supplier: {record['supplier_name']}")

                st.markdown("**Process and Machine**")
                st.write(f"Process Step: {record['step_name']}")
                st.write(f"Machine: {record['machine_name']}")

            with st.expander("Corrective Action (CAPA) Details", expanded=True):
                st.write(f"CAPA ID: {record['capa_id']}")
                st.write(f"Action: {record['action_description']}")
                st.write(f"Status: {record['capa_status']}")
                st.write(f"Opened At: {record['capa_opened_at']}")
                st.write(f"Closed At: {record['capa_closed_at']}")
                st.write(
                    f"Verification Result: "
                    f"{record['verification_result'] or 'Not verified'}"
                )

    else:
        st.info("No defect records found.")

    # Supplier analysis
    st.divider()
    st.header("Supplier Quality Analysis")

    try:
        supplier_df = load_table("""
            SELECT
                s.supplier_name,
                COUNT(DISTINCT d.defect_id) AS defect_cases
            FROM suppliers s
            LEFT JOIN material_lots l
                ON s.supplier_id = l.supplier_id
            LEFT JOIN defects d
                ON l.lot_id = d.lot_id
            GROUP BY s.supplier_id, s.supplier_name
            ORDER BY defect_cases DESC
        """)

        if not supplier_df.empty:
            st.bar_chart(
                supplier_df.set_index("supplier_name")
            )
            st.dataframe(
                supplier_df,
                use_container_width=True,
                hide_index=True
            )

    except Exception as error:
        st.warning(f"Could not load supplier analysis: {error}")

    # Machine analysis
    st.divider()
    st.header("Machine Quality Analysis")

    try:
        machine_df = load_table("""
            SELECT
                m.machine_name,
                COUNT(DISTINCT d.defect_id) AS defect_cases
            FROM machines m
            LEFT JOIN process_steps ps
                ON m.machine_id = ps.machine_id
            LEFT JOIN defects d
                ON ps.step_id = d.step_id
            GROUP BY m.machine_id, m.machine_name
            ORDER BY defect_cases DESC
        """)

        if not machine_df.empty:
            st.bar_chart(
                machine_df.set_index("machine_name")
            )
            st.dataframe(
                machine_df,
                use_container_width=True,
                hide_index=True
            )

    except Exception as error:
        st.warning(f"Could not load machine analysis: {error}")

    st.divider()
    st.caption(
        "Manufacturing Traceability System | "
        "Synthetic demonstration data"
    )


if __name__ == "__main__":
    main()
