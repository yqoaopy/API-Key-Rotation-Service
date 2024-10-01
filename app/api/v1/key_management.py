from fastapi import APIRouter, HTTPException
from app.lib.fixed_window import FixedWindowRateLimiter
from app.models.api_key import APIKeyRequest
from fastapi.responses import JSONResponse

router = APIRouter()

api_keys = {
    "api_key_1": FixedWindowRateLimiter(max_tokens=1000, window_seconds=60),
    "api_key_2": FixedWindowRateLimiter(max_tokens=3000, window_seconds=60),
}

service_token_usage = {
    "service_1": 300,
    "service_2": 100,
    "service_3": 500,
}


@router.post("/api-key")
async def get_api_key(request: APIKeyRequest):
    tokens_needed = service_token_usage[request.type]
    # 根據不同service處理對應的token數量
    for api_key, rate_limiter in api_keys.items():
        if rate_limiter.is_allowed(tokens_needed):
            return JSONResponse(status_code=200, content={"api_key": api_key})

    raise HTTPException(
        status_code=429,
        detail="All API keys have reached their rate limits. Please try again later.",
    )
