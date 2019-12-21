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

from pathlib import Path
from copy import copy, deepcopy
from math import pi
from os import path

import bpy
from bpy.app.handlers import persistent
from bpy.props import BoolProperty, EnumProperty, StringProperty
from bpy.types import Panel
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
        export_mode = wm.FBXGEE_export_mode

        active_object = context.active_object
        selected_objects = context.selected_objects
        active_collection = context.collection

        layout.row().prop(active_object, "FBXGEE_export_format", expand=True)
        layout.prop(active_object, "FBXGEE_export_preset", text="")

        layout.prop(scene, "FBXGEE_engine", text="")

        export_mode_box = layout.box()
        export_mode_box.label(text="Export Mode:")
        export_mode_box.row().prop(wm, "FBXGEE_export_mode", expand=True)

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
        export_dir_box = layout.box()
        export_dir_box.label(text="Export Folder:")
        export_dir_col = export_dir_box.column(align=True)

        if (export_mode == 'OBJECT' and active_object):
            dir_name = path.basename(
                path.normpath(active_object.FBXGEE_dir_path))

            if dir_name == '.':
                export_dir_col.alert = True

            export_dir_col.prop(active_object, "FBXGEE_dir_path", text="")
        elif export_mode == 'COLLECTION':
            dir_name = path.basename(path.normpath(
                active_collection.FBXGEE_dir_path))

            if dir_name == '.':
                export_dir_col.alert = True

            export_dir_col.prop(active_collection, "FBXGEE_dir_path", text="")

        if len(recent_folders) > 0:
            try:
                if export_mode == 'OBJECT':
                    wm.FBXGEE_recent_folders = active_object.FBXGEE_dir_path
                elif export_mode == 'COLLECTION':
                    wm.FBXGEE_recent_folders = active_collection.FBXGEE_dir_path
            except:
                pass

            export_dir_row = export_dir_col.row(align=True)
            export_dir_row.prop(wm, "FBXGEE_recent_folders", text="")
            export_dir_row.operator(
                FBXGEE_OT_sync_dir_path.bl_idname, text="", icon='FILE_REFRESH')

        # Export Buttons
        export_buttons_col = layout.column(align=True)
        export_buttons_col.scale_y = 1.4

        if export_mode == 'OBJECT':
            export_buttons_col.operator(FBXGEE_OT_export_single.bl_idname,
                                        icon='EXPORT').export_type = 'STATIC'
            export_buttons_col.separator()
            export_buttons_col.operator(FBXGEE_OT_export_batch.bl_idname,
                                        icon='EXPORT').export_type = 'STATIC'
            export_buttons_col.operator(
                FBXGEE_OT_export_linked_data.bl_idname, icon='EXPORT')
        elif export_mode == 'COLLECTION':
            export_buttons_col.operator(FBXGEE_OT_export_single.bl_idname,
                                        text="Export Single Static",
                                        icon='EXPORT').export_type = 'STATIC'
            export_buttons_col.operator(FBXGEE_OT_export_single.bl_idname,
                                        text="Export Single Skeletal",
                                        icon='EXPORT').export_type = 'SKELETAL'

            # Show Active Collection
            collection_box = layout.box()
            collection_box.label(text="Collection to Export:")

            if not active_collection.FBXGEE_dir_path:
                collection_box.alert = True

            collection_box.prop(active_collection, "name",
                                text="", icon='GROUP')

        # Show Selected Objects
        obj_box = layout.box()
        obj_box.label(text="Objects to Export:")
        obj_col = obj_box.column(align=True)

        if (export_mode == 'OBJECT' and active_object):
            for obj in selected_objects:
                obj_row = obj_col.row(align=True)
                type_icon = 'OUTLINER_OB_' + obj.type

                if not obj.FBXGEE_dir_path:
                    obj_row.alert = True

                obj_row.prop(obj, "name", text="", icon=type_icon)

                if obj.name == active_object.name:
                    obj_row.label(icon='LAYER_ACTIVE')
        elif export_mode == 'COLLECTION':
            for obj in active_collection.objects:
                obj_row = obj_col.row(align=True)
                type_icon = 'OUTLINER_OB_' + obj.type
                obj_row.prop(obj, "name", text="", icon=type_icon)


def update_dir_path(self, context):
    dir_path = self["FBXGEE_dir_path"]

    if dir_path:
        dir_name = path.basename(path.normpath(dir_path))
        recent_folder = (dir_path, dir_name, '')

        if recent_folder not in recent_folders:
            recent_folders.append(recent_folder)

        wm = context.window_manager

        if wm.FBXGEE_recent_folders != dir_path:
            wm.FBXGEE_recent_folders = dir_path


def get_dir_path(self):
    try:
        return self["FBXGEE_dir_path"]
    except:
        return ""


def set_dir_path(self, value):
    self["FBXGEE_dir_path"] = path.abspath(bpy.path.abspath(value))


def get_recent_folders(self, context):
    return recent_folders


def update_recent_folder(self, context):
    obj_active = context.active_object
    active_collection = context.collection

    export_mode = context.window_manager.FBXGEE_export_mode

    if (obj_active and export_mode == 'OBJECT'):
        wm = context.window_manager
        new_dir_path = wm.FBXGEE_recent_folders

        if obj_active.FBXGEE_dir_path != new_dir_path:
            obj_active.FBXGEE_dir_path = new_dir_path
    elif (active_collection and export_mode == 'COLLECTION'):
        wm = context.window_manager
        new_dir_path = wm.FBXGEE_recent_folders

        if active_collection.FBXGEE_dir_path != new_dir_path:
            active_collection.FBXGEE_dir_path = new_dir_path


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
        dir_path = obj.FBXGEE_dir_path

        if dir_path:
            folders.append(dir_path)

    for collection in collections:
        dir_path = collection.FBXGEE_dir_path

        if dir_path:
            folders.append(dir_path)

    folders = list(set(folders))

    for dir_path in folders:
        dir_name = path.basename(path.normpath(dir_path))
        recent_folder = (dir_path, dir_name, '')
        recent_folders.append(recent_folder)

# NEW
def get_export_presets(self, context):
    export_format = context.active_object.FBXGEE_export_format.lower()
    export_presets = []

    dir = Path(__file__).parent.absolute()
    preset_path = dir / "presets" / export_format
    paths = list(Path(preset_path).rglob('*.py'))

    for path in paths:
        p = Path(path)
        icon = icon_get('unity')
        export_presets.append((p.as_posix(), p.stem, "", icon))

    return export_presets
# NEW

def register():
    register_icons()

    engines = [
        ("UNITY", "Unity", "", icon_get('unity'), 1),
        ("UE4", "Unreal Engine 4", "", icon_get('ue4'), 2),
        ("MAYA", "Maya", "", icon_get('maya'), 3),
    ]

    bpy.types.Scene.FBXGEE_engine = EnumProperty(
        name="Game Engine", items=engines)

    export_modes = [
        ("OBJECT", "Object", "", 1),
        ("COLLECTION", "Collection", "", 2),
    ]

# NEW
    export_formats = [
        ("FBX", "FBX", "", 1),
        ("OBJ", "OBJ", "", 2),
    ]

    bpy.types.Object.FBXGEE_export_format = EnumProperty(
        name="Export Format", items=export_formats)

    bpy.types.Object.FBXGEE_export_preset = EnumProperty(
        name="Export Preset", items=get_export_presets)
# NEW

    bpy.types.WindowManager.FBXGEE_export_mode = EnumProperty(
        name="Export Mode", items=export_modes)
    bpy.types.WindowManager.FBXGEE_recent_folders = EnumProperty(
        name="Recent Folders",
        items=get_recent_folders,
        update=update_recent_folder)
    bpy.types.Object.FBXGEE_dir_path = StringProperty(
        name="Export Directory",
        default="",
        subtype='DIR_PATH',
        update=update_dir_path,
        get=get_dir_path, set=set_dir_path)
    bpy.types.Collection.FBXGEE_dir_path = StringProperty(
        name="Collection Export Directory",
        default="",
        subtype='DIR_PATH',
        update=update_dir_path,
        get=get_dir_path, set=set_dir_path)

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
