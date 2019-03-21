import bpy
import bpy.utils.previews
import os


preview_icons = bpy.utils.previews.new()
icons_dir = os.path.dirname(__file__)


def icon_get(name):
    return preview_icons[name].icon_id


def icon_register(name):
    preview_icons.load(name, os.path.join(icons_dir, name + ".png"), 'IMAGE')


icons = [
    "unity",
    "ue4"
]

for icon in icons:
    icon_register(icon)
