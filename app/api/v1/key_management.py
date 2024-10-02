from fastapi import APIRouter, HTTPException
from app.lib.fixed_window import FixedWindowRateLimiter
from app.models.api_key import APIKeyRequest
from fastapi.responses import JSONResponse
from app.lib.logger import setup_logger


logger = setup_logger("api_key_service.log")

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


@router.post(
    "/api-key",
    summary="Get API Key",
    description="Get an available API key based on the service type.",
    response_description="Returns the available API key.",
    responses={
        200: {
            "description": "Available API key returned.",
            "content": {"application/json": {"example": {"api_key": "api_key_1"}}},
        },
        422: {
            "description": "Validation error occurred, such as missing or incorrect data.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "type"],
                                "msg": "field required",
                                "type": "value_error.missing",
                            }
                        ]
                    }
                }
            },
        },
        429: {
            "description": "All API keys have reached their rate limits.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "All API keys have reached their rate limits. Please try again later."
                    }
                }
            },
        },
    },
)
async def get_api_key(request: APIKeyRequest):
    tokens_needed = service_token_usage[request.type]
    # 根據不同service處理對應的token數量
    for api_key, rate_limiter in api_keys.items():
        if rate_limiter.is_allowed(tokens_needed):
            logger.info(
                f"API Key: {api_key} - Remaining Tokens: {rate_limiter.current_tokens}"
            )
            return JSONResponse(status_code=200, content={"api_key": api_key})

    logger.error("All API keys have reached their rate limits.")
    raise HTTPException(
        status_code=429,
        detail="All API keys have reached their rate limits. Please try again later.",
    )

