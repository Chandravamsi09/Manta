from __future__ import annotations
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import datetime
from manta.core.types import DataType

@dataclass
class Entity:
    """Primary key or identity boundary defining a logical feature group (e.g., user_id, device_id)."""
    name: str
    join_key: str
    data_type: DataType = DataType.STRING
    description: str = ""
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "join_key": self.join_key,
            "data_type": self.data_type.value,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Entity:
        return cls(
            name=data["name"],
            join_key=data["join_key"],
            data_type=DataType(data.get("data_type", "string")),
            description=data.get("description", ""),
            metadata=data.get("metadata", {}),
        )
