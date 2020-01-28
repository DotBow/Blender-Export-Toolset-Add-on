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


def export_scene(directory, file_name, export_preset, export_format):
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
        op.use_selection = True

        if export_format == "fbx":
            op.use_active_collection = False
            kwargs = op.__dict__
            bpy.ops.export_scene.fbx(**kwargs)
        if export_format == "obj":
            kwargs = op.__dict__
            bpy.ops.export_scene.obj(**kwargs)

    return "Export Finished"
