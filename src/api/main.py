"""
FastAPI Application for Bitcoin Sentiment Price Prediction
Production-grade ML model serving with prediction logging
"""

import os
from datetime import datetime
from typing import Optional

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Integer

from src.mlops.prediction_logger import PredictionLogger
from src.serving.model_manager import ModelManager
from src.serving.prediction_pipeline import PredictionPipeline
from src.shared.database import SessionLocal
from src.shared.logging import get_logger

# Initialize logger
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Bitcoin Sentiment Price Prediction API",
    description="Production ML API for Bitcoin price prediction using sentiment analysis",
    version="1.0.0"
)

'''Local Deployment'''
# # Add CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # In production, specify actual origins
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

'''Deolpyment on Render.com'''
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
model_manager = ModelManager()
prediction_pipeline = PredictionPipeline()
prediction_logger = PredictionLogger()

def convert_numpy_types(obj):
    """Convert numpy types to Python native types for JSON serialization"""
    if isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj


@app.on_event("startup")
async def startup_event():
    """Pre-load best models on startup"""
    logger.info("Starting FastAPI application...")
    logger.info("Pre-loading best available models...")
    
    try:
        # Get best models dynamically
        from pathlib import Path
        import json
        
        def get_best_model(feature_set):
            models_dir = Path(f"models/saved_models/{feature_set}")
            best_model = None
            best_accuracy = -1
            
            for model_dir in models_dir.iterdir():
                if not model_dir.is_dir():
                    continue
                metadata_files = list(model_dir.glob("metadata_*.json"))
                if metadata_files:
                    latest_meta = max(metadata_files, key=lambda p: p.stem.split('_')[1])
                    with open(latest_meta) as f:
                        meta = json.load(f)
                    val_acc = meta.get('validation_metrics', {}).get('accuracy', 0)
                    if val_acc > best_accuracy:
                        best_accuracy = val_acc
                        best_model = model_dir.name
            return best_model
        
        vader_best = get_best_model('vader')
        finbert_best = get_best_model('finbert')
        
        if vader_best:
            model_manager.load_model('vader', vader_best)
            logger.info(f"✅ Loaded VADER {vader_best} model")
        
        if finbert_best:
            model_manager.load_model('finbert', finbert_best)
            logger.info(f"✅ Loaded FinBERT {finbert_best} model")
        
        logger.info("FastAPI application ready")
    except Exception as e:
        logger.error(f"Error during startup: {e}")


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Bitcoin Sentiment Price Prediction API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "models": "/models",
            "predict": "/predict",
            "predict_both": "/predict/both",
            "reload_model": "/models/reload",
            "recent_predictions": "/predictions/recent",
            "model_accuracy": "/predictions/accuracy",
            "statistics": "/predictions/statistics",
            "drift_features": "/drift/features",
            "drift_model": "/drift/model",
            "drift_summary": "/drift/summary",
            "retrain_check": "/retrain/check",
            "retrain_execute": "/retrain/execute",
            "retrain_both": "/retrain/both",
            "retrain_status": "/retrain/status"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "loaded_models": len(model_manager.loaded_models)
    }
    
@app.get("/price/recent")
async def get_recent_prices(
    symbol: str = Query("BTC", description="Cryptocurrency symbol"),
    hours: int = Query(24, description="Hours of price data to return"),
    limit: int = Query(100, description="Maximum number of data points")
):
    """
    Get recent price data for charting
    
    Returns recent price history for real-time charting
    """
    try:
        from datetime import datetime, timedelta

        from src.shared.models import PriceData
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        with SessionLocal() as db:
            prices = db.query(PriceData).filter(
                PriceData.symbol == symbol,
                PriceData.collected_at >= cutoff_time
            ).order_by(
                PriceData.collected_at.asc()
            ).limit(limit).all()
            
            price_data = [
                {
                    'timestamp': price.collected_at.isoformat(),
                    'price': float(price.price_usd),
                    'volume_24h': float(price.volume_24h) if price.volume_24h else None,
                    'change_24h': float(price.change_24h) if price.change_24h else None,
                }
                for price in prices
            ]
            
            return {
                'success': True,
                'symbol': symbol,
                'hours': hours,
                'count': len(price_data),
                'latest_price': price_data[-1]['price'] if price_data else None,
                'latest_timestamp': price_data[-1]['timestamp'] if price_data else None,
                'data': price_data
            }
            
    except Exception as e:
        logger.error(f"Failed to get recent prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/sentiment/timeline")
async def get_sentiment_timeline(
    hours: int = Query(24, description="Hours of sentiment data to return"),
    limit: int = Query(100, description="Maximum number of data points")
):
    """
    Get sentiment score timeline for both VADER and FinBERT
    
    Returns hourly sentiment scores for charting
    """
    try:
        from datetime import datetime, timedelta

        from src.shared.models import SentimentData
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        with SessionLocal() as db:
            # Get all sentiment data in the time range
            sentiment_records = db.query(SentimentData).filter(
                SentimentData.processed_at >= cutoff_time
            ).order_by(
                SentimentData.processed_at.asc()
            ).limit(limit).all()
            
            vader_data = []
            finbert_data = []
            
            for record in sentiment_records:
                timestamp = record.processed_at.isoformat()
                
                # VADER score (compound score from -1 to 1)
                vader_data.append({
                    'timestamp': timestamp,
                    'score': float(record.vader_compound)
                })
                
                # FinBERT score (if available)
                if record.finbert_compound is not None:
                    finbert_data.append({
                        'timestamp': timestamp,
                        'score': float(record.finbert_compound)
                    })
            
            # Get latest scores
            latest_vader = vader_data[-1]['score'] if vader_data else None
            latest_finbert = finbert_data[-1]['score'] if finbert_data else None
            
            return {
                'success': True,
                'hours': hours,
                'vader': {
                    'count': len(vader_data),
                    'latest_score': latest_vader,
                    'data': vader_data
                },
                'finbert': {
                    'count': len(finbert_data),
                    'latest_score': latest_finbert,
                    'data': finbert_data
                }
            }
            
    except Exception as e:
        logger.error(f"Failed to get sentiment timeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/predictions/accuracy-timeline")
async def get_prediction_accuracy_timeline(
    hours: int = Query(24, description="Hours of accuracy data to return")
):
    """
    Get prediction accuracy timeline for both models
    
    Returns hourly rolling accuracy for VADER and FinBERT
    """
    try:
        from datetime import datetime, timedelta

        # from sqlalchemy import func, and_
        from src.shared.models import PredictionLog
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        with SessionLocal() as db:
            # Calculate accuracy in hourly windows
            # This groups predictions by hour and calculates accuracy per hour
            
            vader_accuracy = []
            finbert_accuracy = []
            
            # Get all predictions in the time range with outcomes
            vader_preds = db.query(PredictionLog).filter(
                PredictionLog.feature_set == 'vader',
                PredictionLog.predicted_at >= cutoff_time,
                PredictionLog.actual_direction.isnot(None)
            ).order_by(PredictionLog.predicted_at.asc()).all()
            
            finbert_preds = db.query(PredictionLog).filter(
                PredictionLog.feature_set == 'finbert',
                PredictionLog.predicted_at >= cutoff_time,
                PredictionLog.actual_direction.isnot(None)
            ).order_by(PredictionLog.predicted_at.asc()).all()
            
            # Calculate rolling accuracy (last 10 predictions window)
            window_size = 10
            
            for i in range(len(vader_preds)):
                if i >= window_size - 1:
                    window_preds = vader_preds[i - window_size + 1:i + 1]
                    correct = sum(1 for p in window_preds if p.prediction_correct)
                    accuracy = correct / window_size
                    vader_accuracy.append({
                        'timestamp': vader_preds[i].predicted_at.isoformat(),
                        'accuracy': accuracy,
                        'window_size': window_size
                    })
            
            for i in range(len(finbert_preds)):
                if i >= window_size - 1:
                    window_preds = finbert_preds[i - window_size + 1:i + 1]
                    correct = sum(1 for p in window_preds if p.prediction_correct)
                    accuracy = correct / window_size
                    finbert_accuracy.append({
                        'timestamp': finbert_preds[i].predicted_at.isoformat(),
                        'accuracy': accuracy,
                        'window_size': window_size
                    })
            
            return {
                'success': True,
                'hours': hours,
                'vader_accuracy': vader_accuracy,
                'finbert_accuracy': finbert_accuracy
            }
            
    except Exception as e:
        logger.error(f"Failed to get prediction accuracy timeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/models")
async def list_models():
    """List all available models"""
    return {
        "available_models": model_manager.list_available_models()
    }


@app.post("/predict")
async def predict(
    feature_set: str = Query(..., description="Feature set: 'vader' or 'finbert'"),
    model_type: str = Query(..., description="Model type"),
    use_cached_features: bool = Query(True, description="Use cached features")
):
    """Make a prediction with specified model"""
    import time
    start_time = time.time()
    
    try:
        # Validate feature_set
        if feature_set not in ['vader', 'finbert']:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid feature_set: {feature_set}. Must be 'vader' or 'finbert'"
            )
        
        # Get features first (for logging)
        from src.serving.feature_server import FeatureServer
        feature_server = FeatureServer()
        
        if use_cached_features:
            features = feature_server.get_latest_features(feature_set, 'neondb_production')
        else:
            features = feature_server.compute_features_on_demand(feature_set, 'neondb_production')
        
        # Convert Series to dict for JSON storage
        if features is not None:
            features_dict = features.to_dict()
            
            # Convert non-JSON-serializable types
            for key, value in features_dict.items():
                if pd.isna(value):
                    features_dict[key] = None
                elif isinstance(value, pd.Timestamp):
                    features_dict[key] = value.isoformat()  # Convert to ISO string
                elif isinstance(value, (pd.Int64Dtype, pd.Float64Dtype)):
                    features_dict[key] = float(value)
        else:
            features_dict = {}
            
        bitcoin_price = features_dict.get('price_usd') if features_dict else None
        
        
        
        # Make prediction
        result = prediction_pipeline.predict(
            feature_set=feature_set,
            model_type=model_type,
            use_cached_features=use_cached_features
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Prediction failed')
            )
        
        # Calculate response time
        response_time_ms = (time.time() - start_time) * 1000
        result['performance']['response_time_ms'] = response_time_ms
        
        # Get model accuracy
        accuracy_stats = prediction_logger.get_model_accuracy(
            feature_set=feature_set,
            model_type=model_type,
            days=7
        )
        model_accuracy = accuracy_stats.get('accuracy') if accuracy_stats else None
        
        # Add accuracy to result
        result['prediction']['accuracy'] = model_accuracy
        result['prediction']['accuracy_period'] = '7 days'
        if 'confidence' in result['prediction']:
            del result['prediction']['confidence']
        
        # Log prediction with actual features
        try:
            prediction_id = prediction_logger.log_prediction(
                feature_set=feature_set,
                model_type=model_type,
                model_version=result['model_info']['model_version'],
                prediction=result['prediction']['direction_numeric'],
                probability_down=result['prediction']['probability']['down'],
                probability_up=result['prediction']['probability']['up'],
                confidence=max(result['prediction']['probability']['down'], 
                              result['prediction']['probability']['up']),
                features=features_dict, 
                response_time_ms=response_time_ms,
                cached_features=use_cached_features,
                bitcoin_price=bitcoin_price
            )
            
            result['prediction_id'] = prediction_id
            logger.info(f"Prediction logged with ID: {prediction_id}")
            
        except Exception as log_error:
            logger.error(f"Failed to log prediction: {log_error}")
            result['prediction_id'] = None
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/both")
async def predict_both(
    use_cached_features: bool = Query(True, description="Use cached features (faster) or compute on-demand")
):
    """
    Make predictions with both VADER and FinBERT models for comparison
    
    **Now with automatic prediction logging for both models**
    """
    import time
    start_time = time.time()
    
    try:
        # Make predictions with both models
        result = prediction_pipeline.predict_both_models(
            use_cached_features=use_cached_features
        )
        
        # Get accuracies for both models
        vader_accuracy_stats = prediction_logger.get_model_accuracy('vader', 'random_forest', days=7)
        finbert_accuracy_stats = prediction_logger.get_model_accuracy('finbert', 'random_forest', days=7)
        
        vader_accuracy = vader_accuracy_stats.get('accuracy') if vader_accuracy_stats else None
        finbert_accuracy = finbert_accuracy_stats.get('accuracy') if finbert_accuracy_stats else None
        
        # Add accuracy to results and remove confidence
        if result['vader']['success']:
            result['vader']['prediction']['accuracy'] = vader_accuracy
            result['vader']['prediction']['accuracy_period'] = '7 days'
            if 'confidence' in result['vader']['prediction']:
                del result['vader']['prediction']['confidence']
        
        if result['finbert']['success']:
            result['finbert']['prediction']['accuracy'] = finbert_accuracy
            result['finbert']['prediction']['accuracy_period'] = '7 days'
            if 'confidence' in result['finbert']['prediction']:
                del result['finbert']['prediction']['confidence']
        
        # Calculate total response time
        total_response_time_ms = (time.time() - start_time) * 1000
        result['performance']['total_response_time_ms'] = total_response_time_ms
        
        # Log VADER prediction
        if result['vader']['success']:
            try:
                vader_bitcoin_price = result['vader']['model_info'].get('features_dict', {}).get('price_usd')
                
                vader_id = prediction_logger.log_prediction(
                    feature_set='vader',
                    model_type='random_forest',
                    model_version=result['vader']['model_info']['model_version'],
                    prediction=result['vader']['prediction']['direction_numeric'],
                    probability_down=result['vader']['prediction']['probability']['down'],
                    probability_up=result['vader']['prediction']['probability']['up'],
                    confidence=result['vader']['prediction']['confidence'],
                    features=result['vader']['model_info'].get('features_dict', {}),
                    response_time_ms=total_response_time_ms / 2,  # Approximate
                    cached_features=use_cached_features,
                    bitcoin_price=vader_bitcoin_price
                )
                result['vader']['prediction_id'] = vader_id
                
            except Exception as log_error:
                logger.error(f"Failed to log VADER prediction: {log_error}")
                result['vader']['prediction_id'] = None
        
        # Log FinBERT prediction
        if result['finbert']['success']:
            try:
                finbert_bitcoin_price = result['finbert']['model_info'].get('features_dict', {}).get('price_usd')
                
                finbert_id = prediction_logger.log_prediction(
                    feature_set='finbert',
                    model_type='random_forest',
                    model_version=result['finbert']['model_info']['model_version'],
                    prediction=result['finbert']['prediction']['direction_numeric'],
                    probability_down=result['finbert']['prediction']['probability']['down'],
                    probability_up=result['finbert']['prediction']['probability']['up'],
                    confidence=result['finbert']['prediction']['confidence'],
                    features=result['finbert']['model_info'].get('features_dict', {}),
                    response_time_ms=total_response_time_ms / 2,  # Approximate
                    cached_features=use_cached_features,
                    bitcoin_price=finbert_bitcoin_price
                )
                result['finbert']['prediction_id'] = finbert_id
                
            except Exception as log_error:
                logger.error(f"Failed to log FinBERT prediction: {log_error}")
                result['finbert']['prediction_id'] = None
        
        return result
        
    except Exception as e:
        logger.error(f"Dual prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/models/reload")
async def reload_model(
    feature_set: str = Query(..., description="Feature set: 'vader' or 'finbert'"),
    model_type: str = Query(..., description="Model type to reload")
):
    """Reload a model (hot-swap without server restart)"""
    try:
        model_info = model_manager.reload_model(feature_set, model_type)
        return {
            "success": True,
            "message": "Model reloaded successfully",
            "model_info": model_info
        }
    except Exception as e:
        logger.error(f"Model reload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/predictions/recent")
async def get_recent_predictions(
    feature_set: Optional[str] = Query(None, description="Filter by feature set"),
    model_type: Optional[str] = Query(None, description="Filter by model type"),
    limit: int = Query(100, description="Maximum number of predictions to return"),
    only_with_outcomes: bool = Query(False, description="Only return predictions with recorded outcomes")
):
    """
    Get recent predictions for monitoring
    
    **New MLOps endpoint for prediction history**
    """
    try:
        predictions = prediction_logger.get_recent_predictions(
            feature_set=feature_set,
            model_type=model_type,
            limit=limit,
            only_with_outcomes=only_with_outcomes
        )
        
        return {
            "success": True,
            "count": len(predictions),
            "predictions": predictions,
            "filters": {
                "feature_set": feature_set,
                "model_type": model_type,
                "only_with_outcomes": only_with_outcomes
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get recent predictions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/predictions/accuracy")
async def get_model_accuracy(
    feature_set: str = Query(..., description="Feature set: 'vader' or 'finbert'"),
    model_type: str = Query(..., description="Model type"),
    days: int = Query(7, description="Number of days to analyze")
):
    """
    Get model accuracy over specified time period
    
    **New MLOps endpoint for accuracy tracking**
    """
    try:
        accuracy_stats = prediction_logger.get_model_accuracy(
            feature_set=feature_set,
            model_type=model_type,
            days=days
        )
        
        return {
            "success": True,
            "accuracy_stats": accuracy_stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get model accuracy: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/predictions/daily-accuracy")
async def get_daily_accuracy(
    feature_set: str = Query(..., description="Feature set: 'vader' or 'finbert'"),
    model_type: str = Query("random_forest", description="Model type"),
    days: int = Query(7, description="Number of days to analyze")
):
    """
    Get daily accuracy breakdown for chart visualization
    
    Returns accuracy by day for the specified period
    """
    try:
        from datetime import datetime, timedelta

        from sqlalchemy import Date, cast, func

        from src.shared.models import PredictionLog
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        with SessionLocal() as db:
            # Query daily accuracy
            daily_stats = db.query(
                cast(PredictionLog.predicted_at, Date).label('date'),
                func.count(PredictionLog.id).label('total'),
                func.sum(
                    func.cast(PredictionLog.prediction_correct, Integer)
                ).label('correct')
            ).filter(
                PredictionLog.feature_set == feature_set,
                PredictionLog.model_type == model_type,
                PredictionLog.predicted_at >= cutoff_date,
                PredictionLog.actual_direction.isnot(None)
            ).group_by(
                cast(PredictionLog.predicted_at, Date)
            ).order_by(
                cast(PredictionLog.predicted_at, Date)
            ).all()
            
            # Format results
            results = []
            for stat in daily_stats:
                accuracy = stat.correct / stat.total if stat.total > 0 else None
                results.append({
                    'date': stat.date.strftime('%Y-%m-%d'),
                    'accuracy': accuracy,
                    'predictions': stat.total,
                    'correct': stat.correct
                })
            
            return {
                'success': True,
                'feature_set': feature_set,
                'model_type': model_type,
                'days': days,
                'daily_accuracy': results
            }
            
    except Exception as e:
        logger.error(f"Failed to get daily accuracy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/predictions/statistics")
async def get_prediction_statistics():
    """
    Get overall prediction statistics
    
    **New MLOps endpoint for system-wide statistics**
    """
    try:
        stats = prediction_logger.get_prediction_statistics()
        
        return {
            "success": True,
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/drift/features")
async def detect_feature_drift(
    feature_set: str = Query(..., description="Feature set: 'vader' or 'finbert'"),
    reference_days: int = Query(7, description="Days for reference period"),
    current_days: int = Query(1, description="Days for current period")
):
    """
    Detect feature distribution drift
    
    **New MLOps endpoint for data drift monitoring**
    """
    try:
        from src.mlops.drift_detector import DriftDetector
        
        drift_detector = DriftDetector()
        
        drift_results = drift_detector.detect_feature_drift(
            feature_set=feature_set,
            reference_days=reference_days,
            current_days=current_days,
            target_db="local"
        )
        
        return {
            "success": True,
            "drift_analysis": drift_results
        }
        
    except Exception as e:
        logger.error(f"Feature drift detection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/drift/model")
async def detect_model_drift(
    feature_set: str = Query(..., description="Feature set: 'vader' or 'finbert'"),
    model_type: str = Query("random_forest", description="Model type"),
    reference_days: int = Query(7, description="Days for reference period"),
    current_days: int = Query(1, description="Days for current period")
):
    """
    Detect model performance drift
    
    **New MLOps endpoint for model drift monitoring**
    """
    try:
        from src.mlops.drift_detector import DriftDetector
        
        drift_detector = DriftDetector()
        
        drift_results = drift_detector.detect_model_drift(
            feature_set=feature_set,
            model_type=model_type,
            reference_days=reference_days,
            current_days=current_days
        )
        
        return {
            "success": True,
            "drift_analysis": drift_results
        }
        
    except Exception as e:
        logger.error(f"Model drift detection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/drift/summary")
async def get_drift_summary(
    feature_set: str = Query(..., description="Feature set: 'vader' or 'finbert'"),
    model_type: str = Query("random_forest", description="Model type"),
    reference_days: int = Query(30, description="Reference period in days"),
    current_days: int = Query(7, description="Current period in days")
):
    """
    Get comprehensive drift summary with recommendations
    
    **New MLOps endpoint for complete drift analysis**
    """
    try:
        from src.mlops.drift_detector import DriftDetector
        
        drift_detector = DriftDetector()
        
        summary = drift_detector.get_drift_summary(
            feature_set=feature_set,
            model_type=model_type,
            reference_days=reference_days,
            current_days=current_days
        )
        
        # Convert numpy types before returning
        summary = convert_numpy_types(summary)
        
        return {
            "success": True,
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"Drift summary generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/retrain/check")
async def check_retraining_need(
    feature_set: str = Query(..., description="Feature set: 'vader' or 'finbert'"),
    model_type: str = Query("random_forest", description="Model type")
):
    """
    Check if model retraining is needed
    
    **MLOps endpoint for retraining decision**
    """
    try:
        from src.mlops.automated_retraining import AutomatedRetraining
        
        retrainer = AutomatedRetraining()
        decision = retrainer.should_retrain(
            feature_set=feature_set,
            model_type=model_type
        )
        
        return {
            "success": True,
            "decision": decision
        }
        
    except Exception as e:
        logger.error(f"Retraining check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/retrain/execute")
async def execute_retraining(
    feature_set: str = Query(..., description="Feature set: 'vader' or 'finbert'"),
    model_type: str = Query("random_forest", description="Model type"),
    deploy_if_better: bool = Query(True, description="Deploy if new model is better")
):
    """
    Execute model retraining
    
    **MLOps endpoint for manual retraining trigger**
    """
    try:
        from src.mlops.automated_retraining import AutomatedRetraining
        
        retrainer = AutomatedRetraining()
        
        # Check if retraining is advisable first
        decision = retrainer.should_retrain(feature_set, model_type)
        
        if not decision['data_check']['sufficient_data']:
            return {
                "success": False,
                "error": "Insufficient data for retraining",
                "data_check": decision['data_check']
            }
        
        # Execute retraining
        result = retrainer.retrain_model(
            feature_set=feature_set,
            model_type=model_type,
            deploy_if_better=deploy_if_better
        )
        
        return {
            "success": result['success'],
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Retraining execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/retrain/both")
async def execute_retraining_both(
    model_type: str = Query("random_forest", description="Model type"),
    deploy_if_better: bool = Query(True, description="Deploy if new models are better")
):
    """
    Execute retraining for both VADER and FinBERT models
    
    **MLOps endpoint for dual model retraining**
    """
    try:
        from src.mlops.automated_retraining import AutomatedRetraining
        
        retrainer = AutomatedRetraining()
        results = retrainer.retrain_both_feature_sets(
            model_type=model_type,
            deploy_if_better=deploy_if_better
        )
        
        return {
            "success": True,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Dual retraining failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/retrain/status")
async def get_retraining_status():
    """
    Get overall retraining system status
    
    **MLOps endpoint for system status**
    """
    try:
        from src.mlops.automated_retraining import AutomatedRetraining
        
        retrainer = AutomatedRetraining()
        
        # Check status for both feature sets
        vader_decision = retrainer.should_retrain('vader', 'random_forest')
        finbert_decision = retrainer.should_retrain('finbert', 'random_forest')
        
        return {
            "success": True,
            "status": {
                "vader": {
                    "should_retrain": vader_decision['should_retrain'],
                    "reasons": vader_decision['reasons'],
                    "data_available": vader_decision['data_check']['sample_count'],
                    "data_required": vader_decision['data_check']['min_required']
                },
                "finbert": {
                    "should_retrain": finbert_decision['should_retrain'],
                    "reasons": finbert_decision['reasons'],
                    "data_available": finbert_decision['data_check']['sample_count'],
                    "data_required": finbert_decision['data_check']['min_required']
                },
                "thresholds": {
                    "accuracy_degradation": retrainer.accuracy_degradation_threshold,
                    "drift_severity": retrainer.drift_severity_threshold,
                    "min_samples": retrainer.min_samples_required,
                    "min_predictions": retrainer.min_prediction_count
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))