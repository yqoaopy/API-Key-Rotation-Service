import pytest
from app.lib.fixed_window import FixedWindowRateLimiter
from datetime import datetime, timedelta


@pytest.mark.parametrize("tokens_needed, expected_allowance, expected_tokens", [
    (300, True, 700),  
    (500, True, 500),   
    (1000, True, 0),   
])
# 測試 token 配置的正確性
def test_token_allocation(tokens_needed, expected_allowance, expected_tokens):
    rate_limiter = FixedWindowRateLimiter(max_tokens=1000, window_seconds=60)
    assert rate_limiter.is_allowed(tokens_needed) is expected_allowance
    assert rate_limiter.current_tokens == expected_tokens

# 測試請求超過可用token的情況
def test_exceeding_tokens():
    rate_limiter = FixedWindowRateLimiter(max_tokens=1000, window_seconds=60)
    rate_limiter.is_allowed(300)
    rate_limiter.is_allowed(400)  
    rate_limiter.is_allowed(300)  
    assert rate_limiter.current_tokens == 0  

    assert rate_limiter.is_allowed(300) is False  

# 測試重置功能
def test_window_reset():
    rate_limiter = FixedWindowRateLimiter(max_tokens=1, window_seconds=1)
    assert rate_limiter.is_allowed(1) is True
    assert rate_limiter.is_allowed(1) is False 
    
    # 直接修改 window_start 模擬時間經過
    rate_limiter.window_start -= timedelta(seconds=2)
    
    assert rate_limiter.is_allowed(1) is True 


@pytest.mark.parametrize("requests, expected_last_request_result", [
    ([200, 200, 200, 200, 200], False),  
    ([100, 100, 100, 100], True),        
])
# 測試多次請求的情況
def test_multiple_requests(requests, expected_last_request_result):
    rate_limiter = FixedWindowRateLimiter(max_tokens=1000, window_seconds=60)
    
    for req in requests:
        assert rate_limiter.is_allowed(req) is True
    
    # 檢查最後一次請求是否符合 預期
    assert rate_limiter.is_allowed(200) is expected_last_request_result

@pytest.mark.parametrize("max_tokens, window_seconds, tokens_needed, expected_result", [
    (3, 1, 1, True),  
    (3, 1, 3, True),  
    (3, 1, 4, False), 
])
# 測試邊界條件
def test_boundary_conditions(max_tokens, window_seconds, tokens_needed, expected_result): 
    rate_limiter = FixedWindowRateLimiter(max_tokens=max_tokens, window_seconds=window_seconds)
    assert rate_limiter.is_allowed(tokens_needed) is expected_result