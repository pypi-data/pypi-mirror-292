import logging
from django.http import HttpRequest

from dnoticias_utils.templatetags.base import is_on

logger = logging.getLogger(__name__)
menu_items = []


def get_menu_items(request: HttpRequest) -> list:
    """Get the menu items. The menu items are registered using the register_menu_item function.

    :param request: The request object.
    :return: The menu items.
    :rtype: list
    """
    items = []

    for index, item in enumerate(menu_items):
        permissions = item.get("permissions", [])
        active = any([is_on(request, url_name) for url_name in item.get("active_url_names", [])])
        has_permissions = request.user.has_perms(permissions) if permissions else True

        items.append({
            "id": f"menu-item-{index}",
            "name": item.get("name"),
            "icon": item.get("icon"),
            "url_name": item.get("url_name"),
            "active": active,
            "has_permissions": has_permissions,
            "is_category": item.get("is_category"),
            "notification_url": item.get("notification_url"),
        })

    return items

def register_menu_item(
    name: str,
    icon: str = None,
    url_name: str = None,
    active_url_names: list = None,
    permissions: list = None,
    is_category: bool = False,
    notification_url: str = None,
):
    """Register a menu item appending it to the menu_items list.

    :parame name: The name of the menu item.
    :param icon: The icon of the menu item.
    :param url_name: The url name of the menu item.
    :param active_url_names: The url names that will be considered active.
    :param permissions: The permissions required to show the menu item.
    :param is_category: If the menu item is a category.
    :param notification_url: The url to get the notification count. The response must be a json 
     with a count key.
    :return: None
    """
    active_url_names = active_url_names or []
    menu_items.append({
        "name": name,
        "icon": icon,
        "url_name": url_name,
        "active_url_names": active_url_names,
        "permissions": permissions,
        "is_category": is_category,
        "notification_url": notification_url,
    })
