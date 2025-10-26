# ============================================
# dashboard_optimal_load.py
# Predicción de CARGA ÓPTIMA para TODOS los productos del vuelo
# Nuevas features calculadas en predicción:
#   Spec_per_Passenger, Spec_x_Passengers, IsWeekend, Quarter,
#   Avg_Consumed_Product, Avg_Returned_Product
# Sin Unit_Cost
# ============================================

import streamlit as st
import pandas as pd
import numpy as np
import joblib
from datetime import date

# -------------------------
# 1) Cargar artefactos
# -------------------------
best_model = joblib.load("best_model.pkl")
X_columns  = joblib.load("X_columns.pkl")
metadata   = joblib.load("model_metadata.pkl")

onehot_prefixes      = metadata["onehot_prefixes"]
origin_options       = metadata["origin_options"]
flight_type_options  = metadata["flight_type_options"]
service_type_options = metadata["service_type_options"]
product_id_options   = metadata["product_id_options"]
product_id_to_name   = metadata["product_id_to_name"]
per_product_qty_median = metadata["per_product_qty_median"]
avg_by_product       = metadata["avg_by_product"]  # dict: pid -> {Avg_Consumed_Product, Avg_Returned_Product}

# -------------------------
# 2) UI - Parámetros del vuelo
# -------------------------
st.set_page_config(page_title="Optimal Load (todos los productos)", layout="wide")
st.title("Optimal Food Load — TODOS los productos del vuelo (modelo mejorado)")
st.caption("RandomForest + Optuna (200 trials, CV estratificada por Product_ID).")

c1, c2, c3 = st.columns(3)
flight_date = c1.date_input("Fecha del vuelo", value=date.today())
origin      = c2.selectbox("Origin", origin_options)
flight_type = c3.selectbox("Flight Type", flight_type_options)

c4, c5 = st.columns(2)
service_type = c4.selectbox("Service Type", service_type_options)
passengers   = c5.number_input("Passenger Count", min_value=1, max_value=700, value=180)

st.markdown("---")

# -------------------------
# 3) Tabla editable: cantidades por producto
# -------------------------
rows = []
for pid in product_id_options:
    pname = product_id_to_name.get(pid, "")
    default_qty = int(per_product_qty_median.get(pid, 100))
    rows.append({"Product_ID": pid, "Product_Name": pname, "Proposed_Qty": default_qty})

st.subheader("Cantidades propuestas por producto (edita libremente)")
edit_df = st.data_editor(
    pd.DataFrame(rows),
    key="qty_editor_v2",
    use_container_width=True,
    column_config={
        "Product_ID": st.column_config.TextColumn(disabled=True),
        "Product_Name": st.column_config.TextColumn(disabled=True),
        "Proposed_Qty": st.column_config.NumberColumn(min_value=0, step=5),
    }
)

# -------------------------
# 4) Construcción de batch con features nuevas
# -------------------------
def build_rows(shared, table_df, X_cols, prefixes, avg_map):
    """
    shared: dict con Origin, Flight_Type, Service_Type, Passenger_Count, Month, DayOfWeek, IsWeekend, Quarter
    table_df: DataFrame con Product_ID y Proposed_Qty
    avg_map: dict Product_ID -> {Avg_Consumed_Product, Avg_Returned_Product}
    """
    rows = []
    for _, r in table_df.iterrows():
        pid = str(r["Product_ID"])
        qty = float(r["Proposed_Qty"])

        row = {c: 0 for c in X_cols}

        # Numéricas base + derivadas
        row["Passenger_Count"]            = float(shared["Passenger_Count"])
        row["Standard_Specification_Qty"] = float(qty)
        row["Month"]      = float(shared["Month"])
        row["DayOfWeek"]  = float(shared["DayOfWeek"])
        row["IsWeekend"]  = float(shared["IsWeekend"])
        row["Quarter"]    = float(shared["Quarter"])

        # Features por producto (históricas)
        avg_rec = avg_map.get(pid, {"Avg_Consumed_Product": 0.0, "Avg_Returned_Product": 0.0})
        row["Avg_Consumed_Product"] = float(avg_rec.get("Avg_Consumed_Product", 0.0))
        row["Avg_Returned_Product"] = float(avg_rec.get("Avg_Returned_Product", 0.0))

        # Interacciones
        # (usar el mismo eps que en training para evitar div/0)
        eps = 1e-9
        row["Spec_per_Passenger"] = row["Standard_Specification_Qty"] / (row["Passenger_Count"] + eps)
        row["Spec_x_Passengers"]  = row["Standard_Specification_Qty"] *  row["Passenger_Count"]

        # One-hots compartidos
        def set_onehot(prefix, value):
            colname = f"{prefix}{value}"
            if colname in row:
                row[colname] = 1

        set_onehot(prefixes["Origin"],      shared["Origin"])
        set_onehot(prefixes["Flight_Type"], shared["Flight_Type"])
        set_onehot(prefixes["Service_Type"],shared["Service_Type"])

        # Product_ID one-hot
        set_onehot(prefixes["Product_ID"], pid)

        rows.append(row)

    return pd.DataFrame(rows, columns=X_cols)

# Derivados de fecha
Month = int(pd.to_datetime(flight_date).month)
DayOfWeek = int(pd.to_datetime(flight_date).dayofweek)
IsWeekend = 1 if DayOfWeek in [5, 6] else 0
Quarter = (Month - 1)//3 + 1

shared = {
    "Origin": origin,
    "Flight_Type": flight_type,
    "Service_Type": service_type,
    "Passenger_Count": passengers,
    "Month": Month,
    "DayOfWeek": DayOfWeek,
    "IsWeekend": IsWeekend,
    "Quarter": Quarter,
}

X_batch = build_rows(shared, edit_df[["Product_ID","Proposed_Qty"]], X_columns, onehot_prefixes, avg_by_product)

# -------------------------
# 5) Predicción en lote y presentación
# -------------------------
preds = best_model.predict(X_batch).astype(float)

results = edit_df.copy()
results["Optimal_Load_Pred"] = preds
results["Diff_(Optimal-Prop)"] = results["Optimal_Load_Pred"] - results["Proposed_Qty"]

st.subheader("Recomendación de carga óptima — TODOS los productos")
st.dataframe(results, hide_index=True, use_container_width=True)

st.bar_chart(results.set_index("Product_ID")[["Proposed_Qty","Optimal_Load_Pred"]])

st.markdown("---")
cA, cB, cC = st.columns(3)
cA.metric("Total propuesto", f"{results['Proposed_Qty'].sum():,.0f}")
cB.metric("Total óptimo",   f"{results['Optimal_Load_Pred'].sum():,.0f}")
cC.metric("Óptimo - Propuesto", f"{results['Diff_(Optimal-Prop)'].sum():,.0f}")

csv_all = results.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Descargar resultados (CSV)",
    data=csv_all,
    file_name=f"optimal_load_all_products_{origin}_{flight_type}_{service_type}.csv",
    mime="text/csv",
)