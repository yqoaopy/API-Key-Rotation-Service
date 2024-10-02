import aiohttp
import asyncio
import json
import datetime
import time

# 服務定義
services = {
    "service_1": {"latency": 20},
    "service_2": {"latency": 10},
    "service_3": {"latency": 40},
}


async def fetch_api_key(session, service_type):
    url = "http://127.0.0.1:8000/api/v1/api-key"
    payload = json.dumps({"type": service_type})
    headers = {"Content-Type": "application/json"}

    async with session.post(url, data=payload, headers=headers) as response:
        if response.status == 200:
            response_data = await response.json()
            print(f"{datetime.datetime.now()} {service_type}: {response_data}")
        else:
            print(f"Request failed for {service_type} with status {response.status}")


async def send_request_with_delay(service_type, latency, duration):
    start_time = time.time()
    async with aiohttp.ClientSession() as session:
        while time.time() - start_time < duration:
            await fetch_api_key(session, service_type)
            await asyncio.sleep(latency)
            print(
                f"{datetime.datetime.now()} {service_type} has finished waiting for {latency} seconds."
            )


async def control_requests(duration=300):
    tasks = []
    for service_type, details in services.items():
        latency = details["latency"]
        task = send_request_with_delay(service_type, latency, duration)
        tasks.append(task)
    await asyncio.gather(*tasks)


# 執行主程式
if __name__ == "__main__":
    asyncio.run(control_requests(600))
