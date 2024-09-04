from django import template
from menu.models import MenuItem
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(takes_context=True)
def draw_menu(context, menu_name):
    request = context['request']
    current_path = request.path

    menu_items = MenuItem.objects.filter(menu_name=menu_name).select_related('parent')
    menu_tree = build_menu_tree(menu_items)

    if not menu_items:
        return {'empty': True, 'html': ''}

    rendered_menu = render_menu(menu_tree, current_path)
    return {'empty': False, 'html': mark_safe(rendered_menu)}


def build_menu_tree(menu_items):
    menu_tree = {}
    for item in menu_items:
        if item.parent is None:
            menu_tree[item] = []
        else:
            if item.parent not in menu_tree:
                menu_tree[item.parent] = []
            menu_tree[item.parent].append(item)
    return menu_tree


def render_menu(menu_tree, current_path, parent=None, level=0):
    html = ''
    if parent is None:
        items = [item for item in menu_tree.keys() if item.parent is None]
    else:
        items = menu_tree.get(parent, [])

    for item in items:
        sub_menu = render_menu(menu_tree, current_path, parent=item, level=level + 1)
        is_active = item.get_absolute_url() == current_path or sub_menu
        html += f'<li{" class=\"active\"" if is_active else ""}><a href="{item.get_absolute_url()}">{item.title}</a>'
        if sub_menu:
            html += f'<ul>{sub_menu}</ul>'
        html += '</li>'

    return html
