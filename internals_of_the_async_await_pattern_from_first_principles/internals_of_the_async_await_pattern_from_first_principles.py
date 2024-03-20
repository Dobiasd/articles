import time
from collections import deque
from operator import itemgetter
from select import select
from socket import socket, AF_INET, SOCK_STREAM
from typing import Deque, Any, Dict, Tuple, Awaitable, Generator


class Executor:
    current = None
    _ready: Deque[Any] = deque()
    _scheduled: Deque[Any] = deque()
    _read_pending: Dict[Any, Any] = {}
    _write_pending: Dict[Any, Any] = {}

    def submit(self, coroutine) -> None:
        self._ready.append(coroutine)

    def schedule(self, timestamp, coroutine) -> None:
        self._scheduled.append((timestamp, coroutine))
        # A real priority queue would do this automatically and more efficiently.
        self._scheduled = deque(sorted(self._scheduled, key=itemgetter(0)))

    def run(self) -> None:
        while any([self._ready, self._scheduled, self._read_pending, self._write_pending]):
            if not self._ready:
                timeout = None
                if self._scheduled:
                    wakeup_time = self._scheduled[0][0]
                    timeout = max(0, wakeup_time - time.time())

                # Sleep till the timeout expires or a handle becomes ready.
                read_ready, write_ready, _ = select(self._read_pending.keys(),
                                                    self._write_pending.keys(),
                                                    [], timeout)
                for handle in read_ready:
                    self.submit(self._read_pending.pop(handle))
                for handle in write_ready:
                    self.submit(self._write_pending.pop(handle))

                now = time.time()
                while self._scheduled:
                    if now >= self._scheduled[0][0]:
                        self.submit(self._scheduled.pop()[1])
                    else:
                        break

            self.current = self._ready.popleft()
            try:
                # Step the current coroutine for one state transition.
                self.current.send(None)
                # We only re-submit the coroutine when it was not removed/scheduled by async_sleep.
                if self.current:
                    self.submit(self.current)
                    self.current = None
            except StopIteration:
                pass

    def wait_for_write(self, handle, coroutine) -> None:
        self._write_pending[handle] = coroutine

    async def accept(self, sock) -> Tuple[Any, Tuple[str, int]]:
        self._read_pending[sock] = executor.current
        self.current = None
        await YieldOnAwait()
        return sock.accept()

    async def recv(self, sock, max_bytes) -> bytes:
        self._read_pending[sock] = self.current
        self.current = None
        await YieldOnAwait()
        return sock.recv(max_bytes)

    async def send(self, sock, data) -> None:
        self.wait_for_write(sock, self.current)
        self.current = None
        await YieldOnAwait()
        return sock.send(data)


executor = Executor()


# A python technicality - we need an awaitable to switch tasks.
class YieldOnAwait(Awaitable):
    def __await__(self) -> Generator:
        yield


async def async_sleep(duration) -> None:
    executor.schedule(time.time() + duration, executor.current)
    executor.current = None
    await YieldOnAwait()


def sync_sleep(duration) -> None:
    if duration > 0:
        time.sleep(duration)


async def foo() -> None:
    print("a")
    await async_sleep(1)
    print("b")
    await async_sleep(1)
    print("c")


async def bar() -> None:
    print("x")
    await async_sleep(1)
    print("y")
    await async_sleep(1)
    print("z")


def open_socket(host: str, port: int) -> Any:
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(1)
    return sock


async def tcp_server():
    server_sock = open_socket("", 8080)
    while True:
        client_sock, address = await executor.accept(server_sock)
        print(f"Accepted connection from {address}")
        executor.submit(echo_handler(client_sock))


async def echo_handler(sock):
    while True:
        data = await executor.recv(sock, 10000)
        if not data:
            break
        await executor.send(sock, b'echo ' + data)
    print("Connection closed")
    sock.close()


executor.submit(foo())
executor.submit(bar())
executor.submit(tcp_server())
executor.run()
# Cou can try it out like that (linux): nc localhost 8080
