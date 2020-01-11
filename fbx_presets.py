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


from os import path
from pathlib import Path

import bpy


def fbx_export(directory, file_name, export_preset, export_format, use_collection):
    filepath = Path(directory) / (file_name + "." + export_format)

    if filepath:
        class Container(object):
            __slots__ = ('__dict__',)

        op = Container()
        dir = Path(__file__).parent.absolute()
        preset_path = dir / "presets" / export_format / (export_preset + ".py")
        file = open(preset_path, 'r')

        # storing the values from the preset on the class
        for line in file.readlines()[3::]:
            exec(line, globals(), locals())

        # change preset parameters
        op.filepath = filepath.as_posix()
        op.use_active_collection = use_collection
        # pass class dictionary to the operator
        kwargs = op.__dict__

        if export_format == "fbx":
            bpy.ops.export_scene.fbx(**kwargs)
        if export_format == "obj":
            bpy.ops.export_scene.obj(**kwargs)

    return "True"
    # export_mode = bpy.context.window_manager.FBXGEE_export_mode
    # use_collection = True if export_mode == 'COLLECTION' else False
    # selection = not use_collection

    # if engine == "UNITY":
    #     # UNITY Static Mesh
    #     if export_type == "STATIC":
    #         bpy.ops.export_scene.fbx(
    #             filepath=export_path,
    #             use_selection=selection,
    #             use_active_collection=use_collection,
    #             apply_scale_options='FBX_SCALE_ALL',
    #             bake_space_transform=True,
    #             object_types={'MESH', 'OTHER'},
    #             bake_anim=False)

    #         return "Export Finished"
    #     # UNITY Skeletal Mesh
    #     elif export_type == "SKELETAL":
    #         return "Not supported yet"
    #     elif export_type == "ANIMATION":
    #         return "Not supported yet"
    # elif engine == "UE4":
    #     # UE4 Static Mesh
    #     if export_type == "STATIC":
    #         bpy.ops.export_scene.fbx(
    #             filepath=export_path,
    #             use_selection=selection,
    #             use_active_collection=use_collection,
    #             axis_up='Z',
    #             object_types={'MESH', 'OTHER'},
    #             mesh_smooth_type='FACE',
    #             bake_anim=False)

    #         return "Export Finished"
    #     # UE4 Skeletal Mesh
    #     elif export_type == "SKELETAL":
    #         bpy.ops.export_scene.fbx(
    #             filepath=export_path,
    #             use_selection=selection,
    #             use_active_collection=use_collection,
    #             axis_up='Z',
    #             object_types={'ARMATURE', 'MESH', 'OTHER'},
    #             mesh_smooth_type='FACE',
    #             add_leaf_bones=False,
    #             bake_anim=False)

    #         return "Export Finished"
    #     # UE4 Animation
    #     elif export_type == "ANIMATION":
    #         bpy.ops.export_scene.fbx(
    #             filepath=export_path,
    #             use_selection=selection,
    #             axis_up='Z',
    #             object_types={'ARMATURE', 'MESH', 'OTHER'},
    #             mesh_smooth_type='FACE',
    #             add_leaf_bones=False,
    #             bake_anim_simplify_factor=0)

    #         return "Export Finished"
    # elif engine == "MAYA":
    #     # MAYA Static Mesh
    #     if export_type == "STATIC":
    #         bpy.ops.export_scene.fbx(
    #             filepath=export_path,
    #             use_selection=selection,
    #             use_active_collection=use_collection,
    #             object_types={'MESH', 'OTHER'},
    #             bake_anim=False)

    #         return "Export Finished"
    #     # MAYA Skeletal Mesh
    #     elif export_type == "SKELETAL":
    #         return "Not supported yet"
    #     elif export_type == "ANIMATION":
    #         return "Not supported yet"
