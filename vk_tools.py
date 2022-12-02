import re
from vkbottle_types.objects import *


def get_name_by_id(
    source_id: int, groups: GroupsGroupFull, users: UsersUserFull
) -> str:
    if source_id < 0:
        group = [i for i in groups if i.id == abs(source_id)][0]
        return group.name
    else:
        user = [i for i in users if i.id == source_id][0]
        return f"{user.first_name} {user.last_name}"


def fix_bad_vk_links(text: str):
    search_pattern = r"\[(?P<url_ending>[0-9a-z]{3,32})\|(?P<url_name>[^]|]*)\]"
    html_link_pattern = r'<a href="https://vk.com/\g<url_ending>">\g<url_name></a>'
    return re.sub(
        search_pattern,
        html_link_pattern,
        text,
    )


def get_post_url(source_id: int, post_id: int) -> str:
    return f"https://vk.com/wall{source_id}_{post_id}"
