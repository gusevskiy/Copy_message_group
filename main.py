import asyncio
import logging
from datetime import datetime
import os
import ast
from typing import List
from pyrogram import Client, filters
from pyrogram.enums import MessageMediaType
from pyrogram.types import (
    Message,
    InputMediaDocument,
    InputMediaPhoto,
    InputMediaVideo,
)
from dotenv import load_dotenv, find_dotenv

load_dotenv()

log_dir = "./logs"
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    format="[%(levelname) 5s] [%(asctime)s] [%(name)s.%(funcName)s:%(lineno)d]: %(message)s",
    level=logging.INFO,
    filename=os.path.join(log_dir, f"log_{datetime.now().strftime('%Y-%m-%d')}.log"),
)

donor_chat = ast.literal_eval(os.getenv("DONOR"))
logging.info(donor_chat)
recipient_chat = int(os.getenv("RECIPIENT"))
logging.info(recipient_chat)
file_session = str(os.getenv("FILESESSION"))
logging.info(file_session)

app = Client(file_session) 

processed_media_groups = set()


async def edit_text_caption(text: str) -> str:
    """
    Обрезаю текст у сообщений у которых text or caption > 1024
    тк это сообщение переданые с перемиум аккаунтов у них = 4024 
    """
    if len(text) > 1020:
        return text[:1020]
    else:
        return text


async def download_and_prepare_media(
        client: Client, media_group: List[Message]
) -> List:
    """
    Скачивает медиа из медиагруппы и формирует список объектов InputMedia.
    """
    tasks, captions, types = [], [], []

    for msg in media_group:
        if msg.media:
            tasks.append(client.download_media(msg, in_memory=True))
            captions.append(await edit_text_caption(msg.caption) if msg.caption else "")
            types.append(
                "photo" if msg.photo else
                "video" if msg.video else
                "document" if msg.document else None
            )

    files = await asyncio.gather(*tasks)

    return [
        InputMediaPhoto(media=file, caption=caption) if type_ == "photo" else
        InputMediaVideo(media=file, caption=caption) if type_ == "video" else
        InputMediaDocument(
            media=file, caption=caption) if type_ == "document" else None
        for file, caption, type_ in zip(files, captions, types)
    ]


async def handle_single_media(client: Client, message: Message) -> None:
    """
    Пересылает одиночные медиа-сообщения.
    """
    file = await client.download_media(message, in_memory=True)
    caption = await edit_text_caption(message.caption) if message.caption else ""

    if message.photo:
        await client.send_photo(recipient_chat, file, caption=caption)
    elif message.video:
        await client.send_video(recipient_chat, file, caption=caption)
    elif message.document:
        await client.send_document(recipient_chat, file, caption=caption)
    logging.info("End")


@app.on_message(filters.chat(donor_chat))
async def handle_message(client: Client, message: Message) -> None:
    """
    Основной обработчик сообщений.
    """
    try:
        logging.info(f"Сообщение из чата {message.chat.id}: {message.chat.title or ''}")

        # работаем с альбомом
        if message.media_group_id:
            if message.media_group_id in processed_media_groups:
                return

            processed_media_groups.add(message.media_group_id)
            media_group = await client.get_media_group(message.chat.id, message.id)
            media_to_send = await download_and_prepare_media(client, media_group)
            # Отправляем Альбом
            await client.send_media_group(recipient_chat, media_to_send)
            logging.info("End")

        # работает с одним носителем
        elif message.media in [
            MessageMediaType.PHOTO,
            MessageMediaType.VIDEO,
            MessageMediaType.DOCUMENT
        ] and message.media_group_id is None:
            await handle_single_media(client, message)

        # работаем с одиночным текстом или ссылкой на что то.
        elif message.text or message.media == MessageMediaType.WEB_PAGE and message.media_group_id is None:
            text = await edit_text_caption(message.text) if message.text else ""
            link = message.web_page.url if message.web_page else ""
            await client.send_message(recipient_chat, f"{text}{link}")
            logging.info("End")
    except Exception as e:
        logging.error(f"Error Start: {str(e)}")



if __name__ == "__main__":
    app.run()
