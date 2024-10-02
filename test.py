import requests
import json
import time
import threading
import datetime
# 服務定義
services = {
    "service_1": {"token_consumption": 300, "latency": 20},
    "service_2": {"token_consumption": 100, "latency": 10},
    "service_3": {"token_consumption": 500, "latency": 40},
}

def fetch_api_key(service_type):
    url = "http://127.0.0.1:8000/api/v1/api-key"
    payload = json.dumps({"type": service_type})
    headers = {'Content-Type': 'application/json'}
    
    response = requests.post(url, data=payload, headers=headers)
    
    if response.status_code == 200:
        response_data = response.json()  # 解析 JSON 響應
        
        print(f"{datetime.datetime.now()} {service_type}: {response_data}")
    else:
        print(f"Request failed for {service_type} with status {response.status_code}")

def send_request_with_delay(service_type, latency):
    for i in range(3):
        fetch_api_key(service_type)  # 發送請求
        time.sleep(latency)  # 獨立等待服務的延遲時間
        print(f"{datetime.datetime.now()} {service_type} has finished waiting for {latency} seconds.")

def control_requests():
    threads = []
    for service_type, details in services.items():
        latency = details["latency"]
        # 創建並啟動新執行緒以發送請求和等待
        thread = threading.Thread(target=send_request_with_delay, args=(service_type, latency))
        threads.append(thread)
        thread.start()

    # 等待所有執行緒完成
    for thread in threads:
        thread.join()

# 執行主程式
if __name__ == "__main__":
    control_requests()
