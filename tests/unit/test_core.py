import pytest
from manta.core.tensor import Tensor, TensorBuffer, TensorPool
from manta.core.types import DataType, TensorShape, DeviceType
from manta.core.storage import LocalStorageBackend, InMemoryStorageBackend
from manta.core.config import MantaConfig

def test_tensor_creation_and_math():
    t1 = Tensor([1.0, 2.0, 3.0, 4.0], shape=[4], dtype=DataType.FLOAT32)
    t2 = Tensor([0.5, 0.5, 0.5, 0.5], shape=[4], dtype=DataType.FLOAT32)
    
    assert t1.shape.dims == [4]
    assert t1.mean() == 2.5
    assert t1.min() == 1.0
    assert t1.max() == 4.0
    
    t_add = t1 + t2
    assert t_add.data == [1.5, 2.5, 3.5, 4.5]
    
    t_sub = t1 - t2
    assert t_sub.data == [0.5, 1.5, 2.5, 3.5]
    
    t_mul = t1 * 2.0
    assert t_mul.data == [2.0, 4.0, 6.0, 8.0]
    
    dot_val = t1.dot(t2)
    assert dot_val == (0.5 + 1.0 + 1.5 + 2.0)

def test_tensor_serialization():
    t = Tensor([[1.0, 2.0], [3.0, 4.0]], dtype=DataType.FLOAT32)
    raw_bytes = t.to_bytes()
    restored = Tensor.from_bytes(raw_bytes)
    assert restored.shape.dims == [2, 2]
    assert restored.data == [1.0, 2.0, 3.0, 4.0]

def test_tensor_pool_and_buffer():
    pool = TensorPool(max_pool_size=10)
    t = pool.acquire([2, 3])
    assert t.shape.dims == [2, 3]
    pool.release(t)
    
    buf = TensorBuffer(capacity=100)
    ptr1 = buf.allocate(10)
    assert ptr1 == 0
    assert buf.used_bytes == 40
    buf.reset()
    assert buf.used_bytes == 0

def test_storage_backends(tmp_path):
    # Test In-Memory
    mem_store = InMemoryStorageBackend()
    mem_store.put("models/v1.bin", b"mock_weights")
    assert mem_store.exists("models/v1.bin")
    assert mem_store.get("models/v1.bin") == b"mock_weights"
    assert "models/v1.bin" in mem_store.list_keys("models")
    mem_store.delete("models/v1.bin")
    assert not mem_store.exists("models/v1.bin")

    # Test Local Storage
    local_store = LocalStorageBackend(root_dir=tmp_path / "manta_storage")
    local_store.put("chk/epoch_1.bin", b"state_dict_payload")
    assert local_store.exists("chk/epoch_1.bin")
    assert local_store.get("chk/epoch_1.bin") == b"state_dict_payload"
