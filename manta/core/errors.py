from typing import Optional, Dict, Any

class MantaException(Exception):
    """Base exception class for all Manta errors."""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": self.code,
            "message": self.message,
            "details": self.details,
        }

class ConfigError(MantaException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="CONFIG_ERROR", details=details)

class StorageError(MantaException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="STORAGE_ERROR", details=details)

class FeatureStoreError(MantaException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="FEATURE_STORE_ERROR", details=details)

class TrainingError(MantaException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="TRAINING_ERROR", details=details)

class ServingError(MantaException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="SERVING_ERROR", details=details)

class DriftError(MantaException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="DRIFT_ERROR", details=details)

class RegistryError(MantaException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="REGISTRY_ERROR", details=details)

class PipelineError(MantaException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="PIPELINE_ERROR", details=details)

class AuthenticationError(MantaException):
    def __init__(self, message: str = "Unauthorized access", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="AUTH_ERROR", details=details)

class RateLimitError(MantaException):
    def __init__(self, message: str = "Rate limit exceeded", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="RATE_LIMIT_ERROR", details=details)
