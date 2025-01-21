import bpy
from bpy.props import EnumProperty 
from bpy.types import AddonPreferences, PropertyGroup
import rna_keymap_ui

enable_ori = True
enable_piv = True


class OverFlags(PropertyGroup):
    
    ori_overridden: bpy.props.BoolProperty(
        name = "",
        description = "",
        default = False,
    )
    
    piv_overridden: bpy.props.BoolProperty(
        name = "",
        description = "",
        default = False,
    )
    
    stored_orientation: bpy.props.StringProperty(
        name = "",
        description = "",
        default = 'Global',
    ) 
    
    stored_pivot: bpy.props.StringProperty(
        name = "",
        description = "",
        default = 'INDIVIDUAL_ORIGINS',
    )    


# Override current Transform Orientation and Pivot Point to 'Cursor' or restore everything back.
class CURSORPLUS_OT_override(bpy.types.Operator):
    bl_idname = "cursorplus.override"
    bl_label = ""
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}    
    
    action: EnumProperty(
        items=[
            ('ORIENT', 'Override Orientation', ""),
            ('PIVOT', 'Override Pivot Point', ""),
            ('ALL', 'Override All', ""),
            ('STOP', 'Stop Override', "")
        ]
    )
    
    
    @classmethod
    def description(cls, context, properties):
        if properties.action == 'ORIENT':
            return "Override Transform orientation to 'Cursor'"
        if properties.action == 'PIVOT':
            return "Override Transform Pivot Point to 'Cursor'" 
        if properties.action == 'ALL':
            return "Override Transform Orientation and Pivot Point to 'Cursor' " 
        if properties.action == 'STOP':
            return "Revert Overriden parameter(s) to previous state" 
    
    def execute(self, context):
        global test_prop
        t_orientation = context.scene.transform_orientation_slots[0]
        p_point = context.tool_settings
        flags = context.scene.over

        if self.action == 'ORIENT':
            if not flags.ori_overridden:
                flags.stored_orientation = t_orientation.type
                t_orientation.type = 'CURSOR'
                flags.ori_overridden = True
           
        elif self.action == 'PIVOT':
            if not flags.piv_overridden:
                flags.stored_pivot = p_point.transform_pivot_point
                p_point.transform_pivot_point = 'CURSOR'
                flags.piv_overridden = True  
        
        elif self.action == 'ALL':
            if not flags.ori_overridden and not flags.piv_overridden or\
            p_point.transform_pivot_point != 'CURSOR' and \
            t_orientation.type != 'CURSOR': 
                flags.stored_orientation = t_orientation.type
                flags.stored_pivot = p_point.transform_pivot_point
                t_orientation.type = 'CURSOR'
                p_point.transform_pivot_point = 'CURSOR'
                flags.ori_overridden = True
                flags.piv_overridden = True
        
        elif self.action == 'STOP':
            if flags.ori_overridden:
                flags.ori_overridden = False
                # Check if overriden orientation was manualy changed.
                if t_orientation.type == 'CURSOR':
                    t_orientation.type = flags.stored_orientation
                
            if flags.piv_overridden:
                flags.piv_overridden = False
                # Check if overriden pivot point was manualy changed.
                if p_point.transform_pivot_point == 'CURSOR':  
                    p_point.transform_pivot_point = flags.stored_pivot
        
        return {'FINISHED'}


# Process changes in the custom snap list
class CURSORPLUS_OT_toggle_list(bpy.types.Operator):
    bl_idname = "cursorplus.toggle_list"
    bl_label = ""
    bl_options = {'REGISTER', 'INTERNAL'}    
    
    element: EnumProperty(
        items=[
            ('INCREMENT', 'Inc', "Toggle snap to increments"),
            ('GRID', 'Grid', "Toggle snap to grid"),
            ('VERTEX', 'Vert', "Toggle snap to vertices"),
            ('EDGE', 'Edge', "Toggle snap to edges"),
            ('FACE', 'Face', "Toggle snap to faces"),
            ('EDGE_MIDPOINT', 'Edge Mid', "Toggle snap to the middle of edges"),
            ('EDGE_PERPENDICULAR', 'Edge Perp', "Toggle snap to the nearest point of an edge")
        ]
    )
    
    @classmethod
    def description(cls, context, properties):
        if properties.element == 'INCREMENT':
            return "Toggle snap to increments"
        if properties.element == 'GRID':
            return "Toggle snap to grid" 
        if properties.element == 'VERTEX':
            return "Toggle snap to vertices" 
        if properties.element == 'EDGE':
            return "Toggle snap to edges" 
        if properties.element == 'FACE':
            return "Toggle snap to faces" 
        if properties.element == 'EDGE_MIDPOINT':
            return "Toggle snap to the middle of edges" 
        if properties.element == 'EDGE_PERPENDICULAR':
            return "Toggle snap to the nearest point of an edge"     
    
    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        snap_list = set(prefs.plus_snap_list.split(','))
        if len(snap_list) == 1 and self.element in snap_list:
            return {'FINISHED'}

        if self.element in snap_list:
            snap_list.remove(self.element)
        else:
            snap_list.add(self.element)
        prefs.plus_snap_list = ','.join(snap_list)
        bpy.context.area.tag_redraw()
        return {'FINISHED'}
    

# CURSORPLUS related operators     CURSORPLUS related operators      CURSORPLUS related operators   

# Iterate through selected objects, using 'QUATERNION' for unified rotation translation.
class CURSORPLUS_OT_copy_rot_to_selected(bpy.types.Operator):
    bl_idname = "object.cursor_plus_copy"
    bl_label = "Copy Cursor's Rotation"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Copy rotation of the 3D cursor to selected object(s)"

    @classmethod
    def poll(cls, context):
         obj = context.active_object
         return obj is not None and obj.select_get() \
            and context.area.type == 'VIEW_3D' and context.mode in {'OBJECT', 'EDIT_MESH'}

    def execute(self, context):
        cursor = bpy.context.scene.cursor
        store_cursor_mode = cursor.rotation_mode
        cursor.rotation_mode = 'QUATERNION'
        for obj in context.selected_objects:
            store_obj_mode =  obj.rotation_mode
            obj.rotation_mode = 'QUATERNION'
            obj.rotation_quaternion = cursor.rotation_quaternion
            obj.rotation_mode = store_obj_mode
        cursor.rotation_mode = store_cursor_mode    
        return {'FINISHED'}


class CURSORPLUS_OT_clear_cursor_rot(bpy.types.Operator):
    bl_idname = "object.cursor_plus_clear"
    bl_label = "Clear Cursor's Rotation"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Clear the 3D cursor's rotation"
    
    def execute(self, context):
        cursor = bpy.context.scene.cursor
        cursor.rotation_euler = (0,0,0)
        bpy.context.scene.cursor.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)
        cursor.rotation_axis_angle = (0, 0, 1, 0)
        return {'FINISHED'} 


class CURSORPLUS_OT_move_with_cursor(bpy.types.Operator):
    bl_idname = "object.cursor_plus_move"
    bl_label = "Move along the Cursor"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Move selection along the Z axis of the 3D cursor"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.select_get() \
            and context.area.type == 'VIEW_3D' and context.mode in {'OBJECT', 'EDIT_MESH'}
    
    def execute(self, context):
        bpy.ops.transform.translate(
            'INVOKE_DEFAULT',
            orient_type = 'CURSOR',
            orient_matrix_type = 'CURSOR',
            constraint_axis = (False, False, True),
            )
        return {'FINISHED'}


class CURSORPLUS_OT_pivot_with_cursor(bpy.types.Operator):
    bl_idname = "object.cursor_plus_rotate"
    bl_label = "Rotate around the Cursor"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Pivot selection around the 3D cursor. Default axis is Z axis of the 3D Cursor"
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.select_get() \
            and context.area.type == 'VIEW_3D' and context.mode in {'OBJECT', 'EDIT_MESH'}
    
    def execute(self, context):
        bpy.ops.transform.rotate(
            'INVOKE_DEFAULT',
            orient_type = 'CURSOR',
            orient_matrix_type = 'CURSOR',
            center_override = bpy.context.scene.cursor.location,
            orient_axis = 'Z',
            constraint_axis = (False, False, True),
            release_confirm = False
            )
        return {'FINISHED'}

    
class CURSORPLUS_OT_scale_from_cursor(bpy.types.Operator):
    bl_idname = "object.cursor_plus_scale"
    bl_label = "Scale relative to the Cursor"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Scale selection using the 3D cursor as a transform point"
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.select_get() \
            and context.area.type == 'VIEW_3D' and context.mode in {'OBJECT', 'EDIT_MESH'}
    
    def execute(self, context):
        bpy.ops.transform.resize(
            'INVOKE_DEFAULT',
            orient_type = 'CURSOR',
            orient_matrix_type = 'CURSOR',
            center_override = bpy.context.scene.cursor.location,
            release_confirm = False
            )
        return {'FINISHED'}
    
# Move the 3D Cursor with its own snap and align options enabled. Transform orientation - 'Cursor'. 
class CURSORPLUS_OT_move_cursor(bpy.types.Operator):
    bl_idname = "object.cursor_plus_snap"
    bl_label = "Snap Cursor"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """Move the 3D Cursor 
temporarily using custom 'Snap' and 'Align Rotation to Target' options"""

    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D' and context.mode in {'OBJECT', 'EDIT_MESH'}
    
    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        current_transformation = bpy.data.scenes["Scene"].transform_orientation_slots[0].type
        bpy.data.scenes["Scene"].transform_orientation_slots[0].type = 'CURSOR'
        snap_list = set(prefs.plus_snap_list.split(','))
        
        bpy.ops.transform.translate(
            'INVOKE_DEFAULT',
            value=(0, 0, 0),
            orient_type='CURSOR',
            orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            orient_matrix_type='CURSOR',
            mirror=False, snap=True, snap_elements=snap_list,
            use_snap_project=False, snap_target='CLOSEST', use_snap_self=True,
            use_snap_edit=True, use_snap_nonedit=True, snap_align=prefs.plus_snap_align,
            use_snap_selectable=True, cursor_transform=True, release_confirm=False
            )
        bpy.data.scenes["Scene"].transform_orientation_slots[0].type = current_transformation    
        return {'FINISHED'}

# Draw panels   Draw panels   Draw panels   Draw panels   Draw panels   Draw panels   Draw panels

# Main Parent-panel with PLUS Operators 
class CURSORPLUS_PT_cursor_ops(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "View"
    bl_parent_id = "VIEW3D_PT_view3d_cursor"
    bl_label = "3D Cursor Plus"

    def draw(self, context):
        prefs = context.preferences.addons[__package__].preferences
        show_gizmo = context.space_data.shading.show_gizmo_cursor_plus
        bsy1 = 0.7 #button scale y
        bsy2 = 0.7 #button scale y
        layout = self.layout
        col = layout.column()
        row = col.row(align=True)
        box = row.box()
        box.operator('object.cursor_plus_snap', emboss=False, text="Snap to ...", icon='ORIENTATION_CURSOR')
        box = row.box()
        box.operator('object.cursor_plus_clear', emboss=False, text="Clear Rotation")
        
 
        box = col.box()    
        col = box.column(align=True)
        row1 = col.row()
        row1.alignment = 'CENTER'
        row1.label(text="Transform selected")
        
        row = col.row(align=True)
        box = row.box()
        box.scale_y = bsy2
        box.operator('object.cursor_plus_move', emboss=False, text="Move", icon='MOD_LENGTH')
        box = row.box()
        box.scale_y = bsy2
        box.operator('object.cursor_plus_rotate', emboss=False, text="Rotate", icon='CON_ROTLIKE')
        
        row = col.row(align=True)
        box = row.box()
        box.scale_y = bsy2
        box.operator('object.cursor_plus_scale', emboss=False, text="Scale", icon='CON_LOCLIKE')
        box = row.box()
        box.scale_y = bsy2
        box.operator('object.cursor_plus_copy', emboss=False, text="Copy Rotation") #, icon='ORIENTATION_PARENT')
        
        col = layout.column()
        spl = col.split(factor=0.8)
        box = spl.box()
        if prefs.preset_select:
            box.operator('cursorplus.gizmo_presets', emboss=False, text="Gizmo Preset", icon='EVENT_G')
        else:
            box.operator('cursorplus.gizmo_presets', emboss=False, text="Axes Preset", icon='EVENT_A')
        box = spl.box()
        box.operator('object.cursor_gizmo_visibility', emboss=False, text="", \
                    icon='HIDE_OFF' if show_gizmo else 'HIDE_ON')
               
    
# Child-panel with snap elements. Separated to be accessable from pie-menu.
class CURSORPLUS_PT_snap_list(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "CURSORPLUS_PT_cursor_ops"
    bl_label = "Snap Options"
    bl_options = {'DEFAULT_CLOSED'}
        
    def draw(self, context):
        prefs = context.preferences.addons[__package__].preferences
        snap_list = set(prefs.plus_snap_list.split(','))
        box = self.layout.box()
        row = box.row(align=True)
        row.scale_x = 5
        row.operator('cursorplus.toggle_list', text="", icon='SNAP_INCREMENT', \
            emboss=True if 'INCREMENT' in snap_list else False).element='INCREMENT'
        row.operator('cursorplus.toggle_list', text="", icon='SNAP_GRID', \
            emboss=True if 'GRID' in snap_list else False).element='GRID'
        row.operator('cursorplus.toggle_list', text="", icon='SNAP_VERTEX', \
            emboss=True if 'VERTEX' in snap_list else False).element='VERTEX'
        row.operator('cursorplus.toggle_list', text="", icon='SNAP_EDGE', \
            emboss=True if 'EDGE' in snap_list else False).element='EDGE'
        row.operator('cursorplus.toggle_list', text="", icon='SNAP_FACE_CENTER', \
            emboss=True if 'FACE' in snap_list else False).element='FACE'
        row.operator('cursorplus.toggle_list', text="", icon = 'SNAP_MIDPOINT', \
            emboss=True if 'EDGE_MIDPOINT' in snap_list else False).element='EDGE_MIDPOINT'
        row.operator('cursorplus.toggle_list', text="", icon='SNAP_PERPENDICULAR', \
            emboss=True if 'EDGE_PERPENDICULAR' in snap_list else False).element='EDGE_PERPENDICULAR'
        row = box.row(align=True)
        row.alignment = 'CENTER'
        row.prop(prefs, 'plus_snap_align', text="Align Rotation to Target")
 
# Child-panel with Override controls. Separated to be accessable from pie-menu.        
class CURSORPLUS_PT_override(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "CURSORPLUS_PT_cursor_ops"
    bl_label = "Override Transform Options"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):    
        layout = self.layout
        flags = context.scene.over
        # Flags to disable buttons if orientation or pivot was set to 'Cursor'
        if context.scene.transform_orientation_slots[0].type != 'CURSOR':
            enable_ori = True
        else: 
            enable_ori = False
        
        if context.tool_settings.transform_pivot_point != 'CURSOR':            
            enable_piv = True
        else: 
            enable_piv = False
            
        if enable_piv and enable_ori:
            enable_both = True
        else: 
            enable_both = False    
        
        if flags.ori_overridden and not enable_ori or flags.piv_overridden and not enable_piv:
            enable_stop = True
        else:
            enable_stop = False
        
        col = layout.column()
        spl = col.split(factor=0.4)
        box = spl.box()
        box.scale_y=1.6
        if enable_both and not enable_stop:
            box.operator('cursorplus.override', emboss=False, text="ALL", icon='AUTO').action='ALL'
            box.enabled = enable_both
        else:
            box.operator('cursorplus.override', emboss=False, text="STOP", icon='CANCEL').action='STOP'
            box.enabled = enable_stop
        
        col = spl.column()
        col1 = col.column(align=True)
        col1.operator('cursorplus.override', text="Orientation", icon='ORIENTATION_CURSOR').action='ORIENT'
        col1.enabled = enable_ori
        col2 = col.column(align=True)
        col2.operator('cursorplus.override', text="Pivot Point", icon='PIVOT_CURSOR').action='PIVOT'
        col2.enabled = enable_piv


# Default 'update panel' section to process changes in 'Tab category' field in addon preferences.

def updatePanel(self, context):
    
    panels = (
        CURSORPLUS_PT_cursor_ops,
        CURSORPLUS_PT_snap_list,
        CURSORPLUS_PT_override,
        )
    
    try:
        for panel in panels:
            if "bl_rna" in panel.__dict__:
                bpy.utils.unregister_class(panel)
        prefs = context.preferences.addons[__package__].preferences
        CURSORPLUS_PT_cursor_ops.bl_category = prefs.category_plus
        CURSORPLUS_PT_cursor_ops.bl_parent_id = "VIEW3D_PT_view3d_cursor" if prefs.use_parent_plus else ""
        
        for panel in panels:
            bpy.utils.register_class(panel)

    except Exception as e:
        print("\n[{}]\n{}\n\nError:\n{}".format(__package__, message, e))
        pass


# Customizable Pie-menu with PLUS Operators and callable Snap and Override panels.
class CURSORPLUS_MT_cursor_plus_pie(bpy.types.Menu):
    bl_label = "3D Cursor Plus Pie"
    bl_idname = "CURSORPLUS_MT_cursor_plus_pie"

    def slice(self, context, item):
        prefs = context.preferences.addons[__package__].preferences
        show_gizmo = context.space_data.shading.show_gizmo_cursor_plus
        pie = self.layout.menu_pie()
        if item == "MOVECURSOR":
            pie.operator('object.cursor_plus_snap', text="Snap 3D Cursor", icon='ORIENTATION_CURSOR') 
    
        if item == "MOVE":
            pie.operator('object.cursor_plus_move', text="Move", icon='MOD_LENGTH')
        
        if item == "ROTATE":
            pie.operator('object.cursor_plus_rotate',  text="Rotate", icon='CON_ROTLIKE')
                       
        if item == "SCALE":
            pie.operator('object.cursor_plus_scale', text="Scale", icon='CON_LOCLIKE')
                        
        if item == "TWEAK":
            pie.operator('wm.call_panel', text="Tweak Snapping", icon='SNAP_ON').name="CURSORPLUS_PT_snap_list"
                  
        if item == "CLEAR":    
            pie.operator('object.cursor_plus_clear', text="Clear Rotation")
        
        if item == "COPY":
            pie.operator('object.cursor_plus_copy', text="Copy Rotation", icon='ORIENTATION_PARENT')
            
        if item == "OVER":
            pie.operator('wm.call_panel', text="Override", icon='AUTO').name="CURSORPLUS_PT_override"
        
        if item == "PRESET":
            if prefs.preset_select:
                pie.operator('cursorplus.gizmo_presets', text="Gizmo Preset", icon='EVENT_G')
            else:
                pie.operator('cursorplus.gizmo_presets', text="Axes Preset", icon='EVENT_A')
            
        if item == "PRESET_R":
            row = pie.row(align=True)
            box = row.box()
            box.scale_y=1.2
            box.scale_x=1.1
            box.operator('object.cursor_gizmo_visibility', emboss=False, text="", icon='HIDE_OFF' if show_gizmo else 'HIDE_ON')
            box = row.box()
            box.scale_y=1.2
            if prefs.preset_select:
                box.operator('cursorplus.gizmo_presets', emboss=False, text="Gizmo Preset", icon='EVENT_G')
            else:
                box.operator('cursorplus.gizmo_presets', emboss=False, text="Axes Preset", icon='EVENT_A')
                
        if item == "PRESET_L":
            row = pie.row(align=True)
            box = row.box()
            box.scale_y=1.2
            if prefs.preset_select:
                box.operator('cursorplus.gizmo_presets', emboss=False, text="Gizmo Preset", icon='EVENT_G')
            else:
                box.operator('cursorplus.gizmo_presets', emboss=False, text="Axes Preset", icon='EVENT_A')
            box = row.box()
            box.scale_y=1.2
            box.scale_x=1.1
            box.operator('object.cursor_gizmo_visibility', emboss=False, text="", icon='HIDE_OFF' if show_gizmo else 'HIDE_ON')
            
        if item == "VISION":
            pie.operator('object.cursor_gizmo_visibility', text="", icon='HIDE_OFF' if show_gizmo else 'HIDE_ON')    
                    
        if item == "EMPTY":
            pie.separator()        
        
    
    def draw(self, context): 
        prefs = context.preferences.addons[__package__].preferences        
        
        # Left
        self.slice(context, prefs.pie_left)

        # Right
        self.slice(context, prefs.pie_right)
    
        # Bot
        self.slice(context, prefs.pie_bottom)
                       
        # Top
        self.slice(context, prefs.pie_top)
                        
        # Top-Left
        self.slice(context, prefs.pie_top_left)

        # Top-Right
        self.slice(context, prefs.pie_top_right)        
                  
        # Bot-Left    
        self.slice(context, prefs.pie_bottom_left)        
        
        # Bot-Right
        self.slice(context, prefs.pie_bottom_right)        
        

# Register/unregister section
classes = (
    OverFlags,
    CURSORPLUS_OT_toggle_list,
    CURSORPLUS_OT_clear_cursor_rot,
    CURSORPLUS_OT_copy_rot_to_selected,
    CURSORPLUS_OT_move_with_cursor,
    CURSORPLUS_OT_pivot_with_cursor,
    CURSORPLUS_OT_scale_from_cursor,
    CURSORPLUS_OT_move_cursor,
    CURSORPLUS_OT_override,
    CURSORPLUS_PT_cursor_ops,
    CURSORPLUS_PT_snap_list,
    CURSORPLUS_PT_override,
    CURSORPLUS_MT_cursor_plus_pie,
)
  
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.over = bpy.props.PointerProperty(type=OverFlags)
    
    updatePanel(None, bpy.context)

    
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.over