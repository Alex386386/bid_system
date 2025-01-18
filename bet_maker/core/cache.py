from cachetools import TTLCache

from core.config import settings

cache = TTLCache(maxsize=settings.cache_max_size, ttl=settings.cache_ttl)
