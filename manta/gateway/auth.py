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
    def __init__(self, config: Optional[Any] = None):
        from manta.core.config import get_config
        self._cfg = config or get_config().auth
        self._keys: Dict[str, UserPrincipal] = {}
        # Seed configured admin key
        api_key_bytes = self._cfg.api_key.encode("utf-8")
        admin_hash = hashlib.sha256(api_key_bytes).hexdigest()
        self._keys[admin_hash] = UserPrincipal(
            user_id="user_admin",
            username=self._cfg.admin_username,
            roles=[Role.ADMIN],
            api_key_hash=admin_hash
        )

    def authenticate_api_key(self, api_key: str) -> UserPrincipal:
        h = hashlib.sha256(api_key.encode("utf-8")).hexdigest()
        if h not in self._keys:
            raise AuthenticationError("Invalid API key")
        return self._keys[h]

    def validate_credentials(self, username: str, password_or_key: str) -> Optional[UserPrincipal]:
        if username.strip() == self._cfg.admin_username:
            if password_or_key in (self._cfg.admin_password, self._cfg.api_key):
                return UserPrincipal(
                    user_id="user_admin",
                    username=self._cfg.admin_username,
                    roles=[Role.ADMIN]
                )
        return None
