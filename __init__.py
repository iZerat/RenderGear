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
from bpy.props import EnumProperty, BoolProperty, StringProperty, IntProperty, FloatProperty, PointerProperty

# 定义属性类
class My_Properties(bpy.types.PropertyGroup):

    blbl_int1: bpy.props.IntProperty(name = "blbl_int1",soft_min = 0)

    blbl_myBool_poweroff: bpy.props.BoolProperty(name = "myBool_poweroff")



def cmd_Run():

    # 当前 blender 工程文件的路径
    file_pathA = bpy.data.filepath
    file_pathB = file_pathA.replace("\\", "\\\\")

    # 导出路径
    export_pathA = bpy.data.scenes["Scene"].render.filepath
    export_pathB = export_pathA.replace("\\","\\\\")

    # 存放命令  
    orders =[
        "start blender -b",
        file_pathB,
        "-E",
        "BLENDER_EEVEE",
        "-o",
    ]

    # 输入导出路径
    orders.append(export_pathB)

    # 渲染以上所有
    orders.append('-a')

    # 将列表转换成用于命令的字符串
    return ' '.join(orders)



# 侧边栏
class RenderingGear_OperatorUI(bpy.types.Panel):
    bl_idname = 'wm.rendering_gear_ui'
    bl_label = '后台自动渲染'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = '（ : '

    def draw(self, context):
        
        layout = self.layout
        row1 = layout.row()
        row1.label(text='*** 这是个标签 *** ')
        
        # 按钮
        row2 = layout.row()
        row2.operator("wm.rendering_gear", text='开始渲染', icon='DRIVER')

        row3 = layout.row()
        row3.prop(context.scene.my_properties,"myBool_poweroff", text="这是一个单选框")
        


# 执行操作
class RenderingGear_Operator(bpy.types.Operator):
    bl_idname = 'wm.rendering_gear'
    bl_label = 'RenderingGearOperator'

    # 执行的内容
    def execute(self, context):         
        command = cmd_Run()
        os.system(command) # 给终端打命令
        # os.system("shutdown -s -t 60")
        return {'FINISHED'}




# 注册与注销
def register():
    bpy.utils.register_class(My_Properties)
    bpy.utils.register_class(RenderingGear_Operator)
    bpy.utils.register_class(RenderingGear_OperatorUI)
    print("register complex")


def unregister():
    bpy.utils.unregister_class(My_Properties)
    bpy.utils.unregister_class(RenderingGear_Operator)
    bpy.utils.unregister_class(RenderingGear_OperatorUI)
    print("see you")

bpy.types.Scene.my_properties = bpy.props.PointerProperty(type = My_Properties)

