import bpy
import rna_keymap_ui
import textwrap

from mathutils import Matrix
from bpy.props import EnumProperty

from .cursor_plus import updatePanel
from .cursor_undo import toggleUndo
from . import cursor_text
from . import preset_management


pie_items = [
    ("MOVECURSOR", "Snap 3D Cursor", ""),
    ("MOVE", "Move", ""),
    ("ROTATE", "Rotate", ""),
    ("SCALE", "Scale", ""),
    ("TWEAK", "Tweak Snapping", ""),
    ("CLEAR", "Reset 3D Cursor", ""),
    ("COPY", "Copy Rotation", ""),
    ("OVER", "Override Panel", ""),
    ("OVER_ALT", "Override Button", ""),    
    ("PRESET", "Gizmo Preset", ""),
    ("PRESET_R", "Gizmo Preset(R)", ""),
    ("PRESET_L", "Gizmo Preset(L)", ""),
    ("VISION", "Toggle Visibility", ""),
    ("EMPTY", "- Not used - ", ""),
]

plus_ops = (
    "cursorplus.snap_cursor",
    "cursorplus.clear_cursor",
    "cursorplus.move_selected",
    "cursorplus.rotate_selected",
    "cursorplus.scale_selected",
    "cursorplus.copy_rot_to_selected",
    "cursorplus.gizmo_visibility"
)

snap_elements = [
    ("INCREMENT", "SNAP_INCREMENT"),
    ("GRID", "SNAP_GRID"),
    ("VERTEX", "SNAP_VERTEX"),
    ("EDGE", "SNAP_EDGE"),
    ("FACE", "SNAP_FACE"),
    ("EDGE_MIDPOINT", "SNAP_MIDPOINT"),
    ("EDGE_PERPENDICULAR", "SNAP_PERPENDICULAR"),
]

txt = cursor_text

# Multiline text output. Found this workaround on b3d.interplanety.org. Huge thanks to Nikita!
def _label_multiline(context, text, parent):
    scale = context.preferences.system.ui_scale 
    chars = int(context.region.width/(6.2*scale))   
    wrapper = textwrap.TextWrapper(width=chars)
    text_lines = wrapper.wrap(text=text)
    for text_line in text_lines:
        parent.label(text=text_line)

def redraw_cursor(self, context):
    bpy.app.timers.register(redraw_area, first_interval = 0.03)

def redraw_area():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                with bpy.context.temp_override(area=area):
                    bpy.context.area.tag_redraw()
    return None 

def theme_colors(self, context):
    prefs = context.preferences.addons[__package__].preferences
    theme = context.preferences.themes[0].user_interface
    if prefs.use_theme:
        prefs.axis_x_color = theme.axis_x
        prefs.axis_y_color = theme.axis_y
        prefs.axis_z_color = theme.axis_z
        prefs.dot_color = theme.gizmo_view_align
    if prefs.use_theme2:
        prefs.axis_x_color2 = theme.axis_x
        prefs.axis_y_color2 = theme.axis_y
        prefs.axis_z_color2 = theme.axis_z
        prefs.dot_color2 = theme.gizmo_view_align

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Toggle operators   Toggle operators   Toggle operators   Toggle operators   Toggle operators

class CURSORPLUS_OT_gizmo_presets(bpy.types.Operator):
    bl_idname = "cursorplus.gizmo_presets"
    bl_label = "3D Cursor Gizmo Presets"
    bl_options = {'REGISTER', 'INTERNAL'}
    bl_description = "Toggle between Axes/Gizmo presets"
    
    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        prefs.preset_select = not prefs.preset_select
        return {'FINISHED'}

class CURSORPLUS_OT_gizmo_visibility(bpy.types.Operator):
    bl_idname = "cursorplus.gizmo_visibility"
    bl_label = "3D Cursor Gizmo Visibility"
    bl_options = {'REGISTER', 'INTERNAL'}
    bl_description = "Toggle Axes/Gizmo visibility"
    
    def execute(self, context):
        shading = context.space_data.shading
        shading.show_gizmo_cursor_plus = not shading.show_gizmo_cursor_plus
        redraw_area()
        return {'FINISHED'}
    
class CURSORPLUS_OT_align_rotation(bpy.types.Operator):
    bl_idname = "cursorplus.align_rotation"
    bl_label = "Align Rotation to Target"
    bl_options = {'REGISTER', 'INTERNAL'}
    bl_description = "Align Rotation to Target"
    
    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        prefs.plus_snap_align = not prefs.plus_snap_align
        if prefs.plus_snap_align:
            self.report({'INFO'}, f"Align Rotataion to Target")
        else:
            self.report({'INFO'}, f"Keep Orientation")
        return {'FINISHED'}    

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

class CursorPlusPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    pref_tabs: EnumProperty(
        name = "Category",
        description="Preferences Tabs",
        items = [
            ('GIZMO', "Axes / Gizmo", ""),
            ('PLUS_KEYMAP', "Keymap", ""),
            ('UNDO', "Undo Info", ""),
        ],
        default = 'GIZMO'
    )
    
    keymap_tabs: EnumProperty(
        name = "Keymaps",
        description="Keymaps Tabs",
        items = [
            ('GENERAL', "General", ""),
            ('PLUS_OPS', "PLUS Ops", ""),
            ('SNAP', "Snap Options", ""),
        ],
        default = 'GENERAL'
    )
    
# Pie items   Pie items   Pie items   Pie items   Pie items   Pie items   Pie items   Pie items  

    pie_left: EnumProperty(
        name = "Left",
        items = pie_items,
        default = "MOVECURSOR"
    )
    
    pie_right: EnumProperty(
        name = "Right",
        items = pie_items,
        default = "MOVE"
    )

    pie_bottom: EnumProperty(
        name = "Bottom",
        items = pie_items,
        default = "ROTATE"
    )
    
    pie_top: EnumProperty(
        name = "Top",
        items = pie_items,
        default = "SCALE"
    )
    
    pie_top_left: EnumProperty(
        name = "Top Left",
        items = pie_items,
        default = "TWEAK"
    )
    
    pie_top_right: EnumProperty(
        name = "Top Right",
        items = pie_items,
        default = "OVER"
    )
   
    pie_bottom_left: EnumProperty(
        name = "Bottom Left",
        items = pie_items,
        default = "PRESET"
    )
  
    pie_bottom_right: EnumProperty(
        name = "Bottom Right",
        items = pie_items,
        default = "CLEAR"
    )

# Gizmo prefs   Gizmo prefs   Gizmo prefs   Gizmo prefs   Gizmo prefs   Gizmo prefs   Gizmo prefs    

    sync_with_3d_cursor: bpy.props.BoolProperty(
        name = """Link: Hide the Axes/Gizmo if the 3D Cursor is not visible.
Unlink: Allow to use the Axes/Gizmo with or without the 3D Cursor.""",
        default = True
    )
    
    use_3d_cursor_gizmo: bpy.props.BoolProperty(
        name = "Use 3D Cursor Gizmo",
        default = True
    )

    show_axes: bpy.props.BoolProperty(
        name = "Show Axes",
        default = True
    )
    
    show_axes2: bpy.props.BoolProperty(
        name = "Show Axes",
        default = True
    )

    axes_gizmo: bpy.props.BoolProperty(
        name = "Axes as Gizmo",
        default = False
    )
    
    axes_gizmo2: bpy.props.BoolProperty(
        name = "Axes as Gizmo",
        default = True
    )

    show_dot: bpy.props.BoolProperty(
        name = "Show Dot",
        default = True
    )
    
    show_dot2: bpy.props.BoolProperty(
        name = "Show Dot",
        default = True
    )

    dot_gizmo: bpy.props.BoolProperty(
        name = "Dot as Gizmo",
        default = False
    )
    
    dot_gizmo2: bpy.props.BoolProperty(
        name = "Dot as Gizmo",
        default = True
    )
    
    use_theme: bpy.props.BoolProperty(
        name = "Use Theme Colors",
        default = False,
        update = theme_colors
    )
    
    use_theme2: bpy.props.BoolProperty(
        name = "Use Theme Colors",
        default = True,
        update = theme_colors
    )

    custom_gizmo_size: bpy.props.IntProperty(
        name  = "Gizmo Size",
        default = 5,
        min = 0,
        soft_max = 200,
        step = 5,
        subtype='PERCENTAGE'
    )
    
    custom_gizmo_size2: bpy.props.IntProperty(
        name  = "Gizmo Size",
        default = 100,
        min = 0,
        soft_max = 200,
        step = 5,
        subtype='PERCENTAGE'
    )

    arrow_length: bpy.props.IntProperty(
        name = "Arrow Length",
        default = 600,
        min = 0,
        soft_max = 1000,
        subtype = 'PERCENTAGE'
    )
    
    arrow_length2: bpy.props.IntProperty(
        name = "Arrow Length",
        default = 100,
        min = 0,
        soft_max = 1000,
        subtype = 'PERCENTAGE'
    )

    arrow_width: bpy.props.FloatProperty(
        name = "Arrow Width",
        default = 2.5,
        min = 0.0,
        soft_max = 12.0,
        subtype = 'FACTOR'
    )
    
    arrow_width2: bpy.props.FloatProperty(
        name = "Arrow Width",
        default = 2.0,
        min = 0.0,
        soft_max = 12.0,
        subtype = 'FACTOR'
    )

    dot_scale: bpy.props.IntProperty(
        name = "Dot Scale",
        default = 14,
        min = 0,
        soft_max = 100,
        subtype = 'PERCENTAGE'
    )
    
    dot_scale2: bpy.props.IntProperty(
        name = "Dot Scale",
        default = 14,
        min = 0,
        soft_max = 100,
        subtype = 'PERCENTAGE'
    )

    dot_width: bpy.props.FloatProperty(
        name = "Dot Width",
        default = 3.5,
        min = 0.0,
        soft_max = 10.0,
        subtype = 'FACTOR'
    )
    
    dot_width2: bpy.props.FloatProperty(
        name = "Dot Width",
        default = 1.0,
        min = 0.0,
        soft_max = 10.0,
        subtype = 'FACTOR'
    )

    axis_x_color: bpy.props.FloatVectorProperty(
        name = "X Axis Color",
        subtype = 'COLOR_GAMMA',
        default = (1.0, 0.211766, 0.325486),
        min = 0.0,
        max = 1.0
    )
    
    axis_x_color2: bpy.props.FloatVectorProperty(
        name = "X Axis Color",
        subtype = 'COLOR_GAMMA',
        default = (1.0, 0.211766, 0.325486),
        min = 0.0,
        max = 1.0
    )
    
    axis_y_color: bpy.props.FloatVectorProperty(
        name = "Y Axis Color",
        subtype = 'COLOR_GAMMA',
        default = (0.541176, 0.85883, 0.0),
        min = 0.0,
        max = 1.0
    )
    
    axis_y_color2: bpy.props.FloatVectorProperty(
        name = "Y Axis Color",
        subtype = 'COLOR_GAMMA',
        default = (0.541176, 0.85883, 0.0),
        min = 0.0,
        max = 1.0
    )

    axis_z_color: bpy.props.FloatVectorProperty(
        name = "Z Axis Color",
        subtype = 'COLOR_GAMMA',
        default = (0.172551, 0.560786, 1.0),
        min = 0.0,
        max = 1.0
    )
    
    axis_z_color2: bpy.props.FloatVectorProperty(
        name = "Z Axis Color",
        subtype = 'COLOR_GAMMA',
        default = (0.172551, 0.560786, 1.0),
        min = 0.0,
        max = 1.0
    )

    dot_color: bpy.props.FloatVectorProperty(
        name = "Dot Color",
        subtype = 'COLOR_GAMMA',
        default = (0.0, 0.0, 0.0),
        min = 0.0,
        max = 1.0
    )
    
    dot_color2: bpy.props.FloatVectorProperty(
        name = "Dot Color",
        subtype = 'COLOR_GAMMA',
        default = (0.0, 0.0, 0.0),
        min = 0.0,
        max = 1.0
    )
 
    alpha: bpy.props.IntProperty(
        name = "Alpha",
        default = 100,
        min = 0,
        max = 100,
        subtype='PERCENTAGE'
    )
    
    alpha2: bpy.props.IntProperty(
        name = "Alpha",
        default = 60,
        min = 0,
        max = 100,
        subtype = 'PERCENTAGE'
    )


# Plus Snap   Plus Snap   Plus Snap   Plus Snap   Plus Snap   Plus Snap   Plus Snap   Plus Snap

    plus_snap_list: bpy.props.StringProperty(
        name = "CURSORPLUS",
        default = 'EDGE'
    )

    plus_snap_align: bpy.props.BoolProperty(
        name = "Align Cursor Rotation",
        default = True
    )      

# Utility props for UI drawing    Utility props for UI drawing    Utility props for UI drawing  
    
    use_parent_plus: bpy.props.BoolProperty(
        name = "Use Parent Panel",
        description = "Define 3D Cursor Plus tab location",
        default = True,
        update = updatePanel
    )

    category_plus: bpy.props.StringProperty(
        name = "Tab Category",
        description = "3D Cursor Plus tab name",
        default = "3D Cursor Plus",
        update = updatePanel
    )
    
    plus_undo: bpy.props.BoolProperty(
        name = "Undo Toggle",
        description = "Enable/Disable Undo for 3D Cursor",
        default = True,
        update = toggleUndo
    )

    edit_pie: bpy.props.BoolProperty(
        name = "Edit Pie Menu",
        default = False,
    )
    
    set_suggest: bpy.props.BoolProperty(
        name = "",
        description = "Click me!",
        default = False,
    )
    
    move_suggest: bpy.props.BoolProperty(
        name = "",
        description = "Click me!",
        default = False,
    )
    
    set_suggest2: bpy.props.BoolProperty(
        name = "",
        description = "Click me!",
        default = False,
    )
    
    move_suggest2: bpy.props.BoolProperty(
        name = "",
        description = "Click me!",
        default = False,
    )
    
    how_it_works: bpy.props.BoolProperty(
        name = "",
        description = "Click me!",
        default = False,
    )    

    preset_select: bpy.props.BoolProperty(
        name = "",
        description = """This button is only for testing the presets while tweaking. 
To toggle between them when outside this tab, use other options such as a shortcut, 
a pie menu, a button in the sidebar, or the Quick Favorites""",
        default = True,
        update = redraw_cursor
    )
    
    
    def draw(self, context):
        prefs = context.preferences.addons[__package__].preferences
        layout = self.layout
        layout.row().prop(self, 'pref_tabs', expand=True)
        box = layout.box() 

# Gizmo Tab     Gizmo Tab     Gizmo Tab     Gizmo Tab     Gizmo Tab                 

        if self.pref_tabs == 'GIZMO':
            col = box.column()
            col.prop(self, 'use_3d_cursor_gizmo')
            if prefs.use_3d_cursor_gizmo:
                col.separator(type='LINE')
                spl = box.split(factor=0.25)
                # Labels
                colG = spl.column()
                colL = colG.column()
                subSpl = colL.split(factor=0.2)
                subSpl.prop(self, 'preset_select', text="", icon='UV_SYNC_SELECT', toggle = 1, \
                            invert_checkbox=True if prefs.preset_select else False)
                subSpl = colL.split(factor=0.2)
                subSpl.prop(self, 'sync_with_3d_cursor', text="", icon='LINKED' \
                            if prefs.sync_with_3d_cursor else 'UNLINKED', toggle = 1, \
                            invert_checkbox=True if prefs.sync_with_3d_cursor else False)


                colL.label(text=" ")
                colL.label(text=" ")

                colL.separator()
                colL = colG.column()
                row = colL.row()
                row.alignment = 'RIGHT'
                row.label(text="X")
                colL = colG.column()
                row = colL.row()
                row.alignment = 'RIGHT'
                row.label(text="Y")
                colL = colG.column()
                row = colL.row()
                row.alignment = 'RIGHT'
                row.label(text="Z")
                colL = colG.column()
                row = colL.row()
                row.alignment = 'RIGHT'
                row.label(text="Dot")
                colL.separator()
                colL = colG.column()
                row = colL.row()
                row.alignment = 'RIGHT'
                row.label(text="Opacity")
                colL.separator(type='LINE')
                                    
                colL = colG.column()
                row = colL.row()
                row.alignment = 'RIGHT'
                row.label(text="Axes Scale")
                colL = colG.column()
                row = colL.row()
                row.alignment = 'RIGHT'
                row.label(text="Axes Length" )
                colL = colG.column()
                row = colL.row()
                row.alignment = 'RIGHT'
                row.label(text="Axes Width")
                                
                colL.separator(type='LINE')
                colL = colG.column()
                row = colL.row()
                row.alignment = 'RIGHT'
                row.label(text="Dot Scale")
                colL = colG.column()
                row = colL.row()
                row.alignment = 'RIGHT'
                row.label(text="Dot Line Width")
                
                # Preset A
                colG = spl.column()
                row = colG.row()
                row.alignment = 'CENTER'
                if self.preset_select:
                    row.label(text="Preset A", icon='CHECKMARK')
                else:
                    row.label(text="Preset A", icon='BLANK1')
                
                row = colG.row(align=True)
                row.prop(self, 'show_axes', text='Axes', toggle=1)
                subrow = row.row(align=True)
                subrow.enabled = prefs.show_axes
                subrow.prop(self, 'axes_gizmo', text="as Gizmo", toggle=1)
                
                row = colG.row(align=True)
                row.prop(self, 'show_dot', text='Dot', toggle=1)
                subrow = row.row(align=True)
                subrow.enabled = prefs.show_dot
                subrow.prop(self, 'dot_gizmo', text="as Gizmo", toggle=1)
                
                colG.separator()
                colG.prop(self, 'use_theme')
                colGA = colG.column()
                colGA.enabled = not prefs.use_theme
                colGA.prop(self, 'axis_x_color', text="")
                colGA.prop(self, 'axis_y_color', text="")
                colGA.prop(self, 'axis_z_color', text="")
                colGA.prop(self, 'dot_color', text="")
                colG.separator()
                colG.prop(self, 'alpha', text="")
                colG.separator(type='LINE')
                                    
                colG.prop(self, 'custom_gizmo_size', text="")
                colG.prop(self, 'arrow_length', text="")
                colG.prop(self, 'arrow_width', text="")
                colG.separator(type='LINE')
                                
                colG.prop(self, 'dot_scale', text="")
                colG.prop(self, 'dot_width', text="")
               
                # Preset G    
                colG = spl.column()
                row = colG.row()
                row.alignment = 'CENTER'
                if self.preset_select:
                    row.label(text="Preset G", icon='BLANK1')
                else:
                    row.label(text="Preset G", icon='CHECKMARK')
                
                row = colG.row(align=True)
                row.prop(self, 'show_axes2', text='Axes', toggle=1)
                subrow = row.row(align=True)
                subrow.enabled = prefs.show_axes2
                subrow.prop(self, 'axes_gizmo2', text="as Gizmo", toggle=1)
                
                row = colG.row(align=True)
                row.prop(self, 'show_dot2', text='Dot', toggle=1)
                subrow = row.row(align=True)
                subrow.enabled = prefs.show_dot2
                subrow.prop(self, 'dot_gizmo2', text="as Gizmo", toggle=1)
                
                colG.separator()
                colG.prop(self, 'use_theme2')
                colGG = colG.column()
                colGG.enabled = not prefs.use_theme2
                colGG.prop(self, 'axis_x_color2', text="")
                colGG.prop(self, 'axis_y_color2', text="")
                colGG.prop(self, 'axis_z_color2', text="")
                colGG.prop(self, 'dot_color2', text="")
                colG.separator()
                colG.prop(self, 'alpha2', text="")
                colG.separator(type='LINE')
                                    
                colG.prop(self, 'custom_gizmo_size2', text="")
                colG.prop(self, 'arrow_length2', text="" )
                colG.prop(self, 'arrow_width2', text="")
                colG.separator(type='LINE')
                                
                colG.prop(self, 'dot_scale2', text="")
                colG.prop(self, 'dot_width2', text="")

            # Save and Load presets and Pie menu config
            row = layout.row()
            row.operator("cursorplus.save_presets", text="Save Config", icon='FILE_TICK')
            row.operator("cursorplus.load_presets", text="Load Config", icon='FILE_PARENT')     


# Keymap Tab   Keymap Tab   Keymap Tab   Keymap Tab   Keymap Tab   Keymap Tab   Keymap Tab                     

        # 3D Cursor Plus Panel location
        elif self.pref_tabs == 'PLUS_KEYMAP':
            wm = bpy.context.window_manager
            kc = wm.keyconfigs.user
            km1 = kc.keymaps.get("3D View")
            km2 = kc.keymaps.get("3D View Tool: Cursor")
                       
            col = box.column()
            col.prop(self, 'use_parent_plus', text="Use Default panel location: Sidebar > View > 3D Cursor ")
            if not context.preferences.addons[__package__].preferences.use_parent_plus:
                col.prop(self, 'category_plus', text="Tab category")
            col.separator(type='LINE')
            
            _label_multiline(context=context, text=txt.ops1, parent=col)
            col.row().prop(self, 'keymap_tabs', expand=True)
            
# General addon Keymap Tab   General addon Keymap Tab   General addon Keymap Tab   General addon Keymap Tab   
            if self.keymap_tabs == 'GENERAL':
                box = layout.box()
                
                # Pie and Preset hotkeys            
                
                # Not enabling the context_pointer_set until the kmi was modified by user gives both ability
                # to restore it to the previous state and to prohibit kmi deletion from addon keymap tab.
            
                colK = box.column()
                row1a = colK.row()
                for kmi in km1.keymap_items:
                    if kmi.idname == "cursorplus.gizmo_presets":
                        if kmi.is_user_modified:
                            row1a.context_pointer_set("keymap", km1) 
                        rna_keymap_ui.draw_kmi([], kc, km1, kmi, row1a, 0)
                row1a.label(text="", icon='UV_SYNC_SELECT')
                            
                colK = box.column()
                row1b = colK.row()
                for kmi in km1.keymap_items:
                    if kmi.name == "3D Cursor Plus Pie":
                        if kmi.is_user_modified:
                            row1b.context_pointer_set("keymap", km1) 
                        rna_keymap_ui.draw_kmi([], kc, km1, kmi, row1b, 0)
                row1b.prop(self, 'edit_pie', text="", icon='MODIFIER_DATA')
        
                # Pie menu customization 
                spacer1_X = 0.55
                spacer2_X = 0.7
                all_X = 1.0
                all_Y = 1.2
                if self.edit_pie:

                    # Top         
                    colK.separator()
                    row = colK.row()
                    row.alignment = 'CENTER'
                    row.scale_x = all_X
                    row.scale_y = all_Y
                    row.prop(self, "pie_top", text="")

                    # Top-Left + Top-Right              
                    colK.separator()
                    row = colK.row()
                    row.alignment = 'CENTER'
                    
                    row.scale_x = all_X
                    row.scale_y = all_Y
                    row.prop(self, "pie_top_left", text="")
                    spacer = row.row()
                    spacer.scale_x = spacer1_X
                    spacer.label(text=" ")
                    row.prop(self, "pie_top_right", text="")

                    # Left + Right            
                    colK.separator()
                    colK.separator()
                    row = colK.row()
                    row.alignment = 'CENTER'
                    row.scale_x = all_X
                    row.scale_y = all_Y
                    row.prop(self, "pie_left", text="")
                    spacer = row.row()
                    spacer.scale_x = spacer2_X
                    spacer.label(text=" ")
                    row.prop(self, "pie_right", text="")

                    # Bottom-Left + Bottom-Right            
                    colK.separator()
                    colK.separator()
                    row = colK.row()
                    row.alignment = 'CENTER'
                    
                    row.scale_x = all_X
                    row.scale_y = all_Y
                    row.prop(self, "pie_bottom_left", text="")
                    spacer = row.row()
                    spacer.scale_x = spacer1_X
                    spacer.label(text=" ")
                    row.prop(self, "pie_bottom_right", text="")

                    # Bottom  
                    colK.separator()
                    row = colK.row()
                    row.alignment = 'CENTER'
                    row.scale_x = all_X
                    row.scale_y = all_Y
                    row.prop(self, "pie_bottom", text="")
                    colK.separator()
                    
    		# Save and Load presets and Pie menu config
                    row = colK.row()
                    row.operator("cursorplus.save_presets", text="Save Config", icon='FILE_TICK')
                    row.operator("cursorplus.load_presets", text="Load Config", icon='FILE_PARENT')

                # Default 3D Cursor related keymap items:    
                layout.label(text="   3D View")
                box = layout.box()
                
                # 'Set 3D Cursor'            
                col2 = box.column()       
                row2 = col2.row()
                for kmi in km1.keymap_items:            
                    if kmi.idname == "view3d.cursor3d":
                        if kmi.is_user_modified:
                            row2.context_pointer_set("keymap", km1)
                        rna_keymap_ui.draw_kmi([], kc, km1, kmi, row2, 0)
                row2.prop(self, 'set_suggest', text="", icon='LIGHT')
                if self.set_suggest:
                    _label_multiline(context=context, text=txt.header0, parent=col2)
                    _label_multiline(context=context, text=txt.set_sug1a, parent=col2)
                    _label_multiline(context=context, text=txt.set_sug2, parent=col2)
                    col2.separator(type='LINE')  
                
                # 'Move 3D Cursor'             
                col3 = box.column()     
                row3 = col3.row()    
                col3sub = row3.column()
                for kmi in km1.keymap_items:                                    
                    if kmi.idname == "transform.translate" and kmi.properties.cursor_transform:
                        if kmi.is_user_modified:
                            col3sub.context_pointer_set("keymap", km1)
                        rna_keymap_ui.draw_kmi([], kc, km1, kmi, col3sub, 0)
                row3.prop(self, 'move_suggest', text="", icon='LIGHT')
                if self.move_suggest:
                    _label_multiline(context=context, text=txt.header0, parent=col3)
                    _label_multiline(context=context, text=txt.move_sug1, parent=col3)
                    _label_multiline(context=context, text=txt.move_sug2, parent=col3)
                    _label_multiline(context=context, text=txt.move_sug3, parent=col3)
               

                layout.label(text="   3D View Tool: Cursor")
                box = layout.box()
                
                # 'Tool: Set 3D Cursor'               
                col4 = box.column()
                row4 = col4.row()       
                for kmi in km2.keymap_items:
                    if kmi.idname == "view3d.cursor3d":
                        if kmi.is_user_modified:
                                row4.context_pointer_set("keymap", km2)
                        rna_keymap_ui.draw_kmi([], kc, km2, kmi, row4, 0)
                row4.prop(self, 'set_suggest2', text="", icon='LIGHT')
                if self.set_suggest2:
                    _label_multiline(context=context, text=txt.header0, parent=col4)
                    _label_multiline(context=context, text=txt.set_sug1b, parent=col4)
                    _label_multiline(context=context, text=txt.set_sug2, parent=col4)
                    col4.separator(type='LINE')

                
                # 'Tool: Move 3D Cursor'    
                col5 = box.column()
                row5 = col5.row()    
                col5sub = row5.column()       
                for kmi in km2.keymap_items:
                    if kmi.idname == "transform.translate" and kmi.properties.cursor_transform:
                        if kmi.is_user_modified:
                                col5sub.context_pointer_set("keymap", km2)
                        rna_keymap_ui.draw_kmi([], kc, km2, kmi, col5sub, 0)
                row5.prop(self, 'move_suggest2', text="", icon='LIGHT')
                if self.move_suggest2:
                    _label_multiline(context=context, text=txt.header0, parent=col5)
                    _label_multiline(context=context, text=txt.move_sug1, parent=col5)
                    _label_multiline(context=context, text=txt.move_sug2, parent=col5)
                    _label_multiline(context=context, text=txt.move_sug3, parent=col5)
            
# PLUS Operators Keymap Tab      PLUS Operators Keymap Tab      PLUS Operators Keymap Tab     

            elif self.keymap_tabs == 'PLUS_OPS':
                box = layout.box()
                # PLUS-Ops shortcuts
                for kmi in reversed(km1.keymap_items):
                    if kmi.idname in plus_ops:
                        colOps = box.column()
                        rowOps = colOps.row()
                        if kmi.is_user_modified:
                            rowOps.context_pointer_set("keymap", km1)
                        rna_keymap_ui.draw_kmi([], kc, km1, kmi, rowOps, 0)
                        rowOps.label(text="", icon='BLANK1')
            
# Snap Options Keymap Tab       Snap Options Keymap Tab       Snap Options Keymap Tab  

            else:
                box = layout.box()
                # Snap Options shortcuts
                for kmi in km1.keymap_items:
                    if kmi.idname == "cursorplus.align_rotation":
                        colSnap = box.column()
                        rowSnap = colSnap.row()
                        if kmi.is_user_modified:
                            rowSnap.context_pointer_set("keymap", km1)
                        rna_keymap_ui.draw_kmi([], kc, km1, kmi, rowSnap, 0)
                        rowSnap.label(text="", icon='BLANK1')
                        
                snap_icon_mapping = {elem[0]: elem[1] for elem in snap_elements}
                
                for kmi in reversed(km1.keymap_items):
                    if kmi.idname == "cursorplus.toggle_list":
                        colSnap = box.column()
                        rowSnap = colSnap.row()
                        if kmi.is_user_modified:
                            rowSnap.context_pointer_set("keymap", km1)
                        rna_keymap_ui.draw_kmi([], kc, km1, kmi, rowSnap, 0)
                        icon_name = snap_icon_mapping.get(kmi.properties.element, 'BLANK1')
                        rowSnap.label(text="", icon=icon_name)
            
            
                    
# Undo Tab   Undo Tab   Undo Tab   Undo Tab   Undo Tab   Undo Tab   Undo Tab   Undo Tab              
            
        else:                       
            colU = box.column()
            if self.how_it_works:
                spl = colU.split(factor=0.7)
            else:
                spl = colU.split(factor=0.95)
            spl.prop(self, 'plus_undo', text="Use the 3D Cursor Undo")
                    
            if self.how_it_works:
                spl.prop(self, 'how_it_works', text=" ", icon='GHOST_ENABLED', emboss=False)
                colU.separator()
                row = colU.row()
                row.alignment = 'CENTER'
                row.label(text="~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                row = colU.row()
                row.alignment = 'CENTER'
                row.label(text=" ~ << Cursor Taming Ritual >> ~ ")
                row = colU.row()
                row.alignment = 'CENTER'
                row.label(text="~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                row = colU.row()
                row.alignment = 'CENTER'
                row.label(text="1. Summon a ghost.")
                row = colU.row()
                row.alignment = 'CENTER'
                row.label(text="2. Confine it inside the file.")
                row = colU.row()
                row.alignment = 'CENTER'
                row.label(text="3. Cast a spell that mutually ties it with the cursor.")
                row = colU.row()
                row.alignment = 'CENTER'
                row.label(text="~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                row = colU.row()
                row.alignment = 'CENTER'
                row.label(text="From now on, if one of them moves - the other will follow.")
                row = colU.row()
                row.alignment = 'CENTER'
                row.label(text="Thus, you've obtained a haunted Blender file")
                row = colU.row()
                row.alignment = 'CENTER'
                row.label(text="and a ghost, obeying to Undo and Redo operations.")
                row = colU.row()
                row.alignment = 'CENTER'
                row.label(text="Its name is 'x undo'. I hope it won't bother you much.")
                row = colU.row()
                row.alignment = 'CENTER'
                row.label(text="~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                colU.separator()
            else:
                spl.prop(self, 'how_it_works', text="", icon='GHOST_DISABLED', emboss=False)
            colU.separator()

            _label_multiline(context=context, text=txt.undo1, parent=colU)
            colU.label(text="     - 3D Cursor's Location")
            colU.label(text="     - 3D Cursor's Euler Rotation")
            colU.label(text="     - 3D Cursor's Rotation Mode")
            _label_multiline(context=context, text=txt.undo2, parent=colU)
            _label_multiline(context=context, text=txt.undo3, parent=colU)
            _label_multiline(context=context, text=txt.undo4, parent=colU)
            colU.separator()            

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
 
classes = (
    CursorPlusPreferences,
    CURSORPLUS_OT_gizmo_presets,
    CURSORPLUS_OT_gizmo_visibility,
    CURSORPLUS_OT_align_rotation,
)
 
addon_keymap = []

def keymap_reg():
    if not hasattr(bpy.types, "CURSORPLUS_OT_toggle_list"):
        return 0.1
    kc = bpy.context.window_manager.keyconfigs.addon
    km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
    for elem in snap_elements:
        kmi = km.keymap_items.new('cursorplus.toggle_list', 'NONE', 'PRESS')
        kmi.properties.element = elem[0]
        kmi.active = False
        addon_keymap.append((km, kmi))
    return None
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
         
    kc = bpy.context.window_manager.keyconfigs.addon
    km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new('cursorplus.gizmo_presets', 'D', 'PRESS', shift=True, ctrl=True)
    addon_keymap.append((km,kmi))
    
    kmi = km.keymap_items.new('wm.call_menu_pie', 'D', 'PRESS', ctrl=True)
    kmi.properties.name = "CURSORPLUS_MT_cursor_plus_pie"
    addon_keymap.append((km,kmi))
    kmi = km.keymap_items.new('cursorplus.align_rotation', 'NONE', 'PRESS')
    kmi.active = False
    addon_keymap.append((km,kmi))
    
    for op in plus_ops:
        kmi = km.keymap_items.new(op, 'NONE', 'PRESS')
        kmi.active = False
        addon_keymap.append((km, kmi))
    
    bpy.app.timers.register(keymap_reg, first_interval = 0.3)
    
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
        
    for km,kmi in addon_keymap:
        km.keymap_items.remove(kmi)
    addon_keymap.clear()