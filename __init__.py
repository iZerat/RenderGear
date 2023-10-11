bl_info = {
    "name" : "RenderingGear",
    "author" : "iZerat",
    "description" : "",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "",
    "warning" : "",
    "category" : "Render"
}


import bpy
import os
import subprocess
from bpy.props import EnumProperty, BoolProperty, StringProperty, IntProperty, FloatProperty

def cmd_Run(self, context):

    # 当前 blender 工程文件的路径
    file_path1 = bpy.data.filepath
    file_path2 = file_path1.replace("\\", "\\\\")

    # 导出路径
    export_path1 = bpy.data.scenes["Scene"].render.filepath
    export_path2 = export_path1.replace("\\","\\\\")
    engine = context.preferences.addons["cycles"].preferences.compute_device_type
      
    orders =[
        "start blender -b",
        "D:\\testRender\\testRender.blend",
        "-E",
        "BLENDER_EEVEE",
        "-o",
    ]

    # 输入导出路径
    command.append(export_path2)

    # 渲染以上所有
    command.append('-a')

    # 将列表转换成用于命令的字符串
    command = ' '.join(orders)

    os.system(command)








# 侧边栏
class RenderingGear_OperatorUI(bpy.types.Panel):
    bl_idname = 'wm.rendering_gear_ui'
    bl_label = '后台自动渲染'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = '（ : '

    def draw(self, context):
        layout = self.layout
 
        row = layout.row()
        row.label(text='*** 这是一个标签 *** ')
        
        # 按钮
        row1 = layout.row()
        row1.operator("wm.rendering_gear", text='开始渲染', icon='DRIVER')


# 执行操作
class RenderingGear_Operator(bpy.types.Operator):
    bl_idname = 'wm.rendering_gear'
    bl_label = 'RenderingGearOperator'

    # 执行的内容
    def execute(self, context):
        
        cmd_Run(self, context)
        # os.system("shutdown -s -t 60")
        return {'FINISHED'}



def register():
    bpy.utils.register_class(RenderingGear_Operator)
    bpy.utils.register_class(RenderingGear_OperatorUI)
    print("register complex")

def unregister():
    bpy.utils.unregister_class(RenderingGear_Operator)
    bpy.utils.unregister_class(RenderingGear_OperatorUI)
    print("see you")

