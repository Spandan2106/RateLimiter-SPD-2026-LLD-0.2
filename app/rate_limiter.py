from .limiting_algorithms import (
    FixedCounterWindow,
    TokenBucket,
    SlidingWindow,
    SlidingWindowCounter,
)
class RateLimitFactory:

    @staticmethod
    def get_instance(algorithm: str):
        if algorithm == "TokenBucket":
            return TokenBucket()

        elif algorithm == "FixedCounterWindow":
            return FixedCounterWindow()

        elif algorithm == "SlidingWindow":
            return SlidingWindow()

        elif algorithm == "SlidingWindowCounter":
            return SlidingWindowCounter()

        else:
            raise ValueError(
                f"Unknown rate-limiting algorithm: {algorithm}"
            )
