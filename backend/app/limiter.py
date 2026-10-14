from collections import defaultdict, deque
from threading import Lock
from time import monotonic


class SlidingWindowLimiter:
    def __init__(self):
        self._history = defaultdict(deque)
        self._lock = Lock()

    def check(self, client_ip: str, max_requests: int, window_seconds: int):
        now = monotonic()
        with self._lock:
            queue = self._history[client_ip]
            while queue and queue[0] <= now - window_seconds:
                queue.popleft()
            if len(queue) >= max_requests:
                retry_after = max(1, int(queue[0] + window_seconds - now) + 1)
                return False, 0, retry_after
            queue.append(now)
            return True, max_requests - len(queue), 0

    def reset(self):
        with self._lock:
            self._history.clear()
