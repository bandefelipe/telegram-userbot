from pyrogram import Client

app = Client("bot")  # Usa bot.session

async def main():
    await app.start()
    await app.send_message("me", "✅ Sessão Premium ativa!")
    await app.stop()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())