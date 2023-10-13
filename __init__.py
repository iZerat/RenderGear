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
0

import bpy
import os
from bpy.props import EnumProperty, BoolProperty, StringProperty, IntProperty, FloatProperty, PointerProperty


class MyItem(bpy.types.PropertyGroup):
    name:bpy.props.StringProperty(name = "name", default = "")
    data:bpy.props.StringProperty(name = "name", default = "")



# 定义属性类
def My_Properties():

    # list 数据
    bpy.types.Scene.myList = bpy.props.CollectionProperty(type = MyItem)

    # 当前选中的下标
    bpy.types.Scene.active_index = bpy.props.IntProperty(name = "current index", default = 0, min = 0)




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
    bl_idname = 'iz.rendering_gear_ui'
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
        row2.operator("iz.rendering_gear1", text='开始渲染', icon='DRIVER')

        


# 执行操作1
class RenderingGear_OT_Operator1(bpy.types.Operator):
    bl_idname = 'iz.rendering_gear1'
    bl_label = 'RenderingGearOperator1'

    # 执行的内容
    def execute(self, context):         
        command = cmd_Run()
        os.system(command) # 给终端打命令
        return {'FINISHED'}






# 创建队列
class RenderingGear_OT_CreateItem(bpy.types.Operator):
    bl_idname = 'iz.rendering_createitem'
    bl_label = 'RenderingGearCreateItem'

    @classmethod
    def poll(cls, context):
        return True


    # 执行的内容
    def execute(self, context):         

        return {'FINISHED'}

# 删除队列
class RenderingGear_OT_DeleteItem(bpy.types.Operator):
    bl_idname = 'iz.rendering_deleteitem'
    bl_label = 'RenderingGearDeleteItem'

    @classmethod
    def poll(cls, context):
        return True
    
    # 执行的内容
    def execute(self, context):         

        return {'FINISHED'}

# 移动队列
class RenderingGear_OT_MoveItem(bpy.types.Operator):
    bl_idname = 'iz.rendering_moveitem'
    bl_label = 'RenderingGearMoveItem'

    @classmethod
    def poll(cls, context):
        return True
    
    # 执行的内容
    def execute(self, context):         

        return {'FINISHED'}

# 自定义uilist
class RenderingGear_UL_Queue(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon_value, active_data, active_propname, index):

        icon = "BLENDER"

        # 三种显示模式: 'DEFAULT', 'COMPACT', 'GRID'
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text = "", translate = False, icon = icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text = "", icon = icon)

        pass

# 显示队列
class RenderingGear_PT_Queue(bpy.types.Panel):
    bl_idname = 'iz.rendering_queue'
    bl_label = 'RenderingGearQueue'

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'UIList'

    def draw(self, context):
        layout = self.layout

        scene = context.scene

        row1 = layout.row()

        row1.template_list("RenderingGear_UL_Queue", "test list", scene, "myList", scene, "active_index")
        pass




# 注册与注销

classes = [
    MyItem,
    RenderingGear_OperatorUI,
    RenderingGear_OT_Operator1,
    RenderingGear_OT_CreateItem,
    RenderingGear_OT_MoveItem,
    RenderingGear_UL_Queue,
    RenderingGear_PT_Queue
]
def register():
    for item in classes:
        bpy.utils.register_class(item) 

    # 注册属性
    My_Properties()

    print("register complex")


def unregister():
    for item in classes:
        bpy.utils.unregister_class(item)    

    print("see you")




