# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

from copy import copy, deepcopy
from math import pi
from os import path
from pathlib import Path

import bpy
from bpy.app.handlers import persistent
from bpy.props import (BoolProperty, EnumProperty, PointerProperty,
                       StringProperty)
from bpy.types import Panel, PropertyGroup
from bpy.utils import register_class, unregister_class

from .icons import *
from .operators import *

bl_info = {
    "name": "FBX Game Engine Export",
    "description": "FBX format export for Unity and Unreal Engine 4",
    "author": "Oleg Stepanov",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar",
    "warning": "",
    "wiki_url": "",
    "support": 'COMMUNITY',
    "category": "Import-Export"
}


class FBXGEE_PT_panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "FBX Game Export"
    bl_category = "FBX Game Export"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        wm = context.window_manager

        active_object = context.active_object
        selected_objects = context.selected_objects
        active_collection = context.collection

        if len(selected_objects) == 0:
            export_properties = active_collection.export_properties
            export_mode = "COLLECTION"
        elif active_collection:
            export_properties = active_object.export_properties
            export_mode = "OBJECT"

        box = layout.box()
        box.label(text="Export Preset:")
        col = box.column(align=True)
        col.row(align=True).prop(export_properties, "format", expand=True)
        col.prop(export_properties, "preset", text="")

        if not selected_objects and export_mode == 'OBJECT':
            layout.separator()
            layout.label(text="No Objects Selected", icon="ERROR")
            layout.separator()
            return

        settings_box = layout.box()
        settings_box.label(text="Settings:")
        settings_box_col = settings_box.column(align=True)
        settings_box_col.prop(scene, "FBXGEE_reset_pos")
        settings_box_col.prop(scene, "FBXGEE_reset_rot")

        # Active Export Directory
        box = layout.box()
        box.label(text="Export Folder:")
        col = box.column(align=True)

        dir_name = path.basename(path.normpath(
            export_properties.directory))

        if dir_name == '.':
            col.alert = True

        col.prop(export_properties, "directory", text="")

        if len(recent_folders) > 0:
            try:
                wm.FBXGEE_recent_folders = export_properties.directory
            except:
                pass

            row = col.row(align=True)
            row.prop(wm, "FBXGEE_recent_folders", text="")
            row.operator(FBXGEE_OT_sync_dir_path.bl_idname,
                         text="", icon='FILE_REFRESH')

        # Export Buttons
        col = layout.column()
        col.scale_y = 1.4

        if export_mode == 'OBJECT':
            col.operator(FBXGEE_OT_export_single.bl_idname, icon='EXPORT')
            col.operator(FBXGEE_OT_export_batch.bl_idname, icon='EXPORT')
            col.operator(
                FBXGEE_OT_export_linked_data.bl_idname, icon='EXPORT')
        elif export_mode == 'COLLECTION':
            col.operator(FBXGEE_OT_export_single.bl_idname, icon='EXPORT')

            # Show Active Collection
            box = layout.box()
            box.label(text="Collection to Export:")

            if not export_properties.directory:
                box.alert = True

            box.prop(active_collection, "name",
                     text="", icon='GROUP')

        # Show Selected Objects
        obj_box = layout.box()
        obj_box.label(text="Objects to Export:")
        obj_col = obj_box.column(align=True)

        if (export_mode == 'OBJECT' and active_object):
            for obj in selected_objects:
                obj_row = obj_col.row(align=True)
                type_icon = 'OUTLINER_OB_' + obj.type

                if not obj.export_properties.directory:
                    obj_row.alert = True

                obj_row.prop(obj, "name", text="", icon=type_icon)

                if obj.name == active_object.name:
                    obj_row.label(icon='LAYER_ACTIVE')
        elif export_mode == 'COLLECTION':
            for obj in active_collection.objects:
                obj_row = obj_col.row(align=True)
                type_icon = 'OUTLINER_OB_' + obj.type
                obj_row.prop(obj, "name", text="", icon=type_icon)


def get_recent_folders(self, context):
    return recent_folders


def update_recent_folder(self, context):
    obj_active = context.active_object
    active_collection = context.collection
    selected_objects = context.selected_objects

    if len(selected_objects) == 0:
        export_properties = active_collection.export_properties
    elif active_collection:
        export_properties = obj_active.export_properties

    wm = context.window_manager
    new_dir_path = wm.FBXGEE_recent_folders

    if export_properties.directory != new_dir_path:
        export_properties.directory = new_dir_path


recent_folders = []


classes = (
    FBXGEE_PT_panel,
    FBXGEE_OT_export_single,
    FBXGEE_OT_export_batch,
    FBXGEE_OT_sync_dir_path,
    FBXGEE_OT_export_linked_data,
)


@persistent
def collect_recent_folders(dummy):
    recent_folders.clear()
    objects = bpy.context.view_layer.objects
    collections = bpy.data.collections

    folders = []

    for obj in objects:
        dir_path = obj.export_properties.directory

        if dir_path:
            folders.append(dir_path)

    for collection in collections:
        dir_path = collection.export_properties.directory

        if dir_path:
            folders.append(dir_path)

    folders = list(set(folders))

    for dir_path in folders:
        dir_name = path.basename(path.normpath(dir_path))
        recent_folder = (dir_path, dir_name, '')
        recent_folders.append(recent_folder)

# NEW


class ExportProperties(PropertyGroup):
    def update_directory(self, context):
        dir_path = self["directory"]

        if dir_path:
            dir_name = path.basename(path.normpath(dir_path))
            recent_folder = (dir_path, dir_name, '')

            if recent_folder not in recent_folders:
                recent_folders.append(recent_folder)

            wm = context.window_manager

            if wm.FBXGEE_recent_folders != dir_path:
                wm.FBXGEE_recent_folders = dir_path

    def get_directory(self):
        try:
            return self["directory"]
        except:
            return ""

    def set_directory(self, value):
        self["directory"] = path.abspath(bpy.path.abspath(value))

    def get_export_presets(self, context):
        export_format = context.active_object.export_properties.format.lower()
        export_presets = []

        dir = Path(__file__).parent.absolute()
        preset_path = dir / "presets" / export_format
        paths = list(Path(preset_path).rglob('*.py'))

        for path in paths:
            p = Path(path)
            icon = icon_get('unity')
            export_presets.append((p.as_posix(), p.stem, "", icon))

        return export_presets

    export_formats = [
        ("FBX", "FBX", "", 1),
        ("OBJ", "OBJ", "", 2),
    ]

    format: EnumProperty(name="Export Format", items=export_formats)
    preset: EnumProperty(name="Export Preset", items=get_export_presets)
    directory = StringProperty(name="Export Path", default="", subtype='DIR_PATH',
                               update=update_directory, get=get_directory, set=set_directory)


# NEW

def register():
    register_icons()

# NEW
    bpy.utils.register_class(ExportProperties)
    bpy.types.Object.export_properties = PointerProperty(type=ExportProperties)
    bpy.types.Collection.export_properties = PointerProperty(
        type=ExportProperties)
# NEW

    bpy.types.WindowManager.FBXGEE_recent_folders = EnumProperty(
        name="Recent Folders",
        items=get_recent_folders,
        update=update_recent_folder)

    bpy.types.Scene.FBXGEE_reset_pos = BoolProperty(
        name="Reset Position", description="Set object position to (0, 0, 0)", default=False)

    bpy.types.Scene.FBXGEE_reset_rot = BoolProperty(
        name="Reset Rotation", description="Set object rotation to (0, 0, 0)", default=False)

    for cls in classes:
        register_class(cls)

    bpy.app.handlers.load_post.append(collect_recent_folders)


def unregister():
    for cls in classes:
        unregister_class(cls)

    bpy.app.handlers.load_post.remove(collect_recent_folders)
    unregister_icons()


if __name__ == "__main__":
    register()
