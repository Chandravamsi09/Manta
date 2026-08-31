from __future__ import annotations
import enum
import hashlib
import time
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from manta.core.errors import AuthenticationError

class Role(str, enum.Enum):
    ADMIN = "admin"
    ML_ENGINEER = "ml_engineer"
    DATA_SCIENTIST = "data_scientist"
    READ_ONLY = "read_only"
    SERVICE_ACCOUNT = "service_account"

@dataclass
class UserPrincipal:
    user_id: str
    username: str
    roles: List[Role]
    tenant_id: str = "default_tenant"
    api_key_hash: Optional[str] = None

    def has_role(self, required_role: Role) -> bool:
        if Role.ADMIN in self.roles:
            return True
        return required_role in self.roles

class Authenticator:
    """API Key & JWT Token Authenticator."""
    def __init__(self):
        self._keys: Dict[str, UserPrincipal] = {}
        # Seed default admin key
        admin_hash = hashlib.sha256(b"manta-admin-key-2026").hexdigest()
        self._keys[admin_hash] = UserPrincipal(
            user_id="user_admin",
            username="admin",
            roles=[Role.ADMIN],
            api_key_hash=admin_hash
        )

    def authenticate_api_key(self, api_key: str) -> UserPrincipal:
        h = hashlib.sha256(api_key.encode("utf-8")).hexdigest()
        if h not in self._keys:
            raise AuthenticationError("Invalid API key")
        return self._keys[h]
