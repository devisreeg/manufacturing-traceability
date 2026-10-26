
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS products (
    product_id TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id TEXT PRIMARY KEY,
    supplier_name TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'ACTIVE'
        CHECK (status IN ('ACTIVE', 'INACTIVE'))
);

CREATE TABLE IF NOT EXISTS bom (
    bom_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id TEXT NOT NULL,
    material_name TEXT NOT NULL,
    quantity_required REAL NOT NULL CHECK (quantity_required > 0),
    effective_from TEXT NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    UNIQUE (product_id, material_name, effective_from)
);

CREATE TABLE IF NOT EXISTS material_lots (
    lot_id TEXT PRIMARY KEY,
    supplier_id TEXT NOT NULL,
    material_name TEXT NOT NULL,
    quantity_received REAL NOT NULL CHECK (quantity_received >= 0),
    received_date TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'AVAILABLE'
        CHECK (status IN ('AVAILABLE', 'CONSUMED', 'QUARANTINED')),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);

CREATE TABLE IF NOT EXISTS machines (
    machine_id TEXT PRIMARY KEY,
    machine_name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'ACTIVE'
        CHECK (status IN ('ACTIVE', 'MAINTENANCE', 'INACTIVE'))
);

CREATE TABLE IF NOT EXISTS production_orders (
    order_id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL,
    planned_quantity INTEGER NOT NULL CHECK (planned_quantity > 0),
    produced_quantity INTEGER NOT NULL DEFAULT 0
        CHECK (produced_quantity >= 0),
    start_date TEXT NOT NULL,
    end_date TEXT,
    status TEXT NOT NULL DEFAULT 'PLANNED'
        CHECK (status IN ('PLANNED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    CHECK (end_date IS NULL OR end_date >= start_date)
);

CREATE TABLE IF NOT EXISTS order_material_consumption (
    consumption_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT NOT NULL,
    lot_id TEXT NOT NULL,
    quantity_used REAL NOT NULL CHECK (quantity_used > 0),
    FOREIGN KEY (order_id) REFERENCES production_orders(order_id),
    FOREIGN KEY (lot_id) REFERENCES material_lots(lot_id)
);

CREATE TABLE IF NOT EXISTS process_steps (
    step_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    machine_id TEXT NOT NULL,
    step_name TEXT NOT NULL,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    status TEXT NOT NULL
        CHECK (status IN ('PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED')),
    FOREIGN KEY (order_id) REFERENCES production_orders(order_id),
    FOREIGN KEY (machine_id) REFERENCES machines(machine_id),
    CHECK (ended_at IS NULL OR ended_at >= started_at)
);

CREATE TABLE IF NOT EXISTS inspection_plans (
    plan_id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL,
    inspection_name TEXT NOT NULL,
    acceptable_defect_rate REAL NOT NULL
        CHECK (acceptable_defect_rate >= 0 AND acceptable_defect_rate <= 1),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE IF NOT EXISTS inspection_results (
    inspection_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    plan_id TEXT NOT NULL,
    inspected_quantity INTEGER NOT NULL CHECK (inspected_quantity > 0),
    defect_quantity INTEGER NOT NULL CHECK (defect_quantity >= 0),
    inspected_at TEXT NOT NULL,
    result TEXT NOT NULL CHECK (result IN ('PASS', 'FAIL')),
    FOREIGN KEY (order_id) REFERENCES production_orders(order_id),
    FOREIGN KEY (plan_id) REFERENCES inspection_plans(plan_id),
    CHECK (defect_quantity <= inspected_quantity)
);

CREATE TABLE IF NOT EXISTS defects (
    defect_id TEXT PRIMARY KEY,
    inspection_id TEXT NOT NULL,
    order_id TEXT NOT NULL,
    lot_id TEXT,
    step_id TEXT,
    defect_type TEXT NOT NULL,
    severity TEXT NOT NULL
        CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    disposition TEXT NOT NULL
        CHECK (disposition IN ('REWORK', 'SCRAP', 'USE_AS_IS', 'PENDING')),
    detected_at TEXT NOT NULL,
    FOREIGN KEY (inspection_id) REFERENCES inspection_results(inspection_id),
    FOREIGN KEY (order_id) REFERENCES production_orders(order_id),
    FOREIGN KEY (lot_id) REFERENCES material_lots(lot_id),
    FOREIGN KEY (step_id) REFERENCES process_steps(step_id)
);

CREATE TABLE IF NOT EXISTS corrective_actions (
    capa_id TEXT PRIMARY KEY,
    defect_id TEXT NOT NULL,
    action_description TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'OPEN'
        CHECK (status IN ('OPEN', 'IN_PROGRESS', 'PENDING_VERIFICATION', 'CLOSED')),
    opened_at TEXT NOT NULL,
    closed_at TEXT,
    verification_result TEXT
        CHECK (
            verification_result IS NULL
            OR verification_result IN ('PASS', 'FAIL')
        ),
    FOREIGN KEY (defect_id) REFERENCES defects(defect_id),
    CHECK (
        status != 'CLOSED'
        OR (
            closed_at IS NOT NULL
            AND verification_result = 'PASS'
        )
    ),
    CHECK (closed_at IS NULL OR closed_at >= opened_at)
);

CREATE TABLE IF NOT EXISTS event_history (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    event_details TEXT NOT NULL,
    event_time TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_orders_product
    ON production_orders(product_id);

CREATE INDEX IF NOT EXISTS idx_lots_supplier
    ON material_lots(supplier_id);

CREATE INDEX IF NOT EXISTS idx_consumption_order
    ON order_material_consumption(order_id);

CREATE INDEX IF NOT EXISTS idx_inspections_order
    ON inspection_results(order_id);

CREATE INDEX IF NOT EXISTS idx_defects_order
    ON defects(order_id);

CREATE INDEX IF NOT EXISTS idx_capa_status
    ON corrective_actions(status);
