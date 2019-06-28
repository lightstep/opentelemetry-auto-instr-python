"""Instrument redis to report Redis queries.

``patch_all`` will automatically patch your Redis client to make it work.
::

    from ddtrace import Pin, patch
    import redis

    # If not patched yet, you can patch redis specifically
    patch(redis=True)

    # This will report a span with the default settings
    client = redis.StrictRedis(host="localhost", port=6379)
    client.get("my-key")

    # Use a pin to specify metadata related to this client
    Pin.override(client, service='redis-queue')
"""
from .patch import unpatch

__all__ = ['unpatch']
