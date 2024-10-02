from datetime import datetime, timedelta
import time


class FixedWindowRateLimiter:
    def __init__(self, max_tokens, window_seconds):
        self.max_tokens = max_tokens
        self.window_seconds = window_seconds
        self.current_tokens = max_tokens
        self.window_start = datetime.now()

    def is_allowed(self, tokens_needed):
        current_time = datetime.now()

        # 檢查是否進入新的窗口
        if current_time >= self.window_start + timedelta(seconds=self.window_seconds):
            # 進入新的窗口，重置 tokens 和窗口開始時間
            self.current_tokens = self.max_tokens
            self.window_start = current_time

        # 檢查可用token數是否足夠處理
        if self.current_tokens >= tokens_needed:
            self.current_tokens -= tokens_needed
            return True
        return False


# Example Usage
if __name__ == "__main__":
    rate_limiter = FixedWindowRateLimiter(max_tokens=1000, window_seconds=60)

    tokens_needed = 300
    for i in range(20):
        if rate_limiter.is_allowed(tokens_needed):
            print(f"Request {i+1}: Allowed")
        else:
            print(f"Request {i+1}: Not Allowed")
        time.sleep(1)
