from pyrogram import Client
import os

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]

app = Client("bot", api_id=API_ID, api_hash=API_HASH)  # usa o .session que você gerou

@app.on_message()
async def monitorar(client, message):
    print(f"[{message.chat.title}] {message.from_user.first_name}: {message.text}")

if __name__ == "__main__":
    print("Rodando com conta Premium...")
    app.run()