
from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .rate_limiter import RateLimitFactory
from .limiting_algorithms import RateLimitExceeded

app = FastAPI(title="Rate Limiter API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Store a separate limiter for each client and algorithm
ip_addresses = {}

ALGORITHMS = {
    "token_bucket": "TokenBucket",
    "fixed_window": "FixedCounterWindow",
    "sliding_window": "SlidingWindow",
    "sliding_window_counter": "SlidingWindowCounter",
}


@app.get("/")
def home():
    return {"message": "Rate Limiter API is running"}


@app.get("/limited")
def limited(
    request: Request,
    algorithm: str = Query(...),
    client_id: str = Query("default")
):
    if algorithm not in ALGORITHMS:
        raise HTTPException(
            status_code=400,
            detail="Invalid rate-limiting algorithm"
        )

    client = request.client.host
    key = (client, client_id, algorithm)

    if key not in ip_addresses:
        ip_addresses[key] = RateLimitFactory.get_instance(
            ALGORITHMS[algorithm]
        )

    limiter = ip_addresses[key]

    try:
        if limiter.allow_request():
            return {
                "allowed": True,
                "message": "This is a limited-use API",
                "algorithm": algorithm,
                "client_id": client_id
            }

        raise RateLimitExceeded()

    except RateLimitExceeded:
        raise HTTPException(
            status_code=429,
            detail="Too many requests"
        )


@app.get("/unlimited")
def unlimited():
    return {"message": "Free to use API without a rate limit"}
