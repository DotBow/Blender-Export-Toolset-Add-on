import os
import bpy.utils.previews

icons = None
icons_dir = os.path.dirname(__file__)


def icon_get(name):
    if name not in icons:
        icons.load(name, os.path.join(icons_dir, name + ".png"), 'IMAGE')

    return icons[name].icon_id


def register_icons():
    global icons
    icons = bpy.utils.previews.new()


def unregister_icons():
    bpy.utils.previews.remove(icons)
