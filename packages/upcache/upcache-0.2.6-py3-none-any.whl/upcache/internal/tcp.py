from .cache import Cache
from .errors import ProtocolError
from socketserver import BaseRequestHandler, ThreadingTCPServer
from datetime import timedelta
from typing import Tuple, List, Optional, Callable, Set, Dict
from threading import Lock, Thread, Event
import atexit
import os
import sys
import json
import signal
import socket
import struct

# TCP protocol constants
MAGIC_WORD = 0x99DF8060
CMD_SHUTDOWN = 1
CMD_GET_KEY = 2
CMD_SET_KEY = 3
CMD_KEY_EXISTS = 4
CMD_DECR_KEY = 5
CMD_INCR_KEY = 6
CMD_CLEAR_KEYS = 7
CMD_DROP_KEY = 8
CMD_COUNT_KEYS = 9
CMD_ALL_KEYS = 10
CMD_ALL_ITEMS = 11
CMD_DISCONNECT = 12
CMD_WAIT_KEY = 13
CMD_SUB = 14
CMD_UNSUB = 15
CMD_NOTIFY_UPDATE = 16
CMD_NOTIFY_DELETE = 17
CMD_SUB_GLOBAL = 18
CMD_UNSUB_GLOBAL = 19
CMD_INTERRUPT = 20

# TCP protocol formatting structs
_envelope = struct.Struct('II')
_key_header = struct.Struct('I')
_key_response = struct.Struct('bI') # exists, length
_key_value_header = struct.Struct('II')
_value_response = struct.Struct('I')
_wait_header = struct.Struct('IbIbI') # key length, value(exists, length), timeout(exists, length)

class SocketReader:
    """
    Buffers data read from a socket.
    """
    def __init__(self, s: socket.socket, buf_size: int) -> None:
        """
        Constructs a new socket reader on top of a socket and defined
        buffer size.

        :param s socket to read
        :param buf_size number of bytes to read and buffer
        """
        self._socket = s
        self._buf_size = buf_size
        self._buf = b''

    def read(self, size: int) -> bytes:
        """
        Reads a number of bytes from the internal buffer and/or from the socket.

        :param size the number of bytes to read
        :returns payload read from buffer/socket
        """
        res = bytearray()
        while len(res) != size:
            if len(self._buf) == 0:
                self._buf = self._socket.recv(self._buf_size)
            bytes_to_copy = size-len(res)
            res += self._buf[:bytes_to_copy]
            self._buf = self._buf[bytes_to_copy:]
        return bytes(res)

class TCPHandler(BaseRequestHandler):
    """
    Handles TCP requests to the cache server.
    """
    def setup(self) -> None:
        """
        Sets up a connection map and reference to the TCP server cache.
        """
        self.server.on_connect() # type: ignore[attr-defined]
        self._cache = self.server.cache # type: ignore[attr-defined]
        self._cmds = {
            CMD_SHUTDOWN: self._shutdown,
            CMD_GET_KEY: self._get_key,
            CMD_SET_KEY: self._set_key,
            CMD_KEY_EXISTS: self._key_exists,
            CMD_DECR_KEY: self._decr_key,
            CMD_INCR_KEY: self._incr_key,
            CMD_CLEAR_KEYS: self._clear_keys,
            CMD_DROP_KEY: self._drop_key,
            CMD_COUNT_KEYS: self._count_keys,
            CMD_ALL_KEYS: self._all_keys,
            CMD_ALL_ITEMS: self._all_items,
            CMD_WAIT_KEY: self._wait_key,
            CMD_SUB: self._subscribe,
            CMD_UNSUB: self._unsubscribe,
            CMD_SUB_GLOBAL: self._subscribe_global,
            CMD_UNSUB_GLOBAL: self._unsubscribe_global,
            CMD_INTERRUPT: self._interrupt,
        }
        self._cache_update = Subscriber(self.request)
        self._lock = Lock()

    def finish(self) -> None:
        """
        Signals the server that a client disconnected.
        """
        self.server.on_disconnect() # type: ignore[attr-defined]

    def _shutdown(self, data: SocketReader) -> bytes:
        """
        Shuts down the TCP server from a client request.

        :param data request reader
        :returns response
        """
        self.server.shutdown()
        return _envelope.pack(MAGIC_WORD, CMD_SHUTDOWN)

    def _get_key(self, data: SocketReader) -> bytes:
        """
        Retrieves a key and responds with a value or None.

        :param data request reader
        :returns response
        """
        key_len, = _key_header.unpack(data.read(_key_header.size))
        key = data.read(key_len)
        if len(key) != key_len: raise ProtocolError("length")
        value = self._cache.get(key)

        res = _envelope.pack(MAGIC_WORD, CMD_GET_KEY)
        if value is None:
            res += _key_response.pack(False, 0)
        else:
            res += _key_response.pack(True, len(value)) + value
        return res

    def _set_key(self, data: SocketReader) -> bytes:
        """
        Sets a value for an associated key.

        :param data request reader
        :returns response
        """
        key_len, value_len = _key_value_header.unpack(data.read(_key_value_header.size))
        key_value = data.read(key_len + value_len)
        if len(key_value) != key_len + value_len: raise ProtocolError("length")

        self._cache.set(key_value[:key_len], key_value[key_len:])

        return _envelope.pack(MAGIC_WORD, CMD_SET_KEY)
    
    def _wait_key(self, data: SocketReader) -> bytes:
        """
        Waits for an event with an associated key (create/drop/update/increment/decrement).

        :param data request reader
        :returns response
        """
        key_len, has_value, value_len, has_timeout, timeout_usec = _wait_header.unpack(data.read(_wait_header.size))
        key = data.read(key_len)
        if len(key) != key_len: raise ProtocolError("length")
        value = data.read(value_len) if has_value == 1 else None
        if value and len(value) != value_len: raise ProtocolError("length")
        timeout = timedelta(microseconds=timeout_usec) if has_timeout == 1 else None

        key_changed = self._cache.wait_for(key, value, timeout)

        return _envelope.pack(MAGIC_WORD, CMD_WAIT_KEY) + struct.pack('b', key_changed)
    
    def _subscribe(self, data: SocketReader) -> bytes:
        """
        Subscribes to change events for a key in the cache.

        :param data request reader
        :returns response
        """
        key_len, = _key_header.unpack(data.read(_key_header.size))
        key = data.read(key_len)
        if len(key) != key_len: raise ProtocolError("length")
        self.server.subscribe(key, self._cache_update) # type: ignore[attr-defined]
        return _envelope.pack(MAGIC_WORD, CMD_SUB)
    
    def _unsubscribe(self, data: SocketReader) -> bytes:
        """
        Unsubscribes from change events for a key in the cache.

        :param data request reader
        :returns response
        """
        key_len, = _key_header.unpack(data.read(_key_header.size))
        key = data.read(key_len)
        if len(key) != key_len: raise ProtocolError("length")
        self.server.unsubscribe(key, self._cache_update) # type: ignore[attr-defined]
        return _envelope.pack(MAGIC_WORD, CMD_UNSUB)
    
    def _subscribe_global(self, data: SocketReader) -> bytes:
        """
        Subscribes to change events for all keys.

        :param data request reader
        :returns response
        """
        self.server.subscribe_all(self._cache_update) # type: ignore[attr-defined]
        return _envelope.pack(MAGIC_WORD, CMD_SUB_GLOBAL)
    
    def _unsubscribe_global(self, data: SocketReader) -> bytes:
        """
        Unsubscribes from global change events in the cache.

        :param data request reader
        :returns response
        """
        self.server.unsubscribe_all(self._cache_update) # type: ignore[attr-defined]
        return _envelope.pack(MAGIC_WORD, CMD_UNSUB_GLOBAL)
    
    def _interrupt(self, data: SocketReader) -> bytes:
        """
        Generates a "pong" to a "ping" for interrupting a listener thread.

        :param data request reader
        :returns response
        """
        return _envelope.pack(MAGIC_WORD, CMD_INTERRUPT)

    def _key_exists(self, data: SocketReader) -> bytes:
        """
        Determines if a key is located in the cache.

        :param data request reader
        :returns response
        """
        key_len, = _key_header.unpack(data.read(_key_header.size))
        key = data.read(key_len)
        if len(key) != key_len: raise ProtocolError("length")
        exists = self._cache.exists(key)

        return _envelope.pack(MAGIC_WORD, CMD_KEY_EXISTS) + struct.pack('b', exists)

    def _decr_key(self, data: SocketReader) -> bytes:
        """
        Decrements a key's value.

        :param data request reader
        :returns response
        """
        key_len, = _key_header.unpack(data.read(_key_header.size))
        key = data.read(key_len)
        if len(key) != key_len: raise ProtocolError("length")
        value = self._cache.decrement(key)

        return _envelope.pack(MAGIC_WORD, CMD_DECR_KEY) + _value_response.pack(len(value)) + value

    def _incr_key(self, data: SocketReader) -> bytes:
        """
        Increments a key's value.

        :param data request reader
        :returns response
        """
        key_len, = _key_header.unpack(data.read(_key_header.size))
        key = data.read(key_len)
        if len(key) != key_len: raise ProtocolError("length")
        value = self._cache.increment(key)

        return _envelope.pack(MAGIC_WORD, CMD_INCR_KEY) + _value_response.pack(len(value)) + value
    
    def _clear_keys(self, data: SocketReader) -> bytes:
        """
        Clears all keys in the cache.

        :param data request reader
        :returns response
        """
        self._cache.clear()
        return _envelope.pack(MAGIC_WORD, CMD_CLEAR_KEYS)

    def _drop_key(self, data: SocketReader) -> bytes:
        """
        Drops a key from the cache.

        :param data request reader
        :returns response
        """
        key_len, = _key_header.unpack(data.read(_key_header.size))
        key = data.read(key_len)
        if len(key) != key_len: raise ProtocolError("length")
        dropped = self._cache.drop(key)

        return _envelope.pack(MAGIC_WORD, CMD_DROP_KEY) + struct.pack('b', dropped)

    def _count_keys(self, data: SocketReader) -> bytes:
        """
        Counts all keys in the cache.

        :param data request reader
        :returns response
        """
        count = self._cache.count()
        return _envelope.pack(MAGIC_WORD, CMD_COUNT_KEYS) + struct.pack('I', count)

    def _all_keys(self, data: SocketReader) -> bytes:
        """
        Returns all keys in the cache.

        :param data request reader
        :returns response
        """
        num_keys = 0
        key_data = bytearray()
        for k in self._cache.keys():
            key_data += _key_header.pack(len(k)) + k
            num_keys += 1
        return _envelope.pack(MAGIC_WORD, CMD_ALL_KEYS) + struct.pack('I', num_keys) + bytes(key_data)

    def _all_items(self, data: SocketReader) -> bytes:
        """
        Returns all key-value pairs in the cache.

        :param data request reader
        :returns response
        """
        num_items = 0
        kv_data = bytearray()
        for k, v in self._cache.items():
            kv_data += _key_value_header.pack(len(k), len(v)) + k + v
            num_items += 1
        return _envelope.pack(MAGIC_WORD, CMD_ALL_ITEMS) + struct.pack('I', num_items) + bytes(kv_data)

    def handle(self) -> None:
        """
        Processes a TCP client's requests.
        """
        data = SocketReader(self.request, 512)
        try:
            while True:
                magic_word, cmd_id = _envelope.unpack(data.read(_envelope.size))
                if magic_word != MAGIC_WORD: raise ProtocolError('magic word')
                elif cmd_id == CMD_DISCONNECT: break
                cmd = self._cmds.get(cmd_id)
                if cmd is None: raise ProtocolError('command')
                with self._lock:
                    self.request.sendall(cmd(data))
        except:
            pass

class ShutdownSignal(Exception):
    """
    Used as a signal to force the TCP server to shutdown internally.
    """
    pass

class Subscriber:
    """
    Wraps a socket to send updates to a SubscriptionClient.
    """
    def __init__(self, socket: socket.socket) -> None:
        """
        Constructs a new Subscriber on top of a socket.

        :param socket the socket which will be sent updates
        """
        self._socket = socket

    def on_data(self, key: bytes, data: Optional[bytes]) -> None:
        """
        Processes updates received from a key-value update
        in the cache.

        :param key key updated
        :param data value bytes to send to socket
        """
        if data:
            self._socket.sendall(_envelope.pack(MAGIC_WORD, CMD_NOTIFY_UPDATE) + _key_value_header.pack(len(key), len(data)) + key + data)
        else:
            self._socket.sendall(_envelope.pack(MAGIC_WORD, CMD_NOTIFY_DELETE) + _key_response.pack(len(key)) + key)

class SubscriptionList:
    """
    Maintains a list of subscriptions to a key.
    """
    def __init__(self) -> None:
        """
        Constructs a new empty subscription list.
        """
        self._subs : Set[Subscriber] = set()
        self._lock = Lock()
        self._remove : List[Subscriber] = []

    @property
    def empty(self) -> bool:
        """
        Checks if the subscription list is empty.

        :returns True if the subscription list is empty
        """
        return len(self._subs) == 0

    def add(self, sub: Subscriber) -> None:
        """
        Adds a subscriber to the list.

        :param sub subscriber
        """
        with self._lock:
            self._subs.add(sub)

    def remove(self, sub: Subscriber) -> None:
        """
        Removes a subscriber from the list.

        :param sub subscriber
        """
        with self._lock:
            self._subs.discard(sub)

    def send(self, key: bytes, data: Optional[bytes]) -> None:
        """
        Sends a payload to all subscribers.

        :param key key updated
        :param data payload to send
        """
        with self._lock:
            for s in self._subs:
                try:
                    s.on_data(key, data)
                except Exception as e:
                    self._remove.append(s)
        if self._remove:
            with self._lock:
                for item in self._remove:
                    self._subs.discard(item)
            self._remove.clear()

class TCPServer(ThreadingTCPServer):
    """
    Cache server (TCP server)
    """
    def __init__(self, bind: Tuple[str, int], auto_kill: bool) -> None:
        """
        Constructs a new TCP server.

        :param bind host/port combination for TCP listening
        :param auto_kill kills the server when all clients disconnect
        """
        super().__init__(bind, TCPHandler)
        self.cache = Cache(self._on_cache_update)
        self._auto_kill = auto_kill
        self._num_connected = 0
        self._conn_lock = Lock()
        self._subs : Dict[bytes, SubscriptionList] = {}
        self._global_subs = SubscriptionList()

    def _on_cache_update(self, key: bytes, value: Optional[bytes]) -> None:
        """
        Processes updates to the Cache object.

        :param key updated key
        :param value updated value (None to signify deletion)
        """
        subs = self._subs.get(key)
        if subs:
            subs.send(key, value)

    def subscribe(self, key: bytes, sub: Subscriber) -> None:
        """
        Subscribes to change events associated with a key.

        :param key associated key
        :param sub subscriber for receiving updates
        """
        subs = self._subs.get(key)
        if not subs:
            subs = SubscriptionList()
            self._subs[key] = subs
        subs.add(sub)
    
    def unsubscribe(self, key: bytes, sub: Subscriber) -> None:
        """
        Unsubscribes a subscriber from change events associated
        with a key.

        :param key associated key
        :param sub subscriber to unsubscribe
        """
        subs = self._subs.get(key)
        if subs:
            subs.remove(sub)
            if subs.empty: self._subs.pop(key)
    
    def subscribe_all(self, sub: Subscriber) -> None:
        """
        Subscribes to all change events.

        :param sub subscriber for receiving updates
        """
        self._global_subs.add(sub)
    
    def unsubscribe_all(self, sub: Subscriber) -> None:
        """
        Unsubscribes a subscriber from all change events.

        :param sub subscriber to unsubscribe
        """
        self._global_subs.remove(sub)

    def service_actions(self) -> None:
        """
        Processed every loop to determine if the server
        needs to die internally (see auto-kill functionality).
        """
        if self._auto_kill and self._num_connected == 0:
            self.cache.close()
            raise ShutdownSignal()

    def on_connect(self) -> None:
        """
        Increases the connection count.
        """
        with self._conn_lock:
            self._num_connected += 1

    def on_disconnect(self) -> None:
        """
        Decreases the connection count.
        """
        with self._conn_lock:
            self._num_connected -= 1

class SubscriptionClient:
    """
    UpCache subscription client
    """
    def __init__(self, host: str, port: int) -> None:
        """
        Constructs a new TCP-based UpCache client.

        :param host TCP host
        :param port TCP port
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 0))
        s.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
        s.connect((host, port))

        self._update_event = Event()
        self._update_event.clear()
        self._recent_key : Optional[bytes] = None

        self._lock = Lock()
        self._socket = s
        self._callbacks : Dict[bytes, Set[Callable[[bytes, Optional[bytes]], None]]] = {}
        self._global_callbacks : Set[Callable[[bytes, Optional[bytes]], None]] = set()
        self._rd = SocketReader(s, 512)
       
        self._process_thread = Thread(target=self._process_incoming)
        self._process_thread.start()
        self._closed = False

    def wait_for_update(self, key: Optional[bytes]) -> bool:
        """
        Waits for an update on a specific key to occur.  If no key
        is specified, it waits for any key to update.

        :returns True if an update occurred, False if the connection
                 was closed with no update
        """
        # TODO: this may get hairy for multiple waiters...
        while True:
            self._update_event.wait()
            self._update_event.clear()
            if self._closed:
                return False
            elif key is None or self._recent_key == key:
                return True
    
    def wait_for_close(self) -> None:
        """
        Waits for the client to close.
        """
        while not self._closed:
            self._update_event.wait()
            self._update_event.clear()

    def subscribe(self, key: Optional[bytes], callback: Callable[[bytes, Optional[bytes]], None]) -> None:
        """
        Enrolls a subscription callback for a specified key or all events if key is None.

        :param key optional subscription key filter
        :param callback callback for key-value updates
        """
        _sendall = self._socket.sendall
        if key is None:
            self._global_callbacks.add(callback)
            with self._lock:
                _sendall(_envelope.pack(MAGIC_WORD, CMD_SUB_GLOBAL))
        else:
            new_key = False
            cb_list = self._callbacks.get(key)
            if cb_list is None:
                cb_list = set()
                self._callbacks[key] = cb_list
                new_key = True
            cb_list.add(callback)
            if new_key:
                with self._lock:
                    _sendall(_envelope.pack(MAGIC_WORD, CMD_SUB) + _key_header.pack(len(key)) + key)

    def unsubscribe(self, key: Optional[bytes], callback: Callable[[bytes, Optional[bytes]], None]) -> None:
        """
        Removes a subscription callback from a specified key subscription list or from all events.

        :param key optional subscription key filter
        :param callback callback for key-value updates
        """
        if key is None:
            try:
                self._global_callbacks.remove(callback)
            except:
                pass
            if self._global_callbacks:
                return
            with self._lock:
                self._socket.sendall(_envelope.pack(MAGIC_WORD, CMD_UNSUB_GLOBAL))
        else:
            cb_list = self._callbacks.get(key)
            if cb_list is None:
                return
            try:
                cb_list.remove(callback)
            except:
                pass
            if cb_list:
                return
            self._callbacks.pop(key)
            with self._lock:
                self._socket.sendall(_envelope.pack(MAGIC_WORD, CMD_UNSUB) + _key_header.pack(len(key)) + key)

    def _dispatch(self, key: bytes, value: Optional[bytes]) -> None:
        """
        Handles dispatching key-value updates to the appropriate callbacks.

        :param key key updated
        :param value optional value updated (None indicates deletion)
        """

        # Notify that we have a key-value update
        self._recent_key = key
        self._update_event.set()

        for cb in self._global_callbacks:
            cb(key, value)
        cb_list = self._callbacks.get(key)
        if cb_list:
            for cb in cb_list:
                cb(key, value)

    def _process_incoming(self) -> None:
        """
        Processes incoming updates on a dedicated thread.
        """
        _envelope_size = _envelope.size
        _rd_read = self._rd.read
        _envelope_unpack = _envelope.unpack
        _key_value_header_unpack = _key_value_header.unpack
        _key_value_header_size = _key_value_header.size
        _key_response_unpack = _key_response.unpack
        _key_response_size = _key_response.size
        _lock = self._lock
        _dispatch = self._dispatch
        try:
            while True:
                # Process commands
                mw, cmd = _envelope_unpack(_rd_read(_envelope_size))
                with _lock:
                    if cmd == CMD_NOTIFY_UPDATE:
                        key_len, value_len = _key_value_header_unpack(_rd_read(_key_value_header_size))
                        key = _rd_read(key_len)
                        value = _rd_read(value_len)
                    elif cmd == CMD_NOTIFY_DELETE:
                        key_len, = _key_response_unpack(_rd_read(_key_response_size))
                        key = _rd_read(key_len)
                        value = None
                    elif cmd == CMD_SUB or cmd == CMD_UNSUB or cmd == CMD_SUB_GLOBAL or cmd == CMD_UNSUB_GLOBAL:
                        continue
                    else:
                        # CMD_INTERRUPT and friends funnel here...
                        break
                _dispatch(key, value)
        except:
            pass

    def __del__(self) -> None:
        """
        Handles closure if not directly invoked.
        """
        self.close()

    @property
    def is_subscribed(self) -> bool:
        """
        Returns whether the SubscriptionClient is actively subscribed to any
        events.

        :returns True if at least one subscription is open
        """
        # TODO: check _callbacks here?
        return len(self._global_callbacks) != 0 or len(self._callbacks) != 0
    
    def close(self) -> None:
        """
        Closes the connection to the TCP server.
        """
        if self._closed: return

        # Send unsub which will ACK, so wait for thread to complete
        for k in self._callbacks.keys():
            with self._lock:
                self._socket.sendall(_envelope.pack(MAGIC_WORD, CMD_UNSUB) + _key_header.pack(len(k)) + k)
                #mw, cmd = _envelope.unpack(self._rd.read(_envelope.size))
        self._callbacks.clear()
        if self._global_callbacks:
            with self._lock:
                self._socket.sendall(_envelope.pack(MAGIC_WORD, CMD_UNSUB_GLOBAL))
                #mw, cmd = _envelope.unpack(self._rd.read(_envelope.size))
            self._global_callbacks.clear()

        # Interrupt the processing thread by poisoning the TCP connection
        with self._lock:
            self._socket.sendall(_envelope.pack(MAGIC_WORD, CMD_INTERRUPT))
        self._process_thread.join()

        # Send disconnect and shut down
        with self._lock:
            self._socket.sendall(_envelope.pack(MAGIC_WORD, CMD_DISCONNECT))
            self._socket.shutdown(socket.SHUT_RDWR)
            self._socket.close()
        self._closed = True

        # Notify any waiters...
        self._update_event.set()

class Subscription:
    """
    Maintains a subscription and callback to the SubscriptionClient.
    """
    def __init__(self, client: SubscriptionClient, key: Optional[bytes], callback: Callable[[bytes, Optional[bytes]], None]) -> None:
        """
        Registers a callback for key-value updates to the SubscriptionClient.

        :param client subscription client
        :param key optional key filter
        :param callback callback for key-value updates
        """
        self._client = client
        self._key = key
        self._callback = callback
        self._client_close_event = Event()
        self._client_close_event.clear()

        self._client.subscribe(key, callback)

    def close(self) -> None:
        """
        Unsubscribes the callback subscription from the subscription client.
        """
        self._client.unsubscribe(self._key, self._callback)

        # Notify any waiters...
        self._client_close_event.set()

        # Don't waste resources...
        if not self._client.is_subscribed:
            self._client.close()

    def wait_for_update(self, key: Optional[bytes]) -> bool:
        """
        Waits for an update on a specific key to occur.  If no key
        is specified, it waits for any key to update.

        :returns True if an update occurred, False if the connection
                 was closed with no update
        """
        return self._client.wait_for_update(key)
    
    def wait_for_close(self) -> None:
        """
        Waits for the client to close.
        """
        self._client_close_event.wait()

class Client:
    """
    UpCache client
    """
    def __init__(self, host: str, port: int) -> None:
        """
        Constructs a new TCP-based UpCache client.

        :param host TCP host
        :param port TCP port
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 0))
        s.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
        s.connect((host, port))

        self._sub_client : Optional[SubscriptionClient] = None

        self._lock = Lock()
        self._socket = s
        self._rd = SocketReader(s, 512)
        self._closed = False
        self._refs = 0

    def _inc_ref(self) -> None:
        """
        Increases the reference count for avoiding the
        client from closing when in use elsewhere.
        """
        with self._lock:
            self._refs += 1

    def _shutdown_server(self) -> None:
        """
        Shuts down server remotely.
        """
        with self._lock:
            self._socket.sendall(_envelope.pack(MAGIC_WORD, CMD_SHUTDOWN))

    def get(self, key: bytes) -> Optional[bytes]:
        """
        Retrieves a value from the cache.

        :param key the associated key
        :returns associated value (if the key exists) or None (if it doesn't exist)
        """
        with self._lock:
            self._socket.sendall(_envelope.pack(MAGIC_WORD, CMD_GET_KEY) + _key_header.pack(len(key)) + key)
            mw, cmd = _envelope.unpack(self._rd.read(_envelope.size))

            exists, key_len = _key_response.unpack(self._rd.read(_key_response.size))
            key_data = self._rd.read(key_len)
        if exists == 1:
            return key_data
        else:
            return None

    def set(self, key: bytes, value: bytes) -> None:
        """
        Sets a key-value pair in the cache.

        :param key the key
        :param value the associated value
        """
        with self._lock:
            self._socket.sendall(_envelope.pack(MAGIC_WORD, CMD_SET_KEY) + _key_value_header.pack(len(key), len(value)) + key + value)
            mw, cmd = _envelope.unpack(self._rd.read(_envelope.size))
    
    def exists(self, key: bytes) -> bool:
        """
        Checks if a key exists in the cache.

        :param key the associated key to check
        :returns True if the key exists, False otherwise
        """
        req = _envelope.pack(MAGIC_WORD, CMD_KEY_EXISTS) + _key_header.pack(len(key)) + key
        with self._lock:
            self._socket.sendall(req)
            mw, cmd = _envelope.unpack(self._rd.read(_envelope.size))

            exists, = struct.unpack('b', self._rd.read(1))
        return exists == 1
    
    def wait_for(self, key: bytes, value: Optional[bytes] = None, timeout: Optional[timedelta] = None) -> bool:
        """
        Waits for an event with a key.

        :param key the key
        :param value optional value for event condition
        :param timeout optional timeout
        :returns True if an event for the key fired,
                 False if the cache is closed
        """

        req = _envelope.pack(MAGIC_WORD, CMD_WAIT_KEY) + _wait_header.pack(len(key), (value is not None), len(value) if value else 0, (timeout is not None), ((timeout.seconds * 1000000) + timeout.microseconds) if timeout else 0) + key + (value if value else b'')
        with self._lock:
            self._socket.sendall(req)
            mw, cmd = _envelope.unpack(self._rd.read(_envelope.size))

            key_changed, = struct.unpack('b', self._rd.read(1))
        return key_changed == 1

    def decrement(self, key: bytes) -> bytes:
        """
        Decrements a key in the cache.

        :param the key to decrement
        :returns the decremented value
        """
        with self._lock:
            self._socket.sendall(_envelope.pack(MAGIC_WORD, CMD_DECR_KEY) + _key_header.pack(len(key)) + key)
            mw, cmd = _envelope.unpack(self._rd.read(_envelope.size))

            value_len, = _value_response.unpack(self._rd.read(_value_response.size))
            value_data = self._rd.read(value_len)
        return value_data

    def increment(self, key: bytes) -> bytes:
        """
        Increments a key in the cache.

        :param the key to increment
        :returns the incremented value
        """
        with self._lock:
            self._socket.sendall(_envelope.pack(MAGIC_WORD, CMD_INCR_KEY) + _key_header.pack(len(key)) + key)
            mw, cmd = _envelope.unpack(self._rd.read(_envelope.size))

            value_len, = _value_response.unpack(self._rd.read(_value_response.size))
            value_data = self._rd.read(value_len)
        return value_data
    
    def clear(self) -> None:
        """
        Clears all keys from the cache.
        """
        with self._lock:
            self._socket.sendall(_envelope.pack(MAGIC_WORD, CMD_CLEAR_KEYS))
            mw, cmd = _envelope.unpack(self._rd.read(_envelope.size))
    
    def drop(self, key: bytes) -> bool:
        """
        Drops a key from the cache.

        :param key the key to drop
        :returns True if the key exists but was now dropped, False otherwise
        """
        with self._lock:
            self._socket.sendall(_envelope.pack(MAGIC_WORD, CMD_DROP_KEY) + _key_header.pack(len(key)) + key)
            mw, cmd = _envelope.unpack(self._rd.read(_envelope.size))

            dropped, = struct.unpack('b', self._rd.read(1))
        return dropped == 1

    def _get_subscription_client(self) -> SubscriptionClient:
        """
        Creates or returns the existing subscription client for handling
        client-server subscriptions for key-value updates.

        :returns per-instance SubscriptionClient
        """
        if not self._sub_client:
            host, port = self._socket.getpeername()
            self._sub_client = SubscriptionClient(host, port)
        return self._sub_client
    
    def subscribe(self, key: bytes, callback: Callable[[bytes, Optional[bytes]], None]) -> Subscription:
        """
        Opens a subscription to changes on a key.

        :param key the subscription key
        :param callback associated callback for receiving key-value updates
        :returns subscription for maintaining connection details
        """
        return Subscription(self._get_subscription_client(), key, callback)
    
    def subscribe_all(self, callback: Callable[[bytes, Optional[bytes]], None]) -> Subscription:
        """
        Opens a subscription to any key changes.

        :param callback associated callback for receiving key-value updates
        :returns subscription for maintaining connection details
        """
        return Subscription(self._get_subscription_client(), None, callback)
    
    def count(self) -> int:
        """
        Returns the total number of key-value pairs in the cache.

        :returns number of key-value pairs
        """
        with self._lock:
            self._socket.sendall(_envelope.pack(MAGIC_WORD, CMD_COUNT_KEYS))
            mw, cmd = _envelope.unpack(self._rd.read(_envelope.size))

            count, = struct.unpack('I', self._rd.read(4))
        return count
    
    def keys(self) -> List[bytes]:
        """
        Retrieves all keys in the cache.

        :returns list of keys
        """
        with self._lock:
            self._socket.sendall(_envelope.pack(MAGIC_WORD, CMD_ALL_KEYS))
            mw, cmd = _envelope.unpack(self._rd.read(_envelope.size))

            num_keys, = struct.unpack('I', self._rd.read(4))

            keys = []

            for _ in range(num_keys):
                key_len, = _key_header.unpack(self._rd.read(_key_header.size))
                keys.append(self._rd.read(key_len))

        return keys
    
    def items(self) -> List[Tuple[bytes, bytes]]:
        """
        Retrieves all key-value pairs in the cache.

        :returns list of key-value pairs
        """
        with self._lock:
            self._socket.sendall(_envelope.pack(MAGIC_WORD, CMD_ALL_ITEMS))
            mw, cmd = _envelope.unpack(self._rd.read(_envelope.size))

            num_items, = struct.unpack('I', self._rd.read(4))
            
            items = []

            for _ in range(num_items):
                key_len, value_len = _key_value_header.unpack(self._rd.read(_key_value_header.size))
                items.append((self._rd.read(key_len), self._rd.read(value_len)))

        return items
    
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
        if self._closed: return
        with self._lock:
            self._refs -= 1
            if force or self._refs <= 0:
                # Close subscription client
                if self._sub_client:
                    self._sub_client.close()

                self._socket.sendall(_envelope.pack(MAGIC_WORD, CMD_DISCONNECT))
                self._socket.shutdown(socket.SHUT_RDWR)
                self._socket.close()
                self._refs = 0
            self._closed = True

def _try_unlink(filename: str) -> bool:
    """
    Tries to unlink a file.

    :param filename file to unlink
    :returns True if unlinked successfully
    """
    try:
        os.unlink(filename)
        return True
    except:
        return False

# Files to remove
_to_remove : List[str] = []

def _shutdown() -> None:
    """
    Signal / atexit shutdown handler.
    """
    for fn in _to_remove:
        _try_unlink(fn)

    # Force quicker shutdown -- whatever gets here first
    os._exit(0)

# Install signal handler and atexit handler
signal.signal(signal.SIGTERM, lambda _, __: _shutdown())
atexit.register(_shutdown)

def run_cache_server(filename: str, remove_file: bool, auto_kill: bool) -> None:
    """
    Starts a TCP-based cache server which emits its ephemeral
    port to a JSON file for clients.

    :param filename JSON output file
    :param remove_file removes JSON file when server completes
    :param auto_kill kill the TCP server when last client disconnects
    """
    if remove_file:
        _to_remove.append(filename)
    
    try:
        server = TCPServer(('127.0.0.1', 0), auto_kill)
        server_port = server.socket.getsockname()[1]
        with open(filename, 'w') as fd:
            fd.write(json.dumps({"port": server_port}))
        server.serve_forever()
    except ShutdownSignal:
        # Shutdown means we just pass through
        pass
