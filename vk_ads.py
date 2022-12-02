import aiohttp
import base64


ads_label = (
    b"PGRpdiBjbGFzcz0icGlfc2lnbmVkIGFkc19"
    b"tYXJrIj4KICAgICAgPHNwYW4+PC9zcGFuPj"
    b"xpIGNsYXNzPSJpX2Fkc19tYXJrICI+PC9pP"
    b"tCg0LXQutC70LDQvNCwCiAgICA8L2Rpdj4="
)


async def is_ads(source_id: int, post_id: int) -> bool:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://m.vk.com/wall{source_id}_{post_id}"
        ) as response:
            return base64.b64decode(ads_label).decode() in await response.text()
