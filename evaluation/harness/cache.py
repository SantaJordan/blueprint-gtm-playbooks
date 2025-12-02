"""
SQLite-backed caching for API responses.

Caches responses from evaluation APIs to minimize costs on repeat runs.
Each API has its own TTL based on data freshness requirements.
"""

import sqlite3
import json
import hashlib
import time
from pathlib import Path
from dataclasses import dataclass
from typing import Any
from contextlib import contextmanager


# Default TTLs in seconds
DEFAULT_TTLS = {
    "scrapin": 30 * 24 * 3600,      # 30 days
    "exa": 24 * 3600,               # 24 hours
    "serper": 7 * 24 * 3600,        # 7 days
    "blitz": 90 * 24 * 3600,        # 90 days
    "ocean": 30 * 24 * 3600,        # 30 days
    "leadmagic": 30 * 24 * 3600,    # 30 days
    "rapidapi_person": 90 * 24 * 3600,  # 90 days - profile data is stable
    "rapidapi_email": 30 * 24 * 3600,   # 30 days - email mappings can change
    "default": 7 * 24 * 3600,       # 7 days
}


@dataclass
class CacheEntry:
    """A cached API response"""
    key: str
    api: str
    response: dict
    timestamp: float
    ttl: int
    hit_count: int = 0

    @property
    def is_expired(self) -> bool:
        return time.time() > (self.timestamp + self.ttl)

    @property
    def age_hours(self) -> float:
        return (time.time() - self.timestamp) / 3600


class EvaluationCache:
    """
    SQLite-backed cache for API responses during evaluation.

    Usage:
        cache = EvaluationCache("./evaluation/data/cache.db")

        # Check cache first
        if cached := cache.get("scrapin", linkedin_url):
            return cached

        # Make API call
        result = await scrapin.get_company(linkedin_url)

        # Store in cache
        cache.set("scrapin", linkedin_url, result)
    """

    def __init__(self, db_path: str | Path, custom_ttls: dict | None = None):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.ttls = {**DEFAULT_TTLS, **(custom_ttls or {})}

        self._init_db()

    def _init_db(self):
        """Initialize database schema"""
        with self._connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    api TEXT NOT NULL,
                    response TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    ttl INTEGER NOT NULL,
                    hit_count INTEGER DEFAULT 0
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_cache_api
                ON cache(api)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_cache_timestamp
                ON cache(timestamp)
            """)

    @contextmanager
    def _connection(self):
        """Get a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _make_key(self, api: str, *args, **kwargs) -> str:
        """Generate a cache key from API name and parameters"""
        # Combine args and kwargs into a hashable string
        key_parts = [api] + [str(a) for a in args]
        if kwargs:
            key_parts.append(json.dumps(kwargs, sort_keys=True))

        key_str = ":".join(key_parts)
        return hashlib.sha256(key_str.encode()).hexdigest()[:32]

    def get(self, api: str, *args, **kwargs) -> dict | None:
        """
        Get a cached response.

        Args:
            api: API name (scrapin, blitz, ocean, etc.)
            *args, **kwargs: Parameters that uniquely identify the request

        Returns:
            Cached response dict or None if not found/expired
        """
        key = self._make_key(api, *args, **kwargs)

        with self._connection() as conn:
            row = conn.execute(
                "SELECT * FROM cache WHERE key = ?",
                (key,)
            ).fetchone()

            if row is None:
                return None

            entry = CacheEntry(
                key=row["key"],
                api=row["api"],
                response=json.loads(row["response"]),
                timestamp=row["timestamp"],
                ttl=row["ttl"],
                hit_count=row["hit_count"]
            )

            if entry.is_expired:
                # Clean up expired entry
                conn.execute("DELETE FROM cache WHERE key = ?", (key,))
                return None

            # Update hit count
            conn.execute(
                "UPDATE cache SET hit_count = hit_count + 1 WHERE key = ?",
                (key,)
            )

            return entry.response

    def set(self, api: str, *args, response: dict, ttl: int | None = None, **kwargs):
        """
        Store a response in cache.

        Args:
            api: API name
            *args: Parameters for key generation
            response: Response dict to cache
            ttl: Optional custom TTL in seconds
            **kwargs: Additional parameters for key generation
        """
        key = self._make_key(api, *args, **kwargs)
        ttl = ttl or self.ttls.get(api, self.ttls["default"])

        with self._connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO cache (key, api, response, timestamp, ttl, hit_count)
                VALUES (?, ?, ?, ?, ?, 0)
            """, (key, api, json.dumps(response), time.time(), ttl))

    def delete(self, api: str, *args, **kwargs):
        """Delete a specific cache entry"""
        key = self._make_key(api, *args, **kwargs)

        with self._connection() as conn:
            conn.execute("DELETE FROM cache WHERE key = ?", (key,))

    def clear_api(self, api: str):
        """Clear all cache entries for an API"""
        with self._connection() as conn:
            conn.execute("DELETE FROM cache WHERE api = ?", (api,))

    def clear_expired(self) -> int:
        """Remove all expired entries, return count deleted"""
        now = time.time()

        with self._connection() as conn:
            cursor = conn.execute("""
                DELETE FROM cache
                WHERE timestamp + ttl < ?
            """, (now,))
            return cursor.rowcount

    def clear_all(self):
        """Clear entire cache"""
        with self._connection() as conn:
            conn.execute("DELETE FROM cache")

    def stats(self) -> dict:
        """Get cache statistics"""
        with self._connection() as conn:
            total = conn.execute("SELECT COUNT(*) FROM cache").fetchone()[0]

            by_api = {}
            for row in conn.execute("""
                SELECT api, COUNT(*) as count, SUM(hit_count) as hits
                FROM cache GROUP BY api
            """):
                by_api[row["api"]] = {
                    "count": row["count"],
                    "total_hits": row["hits"] or 0
                }

            now = time.time()
            expired = conn.execute("""
                SELECT COUNT(*) FROM cache
                WHERE timestamp + ttl < ?
            """, (now,)).fetchone()[0]

            return {
                "total_entries": total,
                "expired_entries": expired,
                "by_api": by_api,
                "db_size_mb": self.db_path.stat().st_size / (1024 * 1024) if self.db_path.exists() else 0
            }

    def export_for_api(self, api: str) -> list[dict]:
        """Export all cache entries for an API (for debugging/analysis)"""
        with self._connection() as conn:
            rows = conn.execute("""
                SELECT key, response, timestamp, hit_count
                FROM cache WHERE api = ?
            """, (api,)).fetchall()

            return [
                {
                    "key": row["key"],
                    "response": json.loads(row["response"]),
                    "timestamp": row["timestamp"],
                    "hit_count": row["hit_count"]
                }
                for row in rows
            ]


class CachedAPIClient:
    """
    Wrapper to add caching to any async API client.

    Usage:
        cache = EvaluationCache("./cache.db")
        scrapin = ScrapinClient(api_key)
        cached_scrapin = CachedAPIClient(scrapin, cache, "scrapin")

        # This will check cache first, then call API if needed
        result = await cached_scrapin.call("get_company", linkedin_url)
    """

    def __init__(self, client: Any, cache: EvaluationCache, api_name: str):
        self.client = client
        self.cache = cache
        self.api_name = api_name

    async def call(self, method_name: str, *args, skip_cache: bool = False, **kwargs) -> dict:
        """
        Call a method on the wrapped client, with caching.

        Args:
            method_name: Name of method to call on client
            *args, **kwargs: Arguments to pass to method
            skip_cache: If True, bypass cache and always call API

        Returns:
            API response (from cache or fresh)
        """
        # Check cache first
        if not skip_cache:
            cached = self.cache.get(self.api_name, method_name, *args, **kwargs)
            if cached is not None:
                return cached

        # Call API
        method = getattr(self.client, method_name)
        if asyncio.iscoroutinefunction(method):
            result = await method(*args, **kwargs)
        else:
            result = method(*args, **kwargs)

        # Convert to dict if needed
        if hasattr(result, '__dict__'):
            result_dict = result.__dict__
        elif hasattr(result, 'to_dict'):
            result_dict = result.to_dict()
        else:
            result_dict = result

        # Cache result
        self.cache.set(self.api_name, method_name, *args, response=result_dict, **kwargs)

        return result_dict


# For the CachedAPIClient
import asyncio
