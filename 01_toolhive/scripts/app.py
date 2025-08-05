from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from playwright.async_api import async_playwright
import asyncio
import json
import uuid

app = FastAPI()
sessions = {}

@app.get("/sse")
async def sse_endpoint():
    session_id = str(uuid.uuid4())
    sessions[session_id] = {}
    async def event_stream():
        yield f"event: endpoint\ndata: /sse?sessionId={session_id}\n\n"
    return StreamingResponse(event_stream(), media_type="text/event-")

@app.post("/message")
async def message_endpoint(sessionId: str, request: Request):
    data = await request.json()
    print("data : ", data)
    method = data.get("method")

    if method == "initialize":
        sessions[sessionId]["initialized"] = True
        return JSONResponse({"jsonrpc": "2.0", "id": data["id"], "result": "ok"})

    if method == "callTool" and sessions[sessionId].get("initialized"):
        params = data.get("params", {})
        name = params.get("name")
        args = params.get("arguments", {})

        if name == "navigate":
            async with async_playwright() as pw:
                browser = await pw.chromium.launch()
                page = await browser.new_page()
                await page.goto(args["url"])
                title = await page.title()
                await browser.close()
            return JSONResponse({"jsonrpc": "2.0", "id": data["id"], "result": {"title": title}})

    return JSONResponse({"jsonrpc": "2.0", "error": {"code": -32000, "message": "Bad Request"}})