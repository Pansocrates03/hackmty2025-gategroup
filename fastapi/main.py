from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import joblib
import pandas as pd
import numpy as np
from datetime import datetime

# Inicializar FastAPI
app = FastAPI(title="Optimal Load Prediction API")

# Configurar CORS para permitir requests desde tu frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica tu dominio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cargar modelos al iniciar la aplicación
try:
    best_model = joblib.load("best_model.pkl")
    X_columns = joblib.load("X_columns.pkl")
    metadata = joblib.load("model_metadata.pkl")
    
    onehot_prefixes = metadata["onehot_prefixes"]
    avg_by_product = metadata["avg_by_product"]
    
    print("✅ Modelos cargados exitosamente")
except Exception as e:
    print(f"❌ Error cargando modelos: {e}")
    raise

# Modelos de datos
class Product(BaseModel):
    id: str
    name: str
    proposedQty: int

class PredictionRequest(BaseModel):
    products: List[Product]
    flightDate: str
    origin: str
    flightType: str
    serviceType: str
    passengers: int

class PredictionResult(BaseModel):
    id: str
    name: str
    proposedQty: int
    optimal: int
    diff: int

# Función para construir features
def build_feature_rows(shared: Dict[str, Any], products: List[Product], 
                       X_cols: List[str], prefixes: Dict[str, str], 
                       avg_map: Dict[str, Dict[str, float]]) -> pd.DataFrame:
    """
    Construye el DataFrame de features para predicción
    """
    rows = []
    eps = 1e-9
    
    for product in products:
        pid = str(product.id)
        qty = float(product.proposedQty)
        
        # Inicializar row con ceros
        row = {c: 0.0 for c in X_cols}
        
        # Features numéricas base
        row["Passenger_Count"] = float(shared["Passenger_Count"])
        row["Standard_Specification_Qty"] = float(qty)
        row["Month"] = float(shared["Month"])
        row["DayOfWeek"] = float(shared["DayOfWeek"])
        row["IsWeekend"] = float(shared["IsWeekend"])
        row["Quarter"] = float(shared["Quarter"])
        
        # Features históricas por producto
        avg_rec = avg_map.get(pid, {
            "Avg_Consumed_Product": 0.0, 
            "Avg_Returned_Product": 0.0
        })
        row["Avg_Consumed_Product"] = float(avg_rec.get("Avg_Consumed_Product", 0.0))
        row["Avg_Returned_Product"] = float(avg_rec.get("Avg_Returned_Product", 0.0))
        
        # Features de interacción
        row["Spec_per_Passenger"] = row["Standard_Specification_Qty"] / (row["Passenger_Count"] + eps)
        row["Spec_x_Passengers"] = row["Standard_Specification_Qty"] * row["Passenger_Count"]
        
        # One-hot encoding
        def set_onehot(prefix: str, value: str):
            colname = f"{prefix}{value}"
            if colname in row:
                row[colname] = 1.0
        
        set_onehot(prefixes["Origin"], shared["Origin"])
        set_onehot(prefixes["Flight_Type"], shared["Flight_Type"])
        set_onehot(prefixes["Service_Type"], shared["Service_Type"])
        set_onehot(prefixes["Product_ID"], pid)
        
        rows.append(row)
    
    return pd.DataFrame(rows, columns=X_cols)

# Endpoint de health check
@app.get("/")
def read_root():
    return {
        "status": "ok",
        "message": "Optimal Load Prediction API is running",
        "model_loaded": best_model is not None
    }

# Endpoint de predicción
@app.post("/api/predict", response_model=List[PredictionResult])
async def predict(request: PredictionRequest):
    """
    Endpoint principal para predicción de carga óptima
    """
    try:
        # Parsear fecha y calcular features temporales
        flight_date = datetime.strptime(request.flightDate, "%Y-%m-%d")
        month = int(flight_date.month)
        day_of_week = int(flight_date.weekday())
        is_weekend = 1 if day_of_week in [5, 6] else 0
        quarter = (month - 1) // 3 + 1
        
        # Preparar datos compartidos
        shared = {
            "Origin": request.origin,
            "Flight_Type": request.flightType,
            "Service_Type": request.serviceType,
            "Passenger_Count": request.passengers,
            "Month": month,
            "DayOfWeek": day_of_week,
            "IsWeekend": is_weekend,
            "Quarter": quarter,
        }
        
        # Construir features
        X_batch = build_feature_rows(
            shared, 
            request.products, 
            X_columns, 
            onehot_prefixes, 
            avg_by_product
        )
        
        # Hacer predicción
        predictions = best_model.predict(X_batch)
        
        # Preparar resultados
        results = []
        for i, product in enumerate(request.products):
            optimal = int(round(predictions[i]))
            diff = optimal - product.proposedQty
            
            results.append(PredictionResult(
                id=product.id,
                name=product.name,
                proposedQty=product.proposedQty,
                optimal=optimal,
                diff=diff
            ))
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en predicción: {str(e)}")

# Endpoint para obtener metadatos del modelo
@app.get("/api/metadata")
def get_metadata():
    """
    Retorna información sobre el modelo y opciones disponibles
    """
    return {
        "origin_options": metadata.get("origin_options", []),
        "flight_type_options": metadata.get("flight_type_options", []),
        "service_type_options": metadata.get("service_type_options", []),
        "product_id_options": metadata.get("product_id_options", []),
        "product_id_to_name": metadata.get("product_id_to_name", {}),
        "per_product_qty_median": metadata.get("per_product_qty_median", {})
    }

# Para ejecutar con: uvicorn main:app --reload --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)