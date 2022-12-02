import filter
import vk_ads
from vkbottle import API
import logging
import datetime
import config
from aiogram import Bot, Dispatcher, executor, types
import asyncio
import yaml
from aiogram.types.input_media import InputMediaPhoto
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


logging.getLogger("aiogram").setLevel(logging.INFO)
logging.getLogger("vkbottle").setLevel(logging.INFO)

VK_USER_TOKEN = config.VK_USER_TOKEN

TELEGRAM_BOT_TOKEN = config.TELEGRAM_BOT_TOKEN
TELEGRAM_API_ID = config.TELEGRAM_API_ID
TELEGRAM_API_HASH = config.TELEGRAM_API_HASH
TELEGRAM_USER_ID = config.TELEGRAM_USER_ID


def save_last_post_unixtime(last_post_unixtime: int):
    with open("db.yaml", "w") as f:
        f.write(f"last_post_unixtime: {last_post_unixtime}")


def load_last_post_unixtime() -> int:
    try:
        with open("db.yaml") as f:
            return int(yaml.safe_load(f.read())["last_post_unixtime"])
    except FileNotFoundError:
        save_last_post_unixtime(0)
        return 0


def build_telegram_post_text(
    author_name: str,
    post_text: str,
    post_url: str,
    other_media: list,
    original_post_url: str,
    original_author_name: str,
) -> str:

    header = (
        f'<a href="{post_url}">{author_name}</a> reposted <a href="{original_post_url}">{original_author_name}</a>'
        if original_post_url
        else f'<a href="{post_url}">{author_name}</a>'
    )

    also = (
        (
            "This post also contains "
            + ", ".join([f"{other_media[key]} {key}" for key in other_media])
        )
        if other_media
        else None
    )

    return f"{header}\n\n" + f"{post_text}" + (f"\n\n<i>{also}</i>" if also else "")


bot = Bot(token=TELEGRAM_BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

vk_api = API(token=VK_USER_TOKEN)

last_post_unixtime = load_last_post_unixtime()
last_vk_api_request_time = datetime.datetime.fromtimestamp(0)

lock = asyncio.Lock()


def get_keyboard(url: str, original_url: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard = keyboard.add(InlineKeyboardButton(f"Post in VK", url=url))

    if original_url:
        keyboard = keyboard.add(
            InlineKeyboardButton(f"Original post in VK", url=original_url)
        )
    return keyboard


@dp.message_handler(commands="update")
async def echo(message: types.Message):
    global last_vk_api_request_time
    global last_post_unixtime

    async with lock:
        if (datetime.datetime.now() - last_vk_api_request_time).total_seconds() < 5:
            return
        last_vk_api_request_time = datetime.datetime.now()

        newsfeed = await vk_api.newsfeed.get(
            filters="post", start_time=last_post_unixtime
        )
        last_post_unixtime = (
            newsfeed.items[0].date + 1 if newsfeed.items else last_post_unixtime
        )
        save_last_post_unixtime(last_post_unixtime)

    for item in reversed(newsfeed.items):
        (
            author_name,
            post_url,
            post_text,
            photo_urls,
            source_id,
            post_id,
            other_media,
            original_post_url,
            original_author_name,
        ) = filter.filter_post_data(item, newsfeed.groups, newsfeed.profiles)

        if await vk_ads.is_ads(source_id=source_id, post_id=post_id):
            continue

        if photo_urls:
            await message.answer_media_group(
                media=[InputMediaPhoto(url) for url in photo_urls],
            )

        telegram_post_text = build_telegram_post_text(
            author_name,
            post_text,
            post_url,
            other_media,
            original_post_url,
            original_author_name,
        )

        await message.answer(
            text=telegram_post_text,
            disable_web_page_preview=True,
            reply_markup=get_keyboard(post_url, original_post_url),
        )


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
