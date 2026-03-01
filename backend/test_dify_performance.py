import httpx
import time
import json
import os
from dotenv import load_dotenv

load_dotenv()

DIFY_API_URL = os.getenv("DIFY_API_URL", "http://localhost/v1")
DIFY_API_KEY = os.getenv("DIFY_API_KEY", "")

async def test_dify_speed():
    """测试Dify API的响应速度"""
    print("=" * 60)
    print("测试Dify工作流响应速度")
    print("=" * 60)
    
    headers = {
        'Authorization': f'Bearer {DIFY_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "inputs": {
            "input": "你好",
            "style": "专业分析"
        },
        "response_mode": "streaming",
        "user": "test_user"
    }
    
    print(f"\n发送到: {DIFY_API_URL}/workflows/run")
    print(f"Payload: {json.dumps(payload, ensure_ascii=False)}\n")
    
    start_time = time.time()
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        print(f"[{time.time() - start_time:.2f}s] 开始发送请求...")
        
        request_start = time.time()
        async with client.stream(
            'POST',
            f"{DIFY_API_URL}/workflows/run",
            headers=headers,
            json=payload
        ) as response:
            connection_time = time.time() - request_start
            print(f"[{time.time() - start_time:.2f}s] 收到响应状态码: {response.status_code}")
            print(f"连接耗时: {connection_time:.2f}秒\n")
            
            if response.status_code != 200:
                error = await response.aread()
                print(f"错误: {error.decode()}")
                return
            
            first_event = True
            event_count = 0
            
            async for line in response.aiter_lines():
                if line.startswith('data: '):
                    data_str = line[6:]
                    if data_str.strip():
                        try:
                            data = json.loads(data_str)
                            event = data.get('event')
                            event_count += 1
                            
                            if first_event:
                                first_event_time = time.time() - request_start
                                print(f"[{time.time() - start_time:.2f}s] 收到首个事件: {event}")
                                print(f"Dify处理耗时: {first_event_time:.2f}秒\n")
                                first_event = False
                            
                            print(f"[{time.time() - start_time:.2f}s] 事件 #{event_count}: {event}")
                            
                            if event == 'text_chunk':
                                text = data.get('data', {}).get('text', '')
                                print(f"  文本: {text[:50]}...")
                            
                            if event == 'workflow_finished':
                                total_time = time.time() - start_time
                                print(f"\n{'='*60}")
                                print(f"工作流完成!")
                                print(f"总耗时: {total_time:.2f}秒")
                                print(f"总事件数: {event_count}")
                                print(f"{'='*60}")
                                break
                                
                        except json.JSONDecodeError:
                            continue

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_dify_speed())
