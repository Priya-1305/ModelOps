from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class PredictionInput(BaseModel):
    """
    Features for Wisconsin Breast Cancer classification.
    Can be provided as a dictionary of key-value pairs matching EXPECTED_FEATURE_NAMES.
    """
    features: Dict[str, float] = Field(
        ...,
        description="Dictionary mapping each of the 30 Wisconsin feature names (or snake_case) to float values.",
        json_schema_extra={
            "example": {
                "mean_radius": 17.99,
                "mean_texture": 10.38,
                "mean_perimeter": 122.8,
                "mean_area": 1001.0,
                "mean_smoothness": 0.1184,
                "mean_compactness": 0.2776,
                "mean_concavity": 0.3001,
                "mean_concave_points": 0.1471,
                "mean_symmetry": 0.2419,
                "mean_fractal_dimension": 0.07871,
                "radius_error": 1.095,
                "texture_error": 0.9053,
                "perimeter_error": 8.589,
                "area_error": 153.4,
                "smoothness_error": 0.006399,
                "compactness_error": 0.04904,
                "concavity_error": 0.05373,
                "concave_points_error": 0.01587,
                "symmetry_error": 0.03003,
                "fractal_dimension_error": 0.006193,
                "worst_radius": 25.38,
                "worst_texture": 17.33,
                "worst_perimeter": 184.6,
                "worst_area": 2019.0,
                "worst_smoothness": 0.1622,
                "worst_compactness": 0.6656,
                "worst_concavity": 0.7119,
                "worst_concave_points": 0.2654,
                "worst_symmetry": 0.4601,
                "worst_fractal_dimension": 0.1189,
            }
        }
    )
    model_name: Optional[str] = Field(default=None, description="Optional target model name")
    model_version: Optional[str] = Field(default=None, description="Optional target model version")


class BatchPredictionInput(BaseModel):
    items: List[Dict[str, float]] = Field(..., min_length=1, max_length=1000, description="List of feature dictionaries")
    model_name: Optional[str] = Field(default=None)
    model_version: Optional[str] = Field(default=None)


class PredictionResponse(BaseModel):
    prediction: int = Field(..., description="Binary classification (0 or 1)")
    prediction_label: str = Field(..., description="Target class label ('malignant' or 'benign')")
    probabilities: Dict[str, float] = Field(..., description="Predicted class probabilities")
    model_name: str
    model_version: str
    latency_ms: float
    correlation_id: str
    timestamp: datetime


class BatchPredictionResponse(BaseModel):
    predictions: List[PredictionResponse]
    total: int
    model_name: str
    model_version: str
    batch_latency_ms: float
    correlation_id: str


class PredictionLogItem(BaseModel):
    id: str
    correlation_id: str
    model_name: str
    model_version: str
    prediction: int
    prediction_label: str
    probabilities: Dict[str, float]
    latency_ms: float
    features: Optional[Dict[str, Any]] = None
    timestamp: datetime
