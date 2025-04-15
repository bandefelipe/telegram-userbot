import os
import re
import logging
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message
from emojis import EMOJIS
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
ID_GRUPO_AUTORIZADO = int(os.environ["ID_GRUPO_AUTORIZADO"])

# Templates
TEMPLATE_PRE = f'''
{EMOJIS["sinal_verde"]}OPORTUNIDADE DE ENTRADA CONFIRMADA {EMOJIS["bolsa_dinheiro"]}

👉🏻 <b>BILHETE PRONTO AQUI!</b> 👈🏻

{EMOJIS["presente"]} ODD  <b>@{{X}}</b> {EMOJIS["fogo"]}

{EMOJIS["seta_verde_direita"]}APOSTE {EMOJIS["dinheiro"]} <b>100</b>
{EMOJIS["seta_verde_direita"]}RETORNO{EMOJIS["dinheiro"]} <b>{{Y}}</b>

{EMOJIS["carregando"]} <b>PRE-JOGO</b> ⏳

{EMOJIS["sirene_verde"]}APOSTE COM RESPONSABILIDADE{EMOJIS["maior_18"]}'''


TEMPLATE_AOVIVO = f'''
{EMOJIS["sinal_verde"]}OPORTUNIDADE DE ENTRADA CONFIRMADA {EMOJIS["bolsa_dinheiro"]}

👉🏻 <b>BILHETE PRONTO AQUI!</b> 👈🏻

{EMOJIS["presente"]} ODD  <b>@{{X}}</b> {EMOJIS["fogo"]}

{EMOJIS["seta_verde_direita"]}APOSTE {EMOJIS["dinheiro"]} <b>100</b>
{EMOJIS["seta_verde_direita"]}RETORNO{EMOJIS["dinheiro"]} <b>{{Y}}</b>

{EMOJIS["bola_pulando"]} <b>AO-VIVO</b> 🛜

{EMOJIS["sirene_verde"]}APOSTE COM RESPONSABILIDADE{EMOJIS["maior_18"]}'''

TEMPLATE_SUPER = f'''
{EMOJIS['sinal_verde']} OPORTUNIDADE ÚNICA DE SUPER ODD! {EMOJIS['fogo']}

{EMOJIS["sirene_verde"]}{EMOJIS["sirene_verde"]}{EMOJIS["sirene_verde"]}{EMOJIS["sirene_verde"]}{EMOJIS["sirene_verde"]}
{EMOJIS["seta_verde_direita"]} <b>{{DESCRICAO}}</b>
{EMOJIS["sirene_verde"]}{EMOJIS["sirene_verde"]}{EMOJIS["sirene_verde"]}{EMOJIS["sirene_verde"]}{EMOJIS["sirene_verde"]}

{EMOJIS['dinheiro']} Ganho praticamente <b>GARANTIDO</b> com essa odd absurda! {EMOJIS['dinheiro']} 

{EMOJIS["presente"]} ODD ESPECIAL: <b>@{{X}}</b> {EMOJIS["fogo"]}

👉🏻 <b>BILHETE PRONTO AQUI!</b> 👈🏻

{EMOJIS["bola_pulando"]} <b>SUPER-ODD</b> {EMOJIS['dinheiro']}
'''


app = Client(
    name="userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=open(".secrets/user.session").read().strip()
)

@app.on_message(filters.photo & (filters.caption | filters.text))
async def processar_mensagem(client: Client, message: Message):
    if message.chat.id != ID_GRUPO_AUTORIZADO:
        return

    caption = message.caption or message.text or ""
    palavras = caption.strip().split()
    if not palavras or palavras[0].upper() not in ['PRE', 'AOVIVO', 'SUPER']:
        return

    tipo = palavras[0].upper()

    foto = await message.download()

    # 🔸 Caso SUPER
    if tipo == 'SUPER':
        if len(palavras) < 3:
            await message.reply_text("❌ Formato incorreto. Use: SUPER [odd] [descrição] [link opcional]")
            return

        try:
            odd_str = palavras[1].replace(",", ".")
            float_valor = float(odd_str)
        except ValueError:
            await message.reply_text("❌ Odd inválida.")
            return

                # Junta tudo depois da odd
        descricao_com_link = " ".join(palavras[2:])
        
        # Verifica se tem link com shareCode e separa
        match = re.search(r'(https?://\S*shareCode=\w+)', descricao_com_link)
        link_final = match.group(1) if match else None
        descricao = descricao_com_link.replace(link_final, '').strip() if link_final else descricao_com_link

        match = re.search(r'shareCode=([A-Z0-9]+)', caption)
        link_final = None
        if match:
            share_code = match.group(1)
            link_final = f"https://go.aff.mcgames.bet/874az28c?shareCode={share_code}"

        valor_formatado = f"{float_valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        texto_final = TEMPLATE_SUPER.replace('{X}', valor_formatado).replace('{DESCRICAO}', descricao)

        if link_final:
            texto_final = texto_final.replace(
                "👉🏻 <b>BILHETE PRONTO AQUI!</b> 👈🏻",
                f'<a href="{link_final}">👉🏻 <b>BILHETE PRONTO AQUI!</b> 👈🏻</a>'
            )

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
        return

    # 🔹 Caso PRE ou AOVIVO
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

    template = TEMPLATE_PRE if tipo == 'PRE' else TEMPLATE_AOVIVO
    valor_formatado = f"{float_valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    texto_final = template.replace('{X}', valor_formatado).replace('{Y}', f"{retorno:,}".replace(",", "."))

    if link_final:
        texto_final = texto_final.replace(
        "👉🏻 <b>BILHETE PRONTO AQUI!</b> 👈🏻",
        f'<a href="{link_final}">👉🏻 <b>BILHETE PRONTO AQUI!</b> 👈🏻</a>'
        )

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
