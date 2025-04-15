from pyrogram.client import Client
import os
import asyncio

# Substitua pelos dados da sua conta (não do bot)
API_ID = 21475448  # coloque seu API_ID aqui
API_HASH = "6105d23a50ec2e98e33779dd13496466"  # coloque seu API_HASH aqui

async def main():
    app = Client("user_setup", api_id=API_ID, api_hash=API_HASH)

    await app.start()
    print("✅ Login realizado com sucesso!")

    session_string = await app.export_session_string()

    # Salva a sessão de forma segura
    os.makedirs(".secrets", exist_ok=True)
    with open(".secrets/user.session", "w") as f:
        f.write(session_string)

    print("✅ Sessão salva com sucesso em .secrets/user.session")
    print("❗ Guarde esse arquivo com cuidado. Nunca compartilhe!")

    await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
