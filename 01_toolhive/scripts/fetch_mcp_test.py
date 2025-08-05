import aiohttp
import asyncio
import json
import uuid

MCP_URL = "http://127.0.0.1:19030/mcp"

async def mcp_client():
    async with aiohttp.ClientSession() as session:
        # SSE 연결 열기
        async with session.post(
            MCP_URL,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            },
            data=json.dumps({
                "jsonrpc": "2.0",
                "id": "listTools",
                "method": "initialize",
                "params": {
                    "capabilities": {},
                    "clientInfo": {
                        "name": "python-sse-client",
                        "version": "1.0.0"
                    }
                }
            })
        ) as resp:
            print("Connected:", resp.__dict__)
            print("--------------------------------")
            print(resp.text)
            print("--------------------------------")
            async for line in resp.content:
                
                decoded = line.decode().strip()
                if decoded.startswith("data: "):
                    msg = json.loads(decoded[6:])
                    print("📥 Received:", json.dumps(msg, indent=2))

                    
                    # initialize 성공 후 listTools 요청
                    if msg.get("id") and msg["id"] != "listTools":
                        list_tools_req = {
                            "jsonrpc": "2.0",
                            "id": "1",
                            "method": "listTools",
                            "params": {}
                        }
                        await session.post(
                            MCP_URL,
                            headers={
                                "Content-Type": "application/json",
                                "Accept": "application/json, text/event-stream"
                            },
                            data=json.dumps(list_tools_req)
                        )

                    # listTools 결과에서 툴 이름 확인 후 callTool 실행
                    
                    

                    if msg.get("id") == "listTools" and "result" in msg:
                        tools = msg["result"].get("tools", [])
                        print("🔧 Available tools:", tools)
                        if tools:
                            first_tool = tools[0]["name"]
                            call_tool_req = {
                                "jsonrpc": "2.0",
                                "id": "1",
                                "method": "callTool",
                                "params": {
                                    "name": first_tool,
                                    "arguments": {
                                        "url": "https://metashower.tistory.com"
                                    }
                                }
                            }
                            result  = await session.post(
                                MCP_URL,
                                headers={
                                    "Content-Type": "application/json",
                                    "Accept": "application/json, text/event-stream"
                                },
                                data=json.dumps(call_tool_req)
                            )
                            print("--------------------------------")
                            print(result.text)

                    if msg.get("id") == "callTool":
                        print("✅ callTool result:", msg["result"])
                        return  # 종료

asyncio.run(mcp_client())