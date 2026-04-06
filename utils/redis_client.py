"""
Redis Client - Connects to Redis server with graceful JSON fallback.

Used by the test framework to fetch cached test data (search terms,
product lists, session tokens) stored in Redis.  If the Redis server
is not reachable the client falls back to reading the same keys from
test_data/redis_data.json so that tests can still run in environments
where Redis is not installed.
"""
import json
import os
import logging

logger = logging.getLogger(__name__)

# Try to import redis; mark it unavailable if the package is missing
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("redis package not installed - using JSON fallback")


# Path to the local fallback file
_FALLBACK_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "test_data",
    "redis_data.json",
)


class RedisClient:
    """
    Thin wrapper around the Redis connection.

    Usage
    -----
    client = RedisClient()
    value  = client.get("test_search_term")
    all_d  = client.get_all()
    client.set("my_key", "my_value")
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        decode_responses: bool = True,
    ) -> None:
        """
        Attempt to connect to Redis.  On failure, fall back to JSON file.

        Args:
            host: Redis server hostname (default localhost)
            port: Redis server port (default 6379)
            db:   Redis database index (default 0)
            decode_responses: Return str values instead of bytes
        """
        self._client = None
        self._fallback_data: dict = {}

        if REDIS_AVAILABLE:
            try:
                self._client = redis.Redis(
                    host=host,
                    port=port,
                    db=db,
                    decode_responses=decode_responses,
                    socket_connect_timeout=3,  # fail fast if not reachable
                )
                # Ping to verify connectivity
                self._client.ping()
                logger.info("Connected to Redis at %s:%s", host, port)
                print(f"Redis connected at {host}:{port}")
            except Exception as exc:
                logger.warning("Redis unavailable (%s) - using JSON fallback", exc)
                print(f"Redis unavailable: {exc} - using JSON fallback")
                self._client = None

        if self._client is None:
            self._load_fallback()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, key: str, default=None):
        """
        Retrieve a single value by key.

        Args:
            key: The Redis key to look up
            default: Returned when key is missing

        Returns:
            Value associated with key, or *default*
        """
        if self._client is not None:
            value = self._client.get(key)
            return value if value is not None else default

        # Fallback
        return self._fallback_data.get(key, default)

    def set(self, key: str, value, ex: int = None) -> bool:
        """
        Store a value under *key*.

        Args:
            key:   The Redis key
            value: The value to store (will be JSON-serialised for complex types)
            ex:    Optional expiry in seconds

        Returns:
            True on success, False on error
        """
        if self._client is not None:
            try:
                serialised = json.dumps(value) if not isinstance(value, (str, int, float)) else value
                self._client.set(key, serialised, ex=ex)
                return True
            except Exception as exc:
                logger.error("Redis SET failed: %s", exc)
                return False

        # Fallback – persist to JSON file
        self._fallback_data[key] = value
        self._save_fallback()
        return True

    def get_all(self) -> dict:
        """
        Return all key-value pairs available to the framework.

        Returns:
            dict of all test-data keys
        """
        if self._client is not None:
            try:
                keys = self._client.keys("*")
                return {k: self._client.get(k) for k in keys}
            except Exception as exc:
                logger.error("Redis KEYS failed: %s", exc)
                return {}

        return dict(self._fallback_data)

    def get_list(self, key: str) -> list:
        """
        Retrieve a list stored under *key*.

        Returns:
            list value or empty list if key missing / not a list
        """
        if self._client is not None:
            try:
                raw = self._client.get(key)
                if raw:
                    parsed = json.loads(raw)
                    return parsed if isinstance(parsed, list) else [parsed]
            except Exception:
                pass
            return []

        value = self._fallback_data.get(key, [])
        return value if isinstance(value, list) else [value]

    def seed_test_data(self, data: dict, ex: int = 3600) -> None:
        """
        Bulk-load a dictionary of test data into Redis (or the fallback store).

        Args:
            data: dict of {key: value} pairs to insert
            ex:   TTL in seconds for each key (default 1 hour)
        """
        for key, value in data.items():
            self.set(key, value, ex=ex)
        print(f"Seeded {len(data)} keys into Redis{'(fallback)' if self._client is None else ''}")

    def flush_test_data(self) -> None:
        """Remove all keys (use with caution — test environments only)."""
        if self._client is not None:
            try:
                self._client.flushdb()
                print("Redis test DB flushed")
                return
            except Exception as exc:
                logger.error("Redis FLUSHDB failed: %s", exc)

        self._fallback_data.clear()
        self._save_fallback()
        print("Redis fallback store cleared")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_fallback(self) -> None:
        """Load data from the JSON fallback file."""
        try:
            if os.path.exists(_FALLBACK_PATH):
                with open(_FALLBACK_PATH, "r", encoding="utf-8") as fh:
                    self._fallback_data = json.load(fh)
                print(f"Loaded Redis fallback from {_FALLBACK_PATH}")
            else:
                # Provide sensible defaults so tests can still run
                self._fallback_data = {
                    "test_search_term": "laptop",
                    "popular_searches": ["laptop", "mobile", "headphones"],
                    "test_user_email": "testuser@example.com",
                }
                print("Fallback file not found - using built-in defaults")
        except Exception as exc:
            logger.error("Failed to load Redis fallback file: %s", exc)
            self._fallback_data = {"test_search_term": "laptop"}

    def _save_fallback(self) -> None:
        """Persist current fallback data back to the JSON file."""
        try:
            os.makedirs(os.path.dirname(_FALLBACK_PATH), exist_ok=True)
            with open(_FALLBACK_PATH, "w", encoding="utf-8") as fh:
                json.dump(self._fallback_data, fh, indent=2)
        except Exception as exc:
            logger.error("Failed to save Redis fallback file: %s", exc)


# Module-level singleton – import and use directly in step definitions
_default_client: RedisClient | None = None


def get_redis_client() -> RedisClient:
    """
    Return (and lazily create) the module-level RedisClient singleton.

    Example
    -------
    from utils.redis_client import get_redis_client
    rc = get_redis_client()
    term = rc.get("test_search_term", default="laptop")
    """
    global _default_client
    if _default_client is None:
        _default_client = RedisClient()
    return _default_client
