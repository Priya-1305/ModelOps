from typing import Any, Dict, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse


class ModelOpsException(Exception):
    """Base exception for ModelOps platform."""

    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class ModelNotFoundException(ModelOpsException):
    def __init__(self, message: str = "Requested model or version was not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=status.HTTP_404_NOT_FOUND, details=details)


class ModelNotLoadedException(ModelOpsException):
    def __init__(self, message: str = "Model is not loaded or ready to serve inference", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=status.HTTP_503_SERVICE_UNAVAILABLE, details=details)


class InvalidInputException(ModelOpsException):
    def __init__(self, message: str = "Input data failed validation checks", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, details=details)


class TrainingFailedException(ModelOpsException):
    def __init__(self, message: str = "Training pipeline failed to complete", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, details=details)


class PromotionRejectedException(ModelOpsException):
    def __init__(self, message: str = "Candidate model did not meet promotion criteria", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=status.HTTP_400_BAD_REQUEST, details=details)


async def modelops_exception_handler(request: Request, exc: ModelOpsException) -> JSONResponse:
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": exc.__class__.__name__,
                "message": exc.message,
                "details": exc.details,
                "correlation_id": correlation_id,
            }
        },
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    # Never leak internal stack traces to clients in production
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "type": "InternalServerError",
                "message": "An unexpected internal server error occurred.",
                "correlation_id": correlation_id,
            }
        },
    )
