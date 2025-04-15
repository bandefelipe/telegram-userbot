import os
import re
import logging
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message
from emojis import EMOJIS

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
ID_GRUPO_AUTORIZADO = int(os.environ["ID_GRUPO_AUTORIZADO"])

# Templates
TEMPLATE_PRE = f'''
{EMOJIS["sinal_verde"]}OPORTUNIDADE DE ENTRADA CONFIRMADA {EMOJIS["bolsa_dinheiro"]}

👉🏻 BILHETE PRONTO AQUI! 👈🏻

{EMOJIS["presente"]}ODD  @{{X}} {EMOJIS["fogo"]}

{EMOJIS["seta_verde_direita"]}APOSTE {EMOJIS["dinheiro"]} 100
{EMOJIS["seta_verde_direita"]}RETORNO{EMOJIS["dinheiro"]} {{Y}}

{EMOJIS["carregando"]} PRE-JOGO ⏳

{EMOJIS["sirene_verde"]}APOSTE COM RESPONSABILIDADE{EMOJIS["maior_18"]}'''


TEMPLATE_AOVIVO = f'''
{EMOJIS["sinal_verde"]}OPORTUNIDADE DE ENTRADA CONFIRMADA {EMOJIS["bolsa_dinheiro"]}

👉🏻 BILHETE PRONTO AQUI! 👈🏻

{EMOJIS["presente"]}ODD  @{{X}} {EMOJIS["fogo"]}

{EMOJIS["seta_verde_direita"]}APOSTE {EMOJIS["dinheiro"]} 100
{EMOJIS["seta_verde_direita"]}RETORNO{EMOJIS["dinheiro"]} {{Y}}

{EMOJIS["bola_pulando"]} AO-VIVO 🛜

{EMOJIS["sirene_verde"]}APOSTE COM RESPONSABILIDADE{EMOJIS["maior_18"]}'''

app = Client(
    name="userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=open("user.session").read().strip()
)

@app.on_message(filters.photo & (filters.caption | filters.text))
async def processar_mensagem(client: Client, message: Message):
    if message.chat.id != ID_GRUPO_AUTORIZADO:
        return

    caption = message.caption or message.text or ""
    palavras = caption.strip().split()
    if not palavras or palavras[0].upper() not in ['PRE', 'AOVIVO']:
        return

    try:
        odd_str = palavras[1].replace(",", ".")
        float_valor = float(odd_str)
        retorno = int(round(float_valor * 100))
    except (IndexError, ValueError):
        await message.reply_text("❌ Não consegui entender a odd. Envie no formato: PRE 23,45 [link]")
        return

    match = re.search(r'shareCode=([A-Z0-9]+)', caption)
    link_final = None
    if match:
        share_code = match.group(1)
        link_final = f"https://go.aff.mcgames.bet/874az28c?shareCode={share_code}"

    template = TEMPLATE_PRE if palavras[0].upper() == 'PRE' else TEMPLATE_AOVIVO
    valor_formatado = f"{float_valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    texto_final = template.replace('{X}', valor_formatado).replace('{Y}', f"{retorno:,}".replace(",", "."))

    if link_final:
        texto_final = texto_final.replace(
            "👉🏻 CLIQUE AQUI! BILHETE PRONTO! 👈🏻",
            f'<a href="{link_final}">👉🏻 CLIQUE AQUI! BILHETE PRONTO! 👈🏻</a>'
        )

    foto = await message.download()
    await client.send_photo(
        chat_id=message.chat.id,
        photo=foto,
        caption=texto_final,
        parse_mode=ParseMode.HTML
    )

    try:
        await message.delete()
    except Exception as e:
        logging.warning(f"Erro ao apagar mensagem: {e}")

if __name__ == '__main__':
    print("🔵 Userbot rodando com Pyrogram...")
    app.run()
