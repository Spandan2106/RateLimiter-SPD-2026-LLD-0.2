
import time
import threading
from collections import deque
from fastapi import HTTPException


class RateLimitExceeded(HTTPException):
    def __init__(self, detail="Rate limit exceeded"):
        super().__init__(status_code=429, detail=detail)


class RateLimit:
    def __init__(self, limit=10, interval=60):
        self.limit_per_interval = limit
        self.interval = interval
        self.lock = threading.Lock()


# 1. Token Bucket
class TokenBucket(RateLimit):
    def __init__(self):
        super().__init__(limit=10, interval=60)
        self.capacity = 10
        self.tokens = float(self.capacity)
        self.refill_rate = 1  # Tokens per second
        self.last_updated = time.monotonic()

    def allow_request(self, ip=None):
        with self.lock:
            now = time.monotonic()
            elapsed = now - self.last_updated

            self.tokens = min(
                self.capacity,
                self.tokens + elapsed * self.refill_rate
            )
            self.last_updated = now

            if self.tokens >= 1:
                self.tokens -= 1
                return True

            raise RateLimitExceeded()


# 2. Fixed Window Counter
class FixedCounterWindow(RateLimit):
    def __init__(self):
        super().__init__(limit=10, interval=60)
        self.counter = 0
        self.window_id = int(time.monotonic() // self.interval)

    def allow_request(self, ip=None):
        with self.lock:
            current_window = int(
                time.monotonic() // self.interval
            )

            if current_window != self.window_id:
                self.window_id = current_window
                self.counter = 0

            if self.counter >= self.limit_per_interval:
                raise RateLimitExceeded()

            self.counter += 1
            return True


# 3. Sliding Window Log
class SlidingWindow(RateLimit):
    def __init__(self):
        super().__init__(limit=10, interval=60)
        self.logs = deque()

    def allow_request(self, ip=None):
        with self.lock:
            now = time.monotonic()

            while (
                self.logs
                and now - self.logs[0] >= self.interval
            ):
                self.logs.popleft()

            if len(self.logs) >= self.limit_per_interval:
                raise RateLimitExceeded()

            self.logs.append(now)
            return True


# 4. Sliding Window Counter
class SlidingWindowCounter(RateLimit):
    def __init__(self):
        super().__init__(limit=10, interval=60)
        self.previous_count = 0
        self.current_count = 0
        self.window_id = int(time.monotonic() // self.interval)

    def allow_request(self, ip=None):
        with self.lock:
            now = time.monotonic()
            current_window = int(now // self.interval)
            elapsed = now % self.interval

            if current_window != self.window_id:
                if current_window == self.window_id + 1:
                    self.previous_count = self.current_count
                else:
                    self.previous_count = 0

                self.current_count = 0
                self.window_id = current_window

            previous_weight = (
                self.interval - elapsed
            ) / self.interval

            estimated_count = (
                self.previous_count * previous_weight
                + self.current_count
            )

            if estimated_count >= self.limit_per_interval:
                raise RateLimitExceeded()

            self.current_count += 1
            return True
