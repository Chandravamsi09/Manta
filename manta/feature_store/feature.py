from __future__ import annotations
import enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from manta.core.types import DataType

class FeatureType(str, enum.Enum):
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    EMBEDDING = "embedding"
    TIMESTAMP = "timestamp"
    BOOLEAN = "boolean"
    TEXT = "text"

@dataclass
class Feature:
    """Atomic feature attribute specification."""
    name: str
    data_type: DataType
    feature_type: FeatureType = FeatureType.NUMERICAL
    description: str = ""
    nullable: bool = True
    default_value: Optional[Any] = None
    tags: Dict[str, str] = field(default_factory=dict)

    def validate_value(self, value: Any) -> bool:
        if value is None:
            return self.nullable
        if self.data_type in (DataType.FLOAT32, DataType.FLOAT64):
            return isinstance(value, (int, float))
        if self.data_type in (DataType.INT32, DataType.INT64):
            return isinstance(value, int) and not isinstance(value, bool)
        if self.data_type == DataType.BOOL:
            return isinstance(value, bool)
        if self.data_type == DataType.STRING:
            return isinstance(value, str)
        if self.data_type == DataType.ARRAY:
            return isinstance(value, (list, tuple))
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "data_type": self.data_type.value,
            "feature_type": self.feature_type.value,
            "description": self.description,
            "nullable": self.nullable,
            "default_value": self.default_value,
            "tags": self.tags,
        }
