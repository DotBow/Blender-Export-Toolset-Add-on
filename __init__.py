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

import bpy
from bpy.app.handlers import persistent
from bpy.props import BoolProperty, EnumProperty, StringProperty
from bpy.types import Operator, Panel
from bpy.utils import register_classes_factory

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

        layout.prop(scene, "FBXGEE_engine", text="")

        export_mode_box = layout.box()
        export_mode_box.label(text="Export Mode:")
        export_mode_box.row().prop(wm, "FBXGEE_export_mode", expand=True)

        if not selected_objects and export_mode == 'OBJECT':
            layout.separator()
            layout.label(text="No Objects Selected", icon="ERROR")
            layout.separator()
            return

        # Active Export Directory
        export_dir_box = layout.box()
        export_dir_box.label(text="Export Folder:")
        export_dir_col = export_dir_box.column(align=True)

        if export_mode == 'OBJECT':
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
                                        text="Export Single Static",
                                        icon='EXPORT').export_type = 'STATIC'
            export_buttons_col.operator(FBXGEE_OT_export_single.bl_idname,
                                        text="Export Single Skeletal",
                                        icon='EXPORT').export_type = 'SKELETAL'
            export_buttons_col.separator()
            export_buttons_col.operator(FBXGEE_OT_export_batch.bl_idname,
                                        text="Export Batch Static",
                                        icon='EXPORT').export_type = 'STATIC'
            export_buttons_col.operator(FBXGEE_OT_export_batch.bl_idname,
                                        text="Export Batch Skeletal",
                                        icon='EXPORT').export_type = 'SKELETAL'
            export_buttons_col.separator()
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

        if export_mode == 'OBJECT':
            for obj in selected_objects:
                obj_row = obj_col.row(align=True)
                type_icon = 'OUTLINER_OB_' + obj.type

                if not obj.FBXGEE_dir_path:
                    obj_row.alert = True

                obj_row.prop(obj, "name", text="", icon=type_icon)
        elif export_mode == 'COLLECTION':
            for obj in active_collection.objects:
                obj_row = obj_col.row(align=True)
                type_icon = 'OUTLINER_OB_' + obj.type
                obj_row.prop(obj, "name", text="", icon=type_icon)


class FBXGEE_OT_export_single(bpy.types.Operator):
    """Export selected objects in a single file"""
    bl_idname = "object.fbxgee_ot_single_export"
    bl_label = "Export Single"

    export_type_items = [
        ("STATIC", "Static Mesh", "", 1),
        ("SKELETAL", "Skeletal Mesh", "", 2),
    ]

    export_type: EnumProperty(items=export_type_items)

    @classmethod
    def poll(cls, context):
        if context.window_manager.FBXGEE_export_mode == 'OBJECT':
            return (len(context.selected_objects) > 0 and
                    context.active_object.FBXGEE_dir_path != "")
        else:
            return context.collection.FBXGEE_dir_path != ""

    def execute(self, context):
        engine = context.scene.FBXGEE_engine
        active_object = context.active_object
        export_mode = context.window_manager.FBXGEE_export_mode

        file_name = active_object.name if export_mode == 'OBJECT' else context.collection.name
        dir_path = active_object.FBXGEE_dir_path if export_mode == 'OBJECT' else context.collection.FBXGEE_dir_path

        result = fbx_export(
            engine, self.export_type, dir_path, file_name)

        self.report({'INFO'}, result)
        return {'FINISHED'}


class FBXGEE_OT_export_batch(bpy.types.Operator):
    """Export each selected object in a separate file"""
    bl_idname = "object.fbxgee_ot_export_batch"
    bl_label = "Export Batch"

    export_type_items = [
        ("STATIC", "Static Mesh", "", 1),
        ("SKELETAL", "Skeletal Mesh", "", 2),
    ]

    export_type: EnumProperty(items=export_type_items)

    @classmethod
    def poll(cls, context):
        selected_objects = context.selected_objects

        if (len(selected_objects) > 1):
            for obj in selected_objects:
                if obj.FBXGEE_dir_path == "":
                    return False

            return True

        return False

    def execute(self, context):
        selected_objects = context.selected_objects
        engine = context.scene.FBXGEE_engine

        for obj in selected_objects:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            dir_path = obj.FBXGEE_dir_path

            result = fbx_export(
                engine, self.export_type, dir_path, obj.name)

            self.report({'INFO'}, result)

        for obj in selected_objects:
            obj.select_set(True)

        return {'FINISHED'}


class FBXGEE_OT_sync_dir_path(bpy.types.Operator):
    """Set active directory to each selected object"""
    bl_idname = "object.fbxgee_ot_sync_dir_path"
    bl_label = "Synchronize Directories"

    @classmethod
    def poll(cls, context):
        return (len(context.selected_objects) > 1 and
                context.active_object.FBXGEE_dir_path)

    def execute(self, context):
        active_object = context.active_object

        if active_object.FBXGEE_dir_path:
            for obj in context.selected_objects:
                obj.FBXGEE_dir_path = active_object.FBXGEE_dir_path

        return {'FINISHED'}


class FBXGEE_OT_export_linked_data(bpy.types.Operator):
    """ Export transformation data for each linked object into text file """
    bl_idname = "object.fbxgee_ot_export_linked_data"
    bl_label = "Export Linked Data"

    @classmethod
    def poll(cls, context):
        return (context.active_object.FBXGEE_dir_path and
                len(context.selected_objects) > 0)

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_linked(type='OBDATA')

        active_object = context.active_object
        path = active_object.FBXGEE_dir_path

        # Clear file
        open(path + active_object.name + ".txt", 'w').close()

        for obj in context.selected_objects:
            loc = obj.location
            rot = obj.rotation_euler

            with open(path + active_object.name + ".txt", 'a') as file:
                file.write("{0:.2f} {1:.2f} {2:.2f} {3:.2f} {4:.2f} {5:.2f}\n"
                           .format(loc.x, loc.y, loc.z, rot.x, rot.y, rot.z))

        return {'FINISHED'}


def fbx_export(engine, export_type, dir_path, file_name):
    export_path = path.join(dir_path, file_name) + ".fbx"
    export_mode = bpy.context.window_manager.FBXGEE_export_mode
    use_collection = True if export_mode == 'COLLECTION' else False
    selection = not use_collection

    if engine == "UNITY":
        # UNITY Static Mesh
        if export_type == "STATIC":
            bpy.ops.export_scene.fbx(
                filepath=export_path,
                use_selection=selection,
                use_active_collection=use_collection,
                apply_scale_options='FBX_SCALE_ALL',
                bake_space_transform=True,
                object_types={'MESH', 'OTHER'},
                bake_anim=False)

            return "Export Finished"
        # UNITY Skeletal Mesh
        elif export_type == "SKELETAL":
            # bpy.ops.export_scene.fbx(
            #     filepath=export_path,)

            return "Not supported yet"
    elif engine == "UE4":
        # UE4 Static Mesh
        if export_type == "STATIC":
            bpy.ops.export_scene.fbx(
                filepath=export_path,
                use_selection=selection,
                use_active_collection=use_collection,
                axis_up='Z',
                object_types={'MESH', 'OTHER'},
                mesh_smooth_type='FACE',
                bake_anim=False)

            return "Export Finished"
        # UE4 Skeletal Mesh
        elif export_type == "SKELETAL":
            bpy.ops.export_scene.fbx(
                filepath=export_path,
                use_selection=selection,
                use_active_collection=use_collection,
                axis_up='Z',
                object_types={'ARMATURE', 'MESH', 'OTHER'},
                mesh_smooth_type='FACE',
                add_leaf_bones=False,
                bake_anim=False)

            return "Export Finished"


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


engines = [
    ("UNITY", "Unity", "", 1),
    ("UE4", "Unreal Engine 4", "", 2),
]


export_modes = [
    ("OBJECT", "Object", "", 1),
    ("COLLECTION", "Collection", "", 2),
]


recent_folders = []


bpy.types.Scene.FBXGEE_engine = EnumProperty(
    name="Game Engine", items=engines)
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


classes = (
    FBXGEE_PT_panel,
    FBXGEE_OT_export_single,
    FBXGEE_OT_export_batch,
    FBXGEE_OT_sync_dir_path,
    FBXGEE_OT_export_linked_data,
)

register, unregister = register_classes_factory(classes)


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


bpy.app.handlers.load_post.append(collect_recent_folders)


if __name__ == "__main__":
    register()
