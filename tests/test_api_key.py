import pytest
from fastapi.testclient import TestClient
from app.api.v1.key_management import router  # Adjust the import according to your structure
from fastapi import FastAPI
from unittest.mock import patch

app = FastAPI()
app.include_router(router)

client = TestClient(app)


# 模擬 FixedWindowRateLimiter 的行為
@pytest.fixture
def mock_rate_limiter():
    with patch("app.api.v1.key_management.FixedWindowRateLimiter.is_allowed") as mock:
        yield mock


@pytest.mark.parametrize(
    "mock_return_values, expected_status, expected_api_key",
    [
        ([True, True], 200, "api_key_1"),  # 測試成功獲取 API 金鑰
        ([False, False], 429, {"detail": "All API keys have reached their rate limits. Please try again later."}),       # 測試達到速率限制
        ([True, False], 200, "api_key_1"), # 測試第一個金鑰可用,第二個金鑰不可以用
        ([False, True], 200, "api_key_2"), # 測試第一個金鑰不可用,第二個金鑰可用
    ]
)
# 測試不同限流狀態來檢查 API 的行為
def test_get_api_key(mock_rate_limiter, mock_return_values, expected_status, expected_api_key):
    mock_rate_limiter.side_effect = mock_return_values

    response = client.post("/api-key", json={"type": "service_1"})

    assert response.status_code == expected_status
    if expected_status == 200:
        assert "api_key" in response.json()
        assert response.json()["api_key"] == expected_api_key
    else:
        assert response.json() == {"detail": "All API keys have reached their rate limits. Please try again later."}

@pytest.mark.parametrize("invalid_data", [
    {},  
    {"invalid_field": "value"}, 
    {"type": None}, 
    {"type": 123},  
])
# 測試無效請求格式
def test_invalid_request_format(invalid_data):
    response = client.post("/api-key", json=invalid_data)
    assert response.status_code == 422  # Unprocessable Entity (驗證失敗)

@pytest.mark.parametrize(
    "service_type, expected_status, expected_api_key",
    [
        ("service_1", 200, "api_key_1"),
        ("service_2", 200, "api_key_1"), 
        ("service_3", 200, "api_key_1"), 
    ]
)
# 測試不同的服務請求
def test_get_api_key_for_different_services(mock_rate_limiter, service_type, expected_status, expected_api_key):
    mock_rate_limiter.side_effect = [True, True]
    response = client.post("/api-key", json={"type": service_type})
    
    assert response.status_code == expected_status
    assert "api_key" in response.json()
    assert response.json()["api_key"] == expected_api_key
