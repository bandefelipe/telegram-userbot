import os
import re
import logging
import pytesseract
import numpy as np
from PIL import Image
from io import BytesIO
from typing import Optional
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message
import cv2

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
    session_string=open("user.session").read().strip()
)

async def extrair_valor_apos_label(imagem: Image.Image, chat_id: int, app: Client) -> Optional[str]:
    try:
        largura, altura = imagem.size
        y_inicio = int(altura * 0.60)
        recorte_inferior = imagem.crop((0, y_inicio, largura, altura))
        recorte_inferior.save("debug_1_recorte_inferior.png")

        # 🧪 Pré-processamento com OpenCV
        imagem_cv = cv2.cvtColor(np.array(recorte_inferior), cv2.COLOR_RGB2GRAY)
        imagem_cv = cv2.equalizeHist(imagem_cv)
        imagem_cv = cv2.adaptiveThreshold(
            imagem_cv, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        cv2.imwrite("debug_2_binarizada.png", imagem_cv)
        
        # OCR com pytesseract
        texto = pytesseract.image_to_string(recorte_inferior, lang='por')
        logging.info(f"[OCR-pytesseract] Texto extraído:\n{texto}")
        await app.send_message(chat_id, f"[OCR] Texto após pytesseract:\n{texto}")

        linhas = texto.splitlines()
        for linha in linhas:
            if "cota" in linha.lower() and "totais" in linha.lower():
                logging.info(f"[OCR] Linha com label encontrada: {linha}")
        
                # Tenta extrair com regex direto da linha
                match = re.search(r"totais[:\s\-]*([\d.,]+)", linha.lower())
                if match:
                    valor = match.group(1).replace(',', '.')
                    logging.info(f"[OCR] Valor extraído com regex da linha: {valor}")
                    return valor
        
                # Se regex falhar, tenta split manual como fallback
                partes = linha.split()
                for i, parte in enumerate(partes):
                    if "totais" in parte.lower():
                        try:
                            valor = partes[i+1].replace(',', '.')
                            logging.info(f"[OCR] Valor extraído como fallback: {valor}")
                            return valor
                        except IndexError:
                            continue

        await app.send_message(chat_id, "⚠️ Não consegui identificar a cotação. Enviando imagens de debug:")
        await app.send_photo(chat_id, "debug_1_recorte_inferior.png", caption="📸 Recorte Inferior")
        await app.send_photo(chat_id, "debug_2_binarizada.png", caption="📸 Imagem binarizada")
        os.remove("debug_1_recorte_inferior.png")
        os.remove("debug_2_binarizada.png")
        return None

    except Exception as e:
        logging.error(f"[OCR-pytesseract] Erro inesperado: {e}")
        await app.send_message(chat_id, f"❌ Erro ao processar imagem com pytesseract: {e}")
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
        valor = await extrair_valor_apos_label(imagem, message.chat.id, app)

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
