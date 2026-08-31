"""
Manta Gateway: REST API, gRPC interfaces, RBAC authentication, rate limiting, and OpenTelemetry instrumentation.
"""

from manta.gateway.api import create_app
from manta.gateway.auth import Authenticator, Role, UserPrincipal
from manta.gateway.rate_limiter import TokenBucketRateLimiter
from manta.gateway.telemetry import MetricsExporter, TracerProvider

__all__ = [
    "create_app",
    "Authenticator",
    "Role",
    "UserPrincipal",
    "TokenBucketRateLimiter",
    "MetricsExporter",
    "TracerProvider",
]
