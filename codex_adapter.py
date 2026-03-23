"""
Codex-to-ChatCompletions Adapter Proxy

Codex API (claudechn.com) 只支持 /v1/responses 格式 (SSE streaming)
CrewAI 只支持 /v1/chat/completions 格式

这个代理把 CrewAI 的 chat/completions 请求转成 Codex 的 responses 格式
"""
import json
import os
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

CODEX_BASE_URL = os.getenv("CODEX_BASE_URL", "https://claudechn.com/codex")
CODEX_API_KEY = os.getenv("CODEX_API_KEY", "")

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()

    model = body.get("model", "gpt-5.4")
    messages = body.get("messages", [])
    max_tokens = body.get("max_tokens", 4096)

    # 把 messages 里的 system 提取出来作为 instructions
    instructions = ""
    input_messages = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "system":
            instructions += content + "\n"
        else:
            input_messages.append({"role": role, "content": content})

    # 如果只有一条 user 消息，直接用 input 字符串
    if len(input_messages) == 1 and input_messages[0]["role"] == "user":
        input_data = input_messages[0]["content"]
    else:
        input_data = input_messages

    codex_payload = {
        "model": model,
        "input": input_data,
        "max_output_tokens": max_tokens,
        "stream": True,
    }
    if instructions.strip():
        codex_payload["instructions"] = instructions.strip()

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CODEX_API_KEY}",
    }

    # 用流式读取来处理 SSE 响应，避免超时
    output_text = ""
    response_id = "chatcmpl-codex"
    model_name = model
    usage = {}

    async with httpx.AsyncClient(timeout=300.0) as client:
        async with client.stream(
            "POST",
            f"{CODEX_BASE_URL}/v1/responses",
            json=codex_payload,
            headers=headers,
        ) as response:
            async for line in response.aiter_lines():
                if not line.startswith("data: "):
                    continue
                try:
                    data = json.loads(line[6:])
                    event_type = data.get("type", "")

                    if event_type == "response.output_text.done":
                        output_text = data.get("text", "")

                    if event_type == "response.completed":
                        resp = data.get("response", {})
                        response_id = resp.get("id", response_id)
                        model_name = resp.get("model", model)
                        usage = resp.get("usage", {})

                except json.JSONDecodeError:
                    continue

    # 转换为 ChatCompletion 格式
    chat_response = {
        "id": response_id,
        "object": "chat.completion",
        "created": 0,
        "model": model_name,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": output_text,
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": usage.get("input_tokens", 0),
            "completion_tokens": usage.get("output_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
        },
    }

    return JSONResponse(content=chat_response)


@app.get("/health")
async def health():
    return {"status": "ok", "adapter": "codex-to-chatcompletions"}


if __name__ == "__main__":
    port = int(os.getenv("CODEX_PROXY_PORT", "8081"))
    print(f"[codex-adapter] Starting on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
