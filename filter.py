import html
import vk_tools
from vkbottle_types.objects import *


def filter_photos(attachments: WallWallpostAttachment) -> list:
    if not attachments:
        return None

    urls = list()
    for attachment in attachments:
        if attachment.type != WallWallpostAttachmentType.PHOTO:
            continue
        max_sized_photo = max(attachment.photo.sizes, key=lambda x: x.width * x.height)
        urls.append(max_sized_photo.url)

    return urls


def filter_other_media(attachments: WallWallpostAttachment) -> dict:
    other_media = dict()

    if attachments:
        for attachment in attachments:
            if (
                attachment.type == WallWallpostAttachmentType.PHOTO
                or attachment.type == WallWallpostAttachmentType.LINK
            ):
                continue
            if attachment.type not in other_media:
                other_media[attachment.type.value] = 0
            other_media[attachment.type.value] += 1
    return other_media


def filter_original_author_name(
    copy_history: WallWallpostFull, groups: GroupsGroupFull, users: UsersUserFull
) -> str:
    return (
        html.escape(vk_tools.get_name_by_id(copy_history[0].from_id, groups, users))
        if copy_history
        else None
    )


def filter_original_post_url(copy_history: WallWallpostFull) -> str:
    return (
        vk_tools.get_post_url(copy_history[0].from_id, copy_history[0].id)
        if copy_history
        else None
    )


def filter_post_data(
    item: NewsfeedNewsfeedItem, groups: GroupsGroupFull, users: UsersUserFull
) -> tuple:

    author_name = html.escape(vk_tools.get_name_by_id(item.source_id, groups, users))

    post_text = vk_tools.fix_bad_vk_links(html.escape(item.text))
    photo_urls = filter_photos(item.attachments)
    post_url = vk_tools.get_post_url(source_id=item.source_id, post_id=item.post_id)

    original_author_name = filter_original_author_name(item.copy_history, groups, users)

    original_post_url = filter_original_post_url(item.copy_history)

    other_media = filter_other_media(item.attachments)

    return (
        author_name,
        post_url,
        post_text,
        photo_urls,
        item.source_id,
        item.post_id,
        other_media,
        original_post_url,
        original_author_name,
    )
