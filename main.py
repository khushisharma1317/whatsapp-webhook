from fastapi import FastAPI, Request

app = FastAPI()

VERIFY_TOKEN = "khushi_token_123"

@app.get("/webhook")
async def verify_webhook(hub_mode: str = None, hub_challenge: str = None, hub_verify_token: str = None):
    if hub_verify_token == VERIFY_TOKEN:
        return int(hub_challenge)
    return {"error": "Invalid token"}

@app.post("/webhook")
async def receive_message(request: Request):
    data = await request.json()
    print("Incoming message:", data)
    return {"status": "received"}
