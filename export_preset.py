from pathlib import Path
import bpy


def export_fbx(preset_name):
    dir = Path(__file__).parent.absolute()
    preset_path = dir / "presets" / "fbx" / preset_name

    filename = preset_name
    print(filename)
    preset_path = "D:\\"
    print(preset_path)

    if preset_path:
        filepath = "D:\\test.py"

        if filepath:
            class Container(object):
                __slots__ = ('__dict__',)

            op = Container()
            file = open(filepath, 'r')

            # storing the values from the preset on the class
            for line in file.readlines()[3::]:
                exec(line, globals(), locals())

            # change preset parameters
            op.filepath = "D:\\test.obj"
            # pass class dictionary to the operator
            kwargs = op.__dict__
            bpy.ops.export_scene.obj(**kwargs)
        else:
            raise FileNotFoundError(filepath)


if __name__ == '__main__':
    export_fbx('pure_fbx')
