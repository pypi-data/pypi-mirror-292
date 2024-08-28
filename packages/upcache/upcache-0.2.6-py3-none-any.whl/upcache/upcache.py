from .helpers import create_cache_server, get_cache_client, create_cache_client, _validate_name
from .internal.tcp import Subscription

from datetime import timedelta
from typing import Optional, Callable, List, Tuple
import os
import tempfile

class UpCache:
    """
    Wrapper for an UpCache client.
    """
    def __init__(self, name: str, path: Optional[str] = None, auto_kill: bool = True, shared: bool = True) -> None:
        """
        Creates a new UpCache client and conditionally creates a new server.
        A server is created only when the name of a requested cache (`name`)
        is not present in the desired run-file path (`path`).

        :param name cache name
        :param path cache JSON run-file output path
        :param auto_kill kill the cache server when all clients disconnect
        :param shared use a shared client when True, otherwise create a new Client
                      (using shared clients reduces overhead opening connections
                       to the cache server)
        """
        self._client : Optional[Client] = None

        _validate_name(name)
        filename = os.path.join(path or tempfile.gettempdir(), f'upcache-{name}.json')
        try:
            create_cache_server(filename, auto_kill)
        except:
            # Ignore any creation failures.
            # This can happen for one of two reasons:
            # (1) We can't allocate the necessary resources to spin the server up (OS-level)
            # (2) The server is already running
            #
            # Either way, we will sort it out when we instantiate the cache client below.
            pass

        if shared:
            self._client = get_cache_client(filename, wait_for_file=True)
        else:
            self._client = create_cache_client(filename, wait_for_file=True)
    
    def get(self, key: bytes) -> Optional[bytes]:
        """
        Retrieves a value from the cache.

        :param key the associated key
        :returns associated value (if the key exists) or None (if it doesn't exist)
        """
        return self._client.get(key)

    def set(self, key: bytes, value: bytes) -> None:
        """
        Sets a key-value pair in the cache.

        :param key the key
        :param value the associated value
        """
        self._client.set(key, value)
    
    def exists(self, key: bytes) -> bool:
        """
        Checks if a key exists in the cache.

        :param key the associated key to check
        :returns True if the key exists, False otherwise
        """
        return self._client.exists(key)
    
    def wait_for(self, key: bytes, value: Optional[bytes] = None, timeout: Optional[timedelta] = None) -> bool:
        """
        Waits for an event with a key.

        :param key the key
        :param value optional value for event condition
        :param timeout optional timeout
        :returns True if an event for the key fired,
                 False if the cache is closed
        """
        return self._client.wait_for(key, value, timeout)

    def decrement(self, key: bytes) -> bytes:
        """
        Decrements a key in the cache.

        :param the key to decrement
        :returns the decremented value
        """
        return self._client.decrement(key)

    def increment(self, key: bytes) -> bytes:
        """
        Increments a key in the cache.

        :param the key to increment
        :returns the incremented value
        """
        return self._client.increment(key)
    
    def clear(self) -> None:
        """
        Clears all keys from the cache.
        """
        self._client.clear()
    
    def drop(self, key: bytes) -> bool:
        """
        Drops a key from the cache.

        :param key the key to drop
        :returns True if the key exists but was now dropped, False otherwise
        """
        return self._client.drop(key)

    def subscribe(self, key: bytes, callback: Callable[[bytes, Optional[bytes]], None]) -> Subscription:
        """
        Opens a subscription to changes on a key.

        :param key the subscription key
        :param callback associated callback for receiving key-value updates
        :returns subscription for maintaining connection details
        """
        return self._client.subscribe(key, callback)
    
    def subscribe_all(self, callback: Callable[[bytes, Optional[bytes]], None]) -> Subscription:
        """
        Opens a subscription to any key changes.

        :param callback associated callback for receiving key-value updates
        :returns subscription for maintaining connection details
        """
        return self._client.subscribe_all(callback)
    
    def count(self) -> int:
        """
        Returns the total number of key-value pairs in the cache.

        :returns number of key-value pairs
        """
        return self._client.count()
    
    def keys(self) -> List[bytes]:
        """
        Retrieves all keys in the cache.

        :returns list of keys
        """
        return self._client.keys()
    
    def items(self) -> List[Tuple[bytes, bytes]]:
        """
        Retrieves all key-value pairs in the cache.

        :returns list of key-value pairs
        """
        return self._client.items()
    
    def __del__(self) -> None:
        """
        Handles closure if not directly invoked.
        """
        self.close()

    def close(self, force: bool = False) -> None:
        """
        Closes the connection to the TCP server.

        :param force forces the connection closed
        """
        if self._client: self._client.close(force)

