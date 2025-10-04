"""
FastAPI application for Bitcoin price prediction
Production ML serving API
"""
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel, Field  # noqa

from src.serving.model_manager import ModelManager
from src.serving.prediction_pipeline import PredictionPipeline
from src.shared.logging import get_logger, setup_logging

# Initialize logging
setup_logging()
logger = get_logger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Bitcoin Sentiment Price Prediction API",
    description="ML-powered Bitcoin price direction prediction using sentiment analysis",
    default_response_class=ORJSONResponse,
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
prediction_pipeline = PredictionPipeline(target_db="local")
model_manager = ModelManager()


# Response models
class PredictionResponse(BaseModel):
    success: bool
    prediction: Optional[Dict[str, Any]] = None
    model_info: Optional[Dict[str, Any]] = None
    performance: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    models_loaded: int


class ModelsListResponse(BaseModel):
    available_models: Dict[str, list]


# Endpoints
@app.get("/", tags=["General"])
async def root():
    """API root endpoint"""
    return {
        "message": "Bitcoin Sentiment Price Prediction API",
        "version": "1.0.0",
        "endpoints": {
            "predict": "/predict",
            "predict_both": "/predict/both",
            "health": "/health",
            "models": "/models"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models_loaded": len(model_manager.loaded_models)
    }


@app.get("/models", response_model=ModelsListResponse, tags=["Models"])
async def list_models():
    """List all available models"""
    try:
        available = model_manager.list_available_models()
        return {"available_models": available}
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict", response_model=PredictionResponse, tags=["Predictions"])
async def predict(
    feature_set: str = Query(
        "vader",
        description="Feature set to use: 'vader' or 'finbert'",
        regex="^(vader|finbert)$"
    ),
    model_type: str = Query(
        "random_forest",
        description="Model type: 'logistic_regression', 'random_forest', 'gradient_boosting'",
        regex="^(logistic_regression|random_forest|gradient_boosting)$"
    ),
    use_cached_features: bool = Query(
        True,
        description="Use pre-computed features (faster) or compute on-demand"
    )
):
    """
    Generate Bitcoin price direction prediction
    
    Returns prediction for 1-hour ahead price movement (up/down)
    """
    try:
        logger.info(f"Prediction request: {feature_set}, {model_type}")
        
        result = prediction_pipeline.predict(
            feature_set=feature_set,
            model_type=model_type,
            use_cached_features=use_cached_features
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/both", tags=["Predictions"])
async def predict_both():
    """
    Generate predictions from both VADER and FinBERT models
    Useful for comparison and ensemble predictions
    """
    try:
        logger.info("Prediction request: both models")
        
        result = prediction_pipeline.predict_both_models()
        
        return result
        
    except Exception as e:
        logger.error(f"Both models prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/models/reload", tags=["Models"])
async def reload_model(
    feature_set: str = Query(..., regex="^(vader|finbert)$"),
    model_type: str = Query(..., regex="^(logistic_regression|random_forest|gradient_boosting)$")
):
    """
    Reload a model (hot-swap for updates)
    """
    try:
        logger.info(f"Reloading model: {feature_set}/{model_type}")
        
        model_info = model_manager.reload_model(feature_set, model_type)
        
        return {
            "success": True,
            "message": f"Model reloaded: {feature_set}/{model_type}",
            "version": model_info['version'],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Model reload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    logger.info("Starting Bitcoin Prediction API...")
    
    # Pre-load default models
    try:
        model_manager.load_model('vader', 'random_forest')
        logger.info("Preloaded VADER Random Forest model")
    except Exception as e:
        logger.warning(f"Could not preload VADER model: {e}")
    
    try:
        model_manager.load_model('finbert', 'random_forest')
        logger.info("Preloaded FinBERT Random Forest model")
    except Exception as e:
        logger.warning(f"Could not preload FinBERT model: {e}")
    
    logger.info("API startup complete")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Bitcoin Prediction API...")