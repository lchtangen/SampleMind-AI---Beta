#!/usr/bin/env python
"""Quick test of L1 cache implementation"""

from samplemind.core.cache.lru_cache import L1LRUCache, get_l1_cache

print("Testing L1 LRU Cache...")

# Test 1: Basic operations
cache = L1LRUCache(max_entries=100)
cache.set("test:key", {"value": 123})
result = cache.get("test:key")
assert result == {"value": 123}
print("✅ Test 1: Basic set/get")

# Test 2: Statistics
stats = cache.get_stats()
assert stats["entries"] == 1
assert stats["hits"] == 1
print("✅ Test 2: Statistics")

# Test 3: Singleton
cache2 = get_l1_cache()
assert cache2 is get_l1_cache()
print("✅ Test 3: Singleton pattern")

# Test 4: LRU eviction
cache.clear()
small_cache = L1LRUCache(max_entries=3)
small_cache.set("k1", "v1")
small_cache.set("k2", "v2")
small_cache.set("k3", "v3")
small_cache.set("k4", "v4")  # Should evict k1
assert small_cache.get("k1") is None
assert small_cache.get("k4") == "v4"
print("✅ Test 4: LRU eviction")

# Test 5: Delete
cache.clear()
cache.set("del:key", "value")
assert cache.delete("del:key") is True
assert cache.get("del:key") is None
print("✅ Test 5: Delete")

print("\n✅ All L1 LRU Cache tests passed!")
