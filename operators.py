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


import bpy
from bpy.props import EnumProperty
from bpy.types import Operator
from fbx_presets import fbx_export


class FBXGEE_OT_export_single(Operator):
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


class FBXGEE_OT_export_batch(Operator):
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


class FBXGEE_OT_sync_dir_path(Operator):
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


class FBXGEE_OT_export_linked_data(Operator):
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
