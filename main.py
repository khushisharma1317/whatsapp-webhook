from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

VERIFY_TOKEN = "khushi_token_123"

# ⭐ IMPORTANT — Allow your Vercel domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://whatsapp-dashboard-zeta.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

messages_store = []

@app.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(content=challenge)

    return PlainTextResponse(content="Verification failed", status_code=400)

@app.post("/webhook")
async def receive_message(request: Request):
    data = await request.json()

    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        messages = value.get("messages")

        if messages:
            msg_text = messages[0]["text"]["body"]
            sender = messages[0]["from"]

            messages_store.append({
                "from": sender,
                "message": msg_text
            })

    except Exception as e:
        print("Error:", e)

    return {"status": "received"}

@app.get("/messages")
async def get_messages():
    return messages_store
