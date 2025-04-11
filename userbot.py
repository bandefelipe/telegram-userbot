import os
from pyrogram import Client, filters
from pyrogram.types import Message
from PIL import Image
import pytesseract
import re
import logging
from io import BytesIO
from pyrogram.enums import ParseMode

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
ID_GRUPO_AUTORIZADO = int(os.environ["ID_GRUPO_AUTORIZADO"])

# Templates
TEMPLATE_PRE = '''
🚨OPORTUNIDADE DE ENTRADA CONFIRMADA 💰

👉🏻 CLIQUE AQUI! BILHETE PRONTO! 👈🏻

✅ODD  @{X}

➡️APOSTE 💸 100
➡️RETORNO💸 {Y}

⏳ PRE-JOGO 🖼️

🚨 APOSTE COM RESPONSABILIDADE🔞'''

TEMPLATE_AOVIVO = '''
🚨OPORTUNIDADE DE ENTRADA CONFIRMADA 💰

👉🏻 CLIQUE AQUI! BILHETE PRONTO! 👈🏻

✅ODD  @{X}

➡️APOSTE 💸 100
➡️RETORNO💸 {Y}

🔴 AO-VIVO 🖼️

🚨 APOSTE COM RESPONSABILIDADE🔞'''

LABEL = "Cotações totais"

app = Client(
    name="userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string = open("/etc/secrets/user.session").read().strip()
)

def extrair_valor_apos_label(imagem: Image.Image):
    texto = pytesseract.image_to_string(imagem, lang='por')
    logging.info(f"[OCR] Texto extraído:\n{texto}")
    linhas = texto.splitlines()
    for linha in linhas:
        if LABEL.lower() in linha.lower():
            logging.info(f"[OCR] Linha com label encontrada: {linha}")
            partes = linha.split()
            for i, parte in enumerate(partes):
                if LABEL.split()[0].lower() in parte.lower():
                    try:
                        valor = partes[i+2] if partes[i+1].lower() == 'totais' else partes[i+1]
                        return valor.replace(',', '.')
                    except IndexError:
                        continue
    return None

def corrigir_valor_ocr(valor: str) -> str:
    if '.' in valor:
        return valor
    if valor.isdigit():
        if len(valor) == 3:
            return f"{valor[:-2]}.{valor[-2:]}"
        elif valor.endswith("00"):
            return f"{valor[:-2]}.{valor[-2:]}"
    return valor

@app.on_message(filters.photo & (filters.caption | filters.text))
async def processar_mensagem(client: Client, message: Message):
    if message.chat.id != ID_GRUPO_AUTORIZADO:
        return

    caption = message.caption or message.text or ""
    palavras = caption.strip().split()
    if not palavras or palavras[0].upper() not in ['PRE', 'AOVIVO']:
        return

    foto = await message.download()
    with Image.open(foto) as imagem:
        valor = extrair_valor_apos_label(imagem)

    if not valor:
        await message.reply_text("Não consegui identificar a cotação na imagem.")
        return

    valor = corrigir_valor_ocr(valor)

    match = re.search(r'shareCode=([A-Z0-9]+)', caption)
    link_final = None
    if match:
        share_code = match.group(1)
        link_final = f"https://go.aff.mcgames.bet/874az28c?shareCode={share_code}"

    try:
        valor = valor.replace(',', '').strip()
        valor_limpo = re.sub(r"[^\d.]", "", valor)
        partes = valor_limpo.split(".")
        if len(partes) > 2:
            valor_corrigido = "".join(partes[:-1]) + "." + partes[-1]
        else:
            valor_corrigido = valor_limpo
        try:
            float_valor = float(valor_corrigido)
            retorno = int(round(float_valor * 100))
        except ValueError:
            await message.reply_text(f"Erro ao converter o valor '{valor}' em número.")
            return
    except:
        await message.reply_text("Erro ao calcular o valor de retorno.")
        return

    template = TEMPLATE_PRE if palavras[0].upper() == 'PRE' else TEMPLATE_AOVIVO
    valor_formatado = f"{float_valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    texto_final = template.replace('{X}', valor_formatado).replace('{Y}', f"{retorno:,}".replace(",", "."))

    if link_final:
        texto_final = texto_final.replace(
            "👉🏻 CLIQUE AQUI! BILHETE PRONTO! 👈🏻",
            f'<a href="{link_final}">👉🏻 CLIQUE AQUI! BILHETE PRONTO! 👈🏻</a>'
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
