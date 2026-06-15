"""
Maintenance Wizard — FastAPI Backend
AI-powered maintenance decision-support system for industrial equipment.
"""
import json
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.services.vector_store import vector_store
from backend.services.anomaly_detector import anomaly_detector
from backend.routers import chat, equipment, alerts, reports, feedback, knowledge


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup."""
    print("Initializing Maintenance Wizard...")

    # Check and generate synthetic data if missing
    eq_path = os.path.join(settings.DATA_DIR, "equipment.json")
    if not os.path.exists(eq_path):
        print("  Generated data not found. Running synthetic data generator...")
        try:
            os.makedirs(settings.DATA_DIR, exist_ok=True)
            from backend.data.generate_synthetic_data import main as generate_data
            generate_data()
            print("  Synthetic data generated.")
        except Exception as e:
            print(f"  Warning: Synthetic data generation failed: {e}")

    # Ensure predictors are loaded with data/ranges (especially after generation)
    try:
        from backend.services.rul_predictor import rul_predictor
        rul_predictor._load_data()
        anomaly_detector._load_sensor_ranges()
        print("  Predictor and anomaly detector ranges loaded.")
    except Exception as e:
        print(f"  Warning: Failed to load predictor ranges: {e}")

    # Initialize vector store (ingest knowledge base)
    print("  Loading knowledge base into vector store...")
    try:
        vector_store.initialize()
        print("  Vector store initialized.")
    except Exception as e:
        print(f"  Warning: Vector store initialization failed: {e}")

    # Train anomaly detection models
    print("  Training anomaly detection models...")
    try:
        eq_path = os.path.join(settings.DATA_DIR, "equipment.json")
        sensor_path = os.path.join(settings.DATA_DIR, "sensor_data_full.json")
        if os.path.exists(eq_path) and os.path.exists(sensor_path):
            with open(eq_path, "r") as f:
                equipment_list = json.load(f)
            with open(sensor_path, "r") as f:
                sensor_data = json.load(f)
            anomaly_detector.train_models(sensor_data, equipment_list)
            print(f"  Trained models for {len(anomaly_detector.models)} equipment items.")
    except Exception as e:
        print(f"  Warning: Anomaly model training failed: {e}")

    # Warm up analytics cache
    print("  Warming up analytics cache...")
    try:
        await equipment.warm_analytics_cache()
        print("  Analytics cache warmed.")
    except Exception as e:
        print(f"  Warning: Analytics cache warming failed: {e}")

    print("Maintenance Wizard is ready!")
    yield
    print("Shutting down Maintenance Wizard...")


app = FastAPI(
    title="Maintenance Wizard API",
    description="AI-powered maintenance decision-support system for industrial steel plant equipment",
    version="1.0.0",
    lifespan=lifespan
)

# CORS — allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(chat.router)
app.include_router(equipment.router)
app.include_router(alerts.router)
app.include_router(reports.router)
app.include_router(feedback.router)
app.include_router(knowledge.router)


@app.get("/")
async def root():
    return {
        "name": "Maintenance Wizard API",
        "version": "1.0.0",
        "status": "operational",
        "description": "AI-powered maintenance decision-support for industrial equipment"
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "vector_store": vector_store._initialized}
