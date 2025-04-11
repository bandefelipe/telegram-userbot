from pyrogram.client import Client
import os
import asyncio

# Substitua pelos dados da sua conta (não do bot)
API_ID = 20238661  # coloque seu API_ID aqui
API_HASH = "d41b8480695c3aca5959537080e6ebd6"  # coloque seu API_HASH aqui

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