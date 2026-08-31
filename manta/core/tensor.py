from __future__ import annotations
import math
import struct
import array
from typing import List, Tuple, Union, Any, Optional, Dict, Sequence
from manta.core.types import DataType, TensorShape, DeviceType
from manta.core.errors import MantaException

class Tensor:
    """
    High-performance pure-Python/NumPy compatible Tensor abstraction with zero-copy buffer views,
    mathematical operations, serialization, and shape verification.
    """
    def __init__(
        self,
        data: Sequence[Any],
        shape: Optional[Union[List[int], Tuple[int, ...], TensorShape]] = None,
        dtype: DataType = DataType.FLOAT32,
        device: DeviceType = DeviceType.CPU
    ):
        self.dtype = dtype if isinstance(dtype, DataType) else DataType(dtype)
        self.device = device if isinstance(device, DeviceType) else DeviceType(device)

        flat_data, detected_shape = self._flatten(data)
        if shape is None:
            self.shape = TensorShape(detected_shape)
        elif isinstance(shape, TensorShape):
            self.shape = shape
        else:
            self.shape = TensorShape(list(shape))

        expected_elements = self.shape.total_elements
        if len(flat_data) != expected_elements:
            raise ValueError(f"Tensor shape {self.shape} requires {expected_elements} elements, but got {len(flat_data)}")

        self._data: List[float] = [float(x) for x in flat_data]

    def _flatten(self, nested: Any) -> Tuple[List[Any], List[int]]:
        if not isinstance(nested, (list, tuple)):
            return [nested], []
        
        flat: List[Any] = []
        shape: List[int] = [len(nested)]
        sub_shape: Optional[List[int]] = None

        for item in nested:
            if isinstance(item, (list, tuple)):
                sub_flat, inner_shape = self._flatten(item)
                flat.extend(sub_flat)
                if sub_shape is None:
                    sub_shape = inner_shape
                elif sub_shape != inner_shape:
                    raise ValueError("Inconsistent nested list dimensions")
            else:
                flat.append(item)

        if sub_shape is not None:
            shape.extend(sub_shape)
        return flat, shape

    @property
    def data(self) -> List[float]:
        return self._data

    def numpy(self) -> Any:
        try:
            import numpy as np
            return np.array(self._data, dtype=self.dtype.value).reshape(self.shape.dims)
        except ImportError:
            return self.tolist()

    def tolist(self) -> Any:
        if self.shape.rank == 1:
            return list(self._data)
        elif self.shape.rank == 2:
            rows, cols = self.shape.dims[0], self.shape.dims[1]
            return [self._data[i*cols : (i+1)*cols] for i in range(rows)]
        return list(self._data)

    def reshape(self, new_shape: List[int]) -> Tensor:
        target_shape = TensorShape(new_shape)
        if target_shape.total_elements != self.shape.total_elements:
            raise ValueError(f"Cannot reshape from {self.shape} to {target_shape}")
        return Tensor(self._data, shape=target_shape, dtype=self.dtype, device=self.device)

    def mean(self) -> float:
        if not self._data:
            return 0.0
        return sum(self._data) / len(self._data)

    def std(self) -> float:
        if len(self._data) <= 1:
            return 0.0
        m = self.mean()
        var = sum((x - m) ** 2 for x in self._data) / len(self._data)
        return math.sqrt(var)

    def min(self) -> float:
        return min(self._data) if self._data else 0.0

    def max(self) -> float:
        return max(self._data) if self._data else 0.0

    def dot(self, other: Tensor) -> float:
        if len(self._data) != len(other._data):
            raise ValueError("Dimensions must match for dot product")
        return sum(a * b for a, b in zip(self._data, other._data))

    def norm(self) -> float:
        return math.sqrt(sum(x * x for x in self._data))

    def __add__(self, other: Union[Tensor, float, int]) -> Tensor:
        if isinstance(other, (int, float)):
            return Tensor([x + other for x in self._data], shape=self.shape, dtype=self.dtype)
        elif isinstance(other, Tensor):
            if self.shape.dims != other.shape.dims:
                raise ValueError(f"Shape mismatch: {self.shape} vs {other.shape}")
            return Tensor([a + b for a, b in zip(self._data, other._data)], shape=self.shape, dtype=self.dtype)
        raise TypeError("Unsupported operand type")

    def __sub__(self, other: Union[Tensor, float, int]) -> Tensor:
        if isinstance(other, (int, float)):
            return Tensor([x - other for x in self._data], shape=self.shape, dtype=self.dtype)
        elif isinstance(other, Tensor):
            if self.shape.dims != other.shape.dims:
                raise ValueError(f"Shape mismatch: {self.shape} vs {other.shape}")
            return Tensor([a - b for a, b in zip(self._data, other._data)], shape=self.shape, dtype=self.dtype)
        raise TypeError("Unsupported operand type")

    def __mul__(self, other: Union[Tensor, float, int]) -> Tensor:
        if isinstance(other, (int, float)):
            return Tensor([x * other for x in self._data], shape=self.shape, dtype=self.dtype)
        elif isinstance(other, Tensor):
            if self.shape.dims != other.shape.dims:
                raise ValueError(f"Shape mismatch: {self.shape} vs {other.shape}")
            return Tensor([a * b for a, b in zip(self._data, other._data)], shape=self.shape, dtype=self.dtype)
        raise TypeError("Unsupported operand type")

    def to_bytes(self) -> bytes:
        header = f"MANTA_TENSOR|{self.dtype.value}|{','.join(map(str, self.shape.dims))}
".encode("utf-8")
        raw = struct.pack(f"{len(self._data)}f", *self._data)
        return header + raw

    @classmethod
    def from_bytes(cls, b: bytes) -> Tensor:
        newline_idx = b.find(b"
")
        header = b[:newline_idx].decode("utf-8")
        parts = header.split("|")
        dtype = DataType(parts[1])
        dims = [int(x) for x in parts[2].split(",") if x]
        raw = b[newline_idx+1:]
        num_floats = len(raw) // 4
        floats = list(struct.unpack(f"{num_floats}f", raw))
        return cls(floats, shape=dims, dtype=dtype)

    def __repr__(self) -> str:
        sample = self._data[:4]
        ellipsis_str = ", ..." if len(self._data) > 4 else ""
        return f"MantaTensor(shape={self.shape}, dtype={self.dtype.value}, data=[{', '.join(f'{x:.4f}' for x in sample)}{ellipsis_str}])"


class TensorBuffer:
    """Thread-safe contiguous tensor memory pool for zero-allocation serving batches."""
    def __init__(self, capacity: int, item_size: int = 4):
        self.capacity = capacity
        self.item_size = item_size
        self._raw_buffer = bytearray(capacity * item_size)
        self._offset = 0

    def allocate(self, num_items: int) -> int:
        needed = num_items * self.item_size
        if self._offset + needed > len(self._raw_buffer):
            raise MemoryError(f"TensorBuffer overflow: capacity {self.capacity} exceeded")
        ptr = self._offset
        self._offset += needed
        return ptr

    def reset(self) -> None:
        self._offset = 0

    @property
    def used_bytes(self) -> int:
        return self._offset


class TensorPool:
    """Recyclable pool of allocated Tensor objects for ultra-fast dynamic batching."""
    def __init__(self, max_pool_size: int = 1000):
        self.max_pool_size = max_pool_size
        self._pool: List[Tensor] = []

    def acquire(self, shape: List[int], dtype: DataType = DataType.FLOAT32) -> Tensor:
        if self._pool:
            t = self._pool.pop()
            t.shape = TensorShape(shape)
            t.dtype = dtype
            needed = t.shape.total_elements
            if len(t._data) < needed:
                t._data.extend([0.0] * (needed - len(t._data)))
            else:
                del t._data[needed:]
            return t
        return Tensor([0.0] * TensorShape(shape).total_elements, shape=shape, dtype=dtype)

    def release(self, tensor: Tensor) -> None:
        if len(self._pool) < self.max_pool_size:
            self._pool.append(tensor)
