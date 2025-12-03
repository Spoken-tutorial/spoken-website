from django.core.cache import cache

REGISTRY_KEY = "_cache_key_registry"

def register_cache_key(key):
    keys = cache.get(REGISTRY_KEY)
    if not keys:
        keys = []  
    if key not in keys:
        keys.append(key)
        cache.set(REGISTRY_KEY, keys, None)

def unregister_cache_key(key):
    keys = cache.get(REGISTRY_KEY)
    if not keys:
        return
    if key in keys:
        keys.remove(key)
        cache.set(REGISTRY_KEY, keys, None)

def list_cache_keys():
    return sorted(cache.get(REGISTRY_KEY) or [])
