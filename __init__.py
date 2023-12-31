bl_info = {
    "name" : "RenderGear",
    "author" : "iZerat",
    "description" : "Background multi queue automatic rendering plugin",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "",
    "warning" : "",
    "doc_url" : "https://github.com/iZerat/RenderGear",
    "category" : "Render"
}

import bpy
import os
import time
import subprocess
import threading
from bpy.props import EnumProperty, BoolProperty, StringProperty, IntProperty, FloatProperty, PointerProperty, CollectionProperty
from bpy.types import PropertyGroup, UIList, Operator, Panel


class MyItem(bpy.types.PropertyGroup):

    my_item_name:StringProperty(
        name = "my_item_name",
        default = "untitled queue"
        )
    
    start_frame:IntProperty(
        name = "start_frame",
        default = 0,
        min = 0,
        update=lambda self,
        context: self.update_end_frame(context)
        )
    
    end_frame:IntProperty(
        name = "end_frame",
        default = 0,
        min = 0,
        update=lambda self,
        context: self.update_start_frame(context)
        )
    
    # 更新 start_frame 的值
    def update_start_frame(self, context):
        if self.start_frame > self.end_frame:
            self.start_frame = self.end_frame

    # 更新 end_frame 的值
    def update_end_frame(self, context):
        if self.end_frame < self.start_frame:
            self.end_frame = self.start_frame

# 定义属性函数
def My_Properties():

    # list 数据
    bpy.types.Scene.my_list = CollectionProperty(type = MyItem)

    # 当前选中的下标
    bpy.types.Scene.active_index = bpy.props.IntProperty(name = "Index for my_list", default = 0)

    # 用于判断是否要关机的布尔值
    bpy.types.Scene.power_off_bool = bpy.props.BoolProperty(
        name="Power off Bool",
        description="Boolean value used to determine whether to shut down",
        default= False
    )


# 定义队列
class RenderingGear_UL_Queue(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon_value, active_data, active_propname, index):
        
        # 队列图标
        custom_icon = "RENDER_RESULT"

        # 三种显示模式: 'DEFAULT', 'COMPACT', 'GRID'
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text = "Frame：" + str(item.start_frame) + " - " + str(item.end_frame), translate = False, icon = custom_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text = "", icon = custom_icon)


# 添加新的队列
class RenderingGear_OT_CreateItem(bpy.types.Operator):
    bl_idname = 'iz.rendering_create_item'
    bl_label = 'RenderingGearCreateItem'
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):

        context.scene.my_list.add()

        # 对新建的队列的开始帧和结束帧初始化
        i = len(bpy.context.scene.my_list) - 1   # 需要操作的项

        # 同步成当成场景所设置的开始帧与结束帧
        bpy.context.scene.my_list[i].start_frame =  bpy.context.scene.frame_start
        bpy.context.scene.my_list[i].end_frame =  bpy.context.scene.frame_end

        return{'FINISHED'}

# 删除所选队列
class RenderingGear_OT_DeleteItem(bpy.types.Operator):
    bl_idname = 'iz.rendering_delete_item'
    bl_label = 'RenderingGearDeleteItem'

    @classmethod
    def poll(cls, context):
        if context.scene.my_list:
            return context.scene.my_list

        return False

    def execute(self, context):   
        # 从scene接收collection和list_index
        my_list = context.scene.my_list
        index = context.scene.active_index

        # 删除项，更改当前选择项索引
        my_list.remove(index)

        # 重新更新队列
        context.scene.active_index = min(max(0, index - 1), len(my_list) - 1)

        return {'FINISHED'}
    
# 一键清空所有队列
class RenderingGear_OT_ClearItem(bpy.types.Operator):
    bl_idname = 'iz.rendering_clear_item'
    bl_label = 'RenderingGearClearItem'

    def execute(self, context):
        bpy.context.scene.my_list.clear()

        # 将选中状态缺省至第一位
        bpy.context.scene.active_index = 0
        
        return{'FINISHED'}

# 移动队列
class RenderingGear_OT_MoveItem(bpy.types.Operator):
    bl_idname = 'iz.rendering_move_item'
    bl_label = 'RenderingGearMoveItem'

    # 控制移动的方向
    items = [
        ("UP",'up','',1),
        ("DOWN",'down','',2)
    ]

    direction: bpy.props.EnumProperty(items = items)

    @classmethod
    def poll(cls, context):
        return True


    def execute(self, context):

        # 当前所选的编号
        active_index = context.scene.active_index

        # 目标编号
        neighbor_index = context.scene.active_index + (-1 if self.direction == "UP" else 1)

        # 如果所选的项是最顶部或最底部则取消操作
        if neighbor_index < 0 or neighbor_index >= len(context.scene.my_list):
            return {"CANCELLED"}

        # 交换数据
        context.scene.my_list.move(active_index, neighbor_index)

        # 更新下标
        context.scene.active_index = neighbor_index

        return{'FINISHED'}




# 管理渲染命令
def cmd_Run(current_queue):

    start = bpy.context.scene.my_list[current_queue].start_frame
    end = bpy.context.scene.my_list[current_queue].end_frame

    # blender 的可执行文件路径
    blender_pathA = bpy.app.binary_path
    blender_pathB = blender_pathA.replace("\\", "\\\\")
    blender_pathC = blender_pathB.replace(' ', '" "')

    # 当前 blender 工程文件的路径
    file_pathA = bpy.data.filepath
    file_pathB = file_pathA.replace("\\", "\\\\")

    # 导出路径
    export_pathA = bpy.data.scenes["Scene"].render.filepath
    export_pathB = export_pathA.replace("\\","\\\\")

    # 词列表  
    words =[
        "start", # 打开多一层终端
        blender_pathC, # 启动 Blneder
        "-b", # 让它在后台运行
        file_pathB, # 填入导出路径
        "-E", # 渲染引擎
        bpy.context.scene.render.engine, # 选择用哪个渲染引擎
        "-o", # 路径
        export_pathB, # 填入导出路径
        "--frame-start", # 开始帧
        str(start), # 填入当前渲染的开始帧
        "--frame-end", # 结束帧
        str(end), # 填入当前渲染的结束帧
        "-a", # 渲染动画
    ]


    # 将列表里的词组成一行命令
    sentence = ' '.join(words)

    return sentence # 将这行命令作为这个函数的返回值


# 定义渲染函数
def render(self,current_queue,total_queue):

    while current_queue != total_queue: # 如果当前所执行到的队列编号没有达到总共的队列数时，则执行一下循环

        command = cmd_Run(current_queue) # 传入当前所执行到的队列编号

        # 创建一个进程，并执行渲染命令
        process1 = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 

        return_code = process1.poll()

        if return_code is not None:
            # 如果渲染进程已结束
            if return_code == 0:                     
                self.report({'INFO'}, "第 " + str(current_queue + 1) + " 个队列已渲染完成")
                print("第 " + str(current_queue + 1) + " 个队列已渲染完成")
            else:
                print(f"后台渲染出错，错误代码 {return_code}")
            break
        else:
            # 渲染进程仍在运行
            line = process1.stdout.readline()
            if line:
                print(line.decode("utf-8").strip())

        current_queue = current_queue + 1

    is_power_off() # 判断是否要关机


# 定义判断是否要关机的函数
def is_power_off():
    if bpy.context.scene.power_off_bool == True:
        os.system("shutdown -r -t 300") # 关机操作




# 侧边栏
class RenderingGear_PT_OperatorUI(bpy.types.Panel):
    bl_idname = 'iz.rendering_gear_ui'
    bl_label = 'Background automatic queue rendering'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'RenderGear'

    def draw(self, context):
        
        scene = context.scene
        layout = self.layout

        # 标签
        row = layout.row()
        row.label( text = " --  Render Queue -- ")

        # 添加「清空列表」的按钮
        row = layout.row()
        row.operator("iz.rendering_clear_item", text = "Clear List", icon = "TRASH")
        
        # 显示列表
        row = layout.row()
        row.template_list("RenderingGear_UL_Queue", "", scene, "my_list", scene, "active_index")

        # 位于右侧创建「添加」按钮
        subcol = row.column()
        subcol.operator("iz.rendering_create_item", text = "", icon = "ADD")

        # 位于右侧创建「删除」按钮
        subcol.operator("iz.rendering_delete_item", text = "", icon = "REMOVE")

        # 位于右侧创建「上升」按钮
        subcol.operator("iz.rendering_move_item", text = "", icon = "TRIA_UP").direction = "UP"

        # 位于右侧创建「下降」按钮
        subcol.operator("iz.rendering_move_item", text = "", icon = "TRIA_DOWN").direction = "DOWN"
        
        # 显示数据
        if (scene.active_index >= 0 or scene.active_index < len(scene.my_list)) and scene.my_list:
            item = scene.my_list[scene.active_index]
            row = layout.row()
            row.prop(item, "start_frame", text = "Start")
            row.prop(item, "end_frame", text = "End")

        # 创建一个列来放置单选框
        col = layout.column()

        # 添加一个布尔属性，并将其绑定到单选框
        col.prop(context.scene, "power_off_bool", text = " Shutdown after rendering is finished")

        # 添加「渲染所有」的按钮
        row = layout.row()
        row.operator("iz.rendering_gear1", text = "Render All", icon = "CONSOLE")

        pass




# 执行操作1
class RenderingGear_OT_Operator1(bpy.types.Operator):
    bl_idname = 'iz.rendering_gear1'
    bl_label = 'RenderingGearOperator1'
    
    def invoke(self, context, event):
        self.cmd = None

        # 判断用户是否有保存文件
        if bpy.data.is_dirty:
            self.report({'ERROR'}, "The file has not been saved. Please save the file before proceeding with this operation")
            return {'FINISHED'}
        
        
        # 判断用户所设置的结束帧数否都大于或等于开始帧
        i = len(bpy.context.scene.my_list)
        a = 0
        while a != i:
            if bpy.context.scene.my_list[a].end_frame >= bpy.context.scene.my_list[a].start_frame:
                a = a + 1
            else:
                self.report({'ERROR'}, "Please check if the set end frame is greater than the start frame")
                return {'FINISHED'}

        
        if not event.ctrl:
            return self.execute(context)
        
        return {'FINISHED'}

    # 执行的内容
    def execute(self, context):

        total_queue = len(bpy.context.scene.my_list) # 总共的队列数
        current_queue = 0 # 当前所执行到的队列编号

        self.report({'INFO'}, "The total number of queues is " + str(total_queue) + " , Start performing background rendering")
        print("The total number of queues is " + str(total_queue) + " , Start performing background rendering")

        # 创建线程，并且传参
        task1 = threading.Thread(target = render,args = (self, current_queue, total_queue, ))

        task1.start() # 启用线程

        return {'FINISHED'}


# 需要注册的类
classes = [
    MyItem,
    RenderingGear_UL_Queue,
    RenderingGear_OT_Operator1,
    RenderingGear_OT_CreateItem,
    RenderingGear_OT_DeleteItem,
    RenderingGear_OT_ClearItem,
    RenderingGear_OT_MoveItem,
    RenderingGear_PT_OperatorUI,

]

# 注册
def register():
    for item in classes:
        bpy.utils.register_class(item) 

    # 注册属性
    My_Properties()

    print("REGISTER COMPLEX") 

# 注销
def unregister():
    for item in classes:
        bpy.utils.unregister_class(item)
    
    # 删除属性
    del bpy.types.Scene.my_list
    del bpy.types.Scene.active_index
    del bpy.types.Scene.power_off_bool

    print("PHANTOM HAS RETURNED TO THEIR WORDL")
