import bpy
from mathutils import Matrix
import math


# Technically, one set of gizmos could handle the job, but user interaction suffered in terms of 
# appearance: the active arrow drifted away from the other gizmo elements, and changing axes caused
# the arrow to become stuck far away with offset until the transformation was over. I had workarounds,
# but they were too bulky and overly complicated. Therefore, I decided to use two sets of gizmos: 
# one for pure looks, and another, mostly invisible, as the real controlers.  

def add_overlay_gizmo_prop():
    if not hasattr(bpy.types.View3DShading, 'show_gizmo_cursor_plus'):
        bpy.types.View3DShading.show_gizmo_cursor_plus = bpy.props.BoolProperty(
            name="Show Cursor Gizmo",
            description="Toggle Gizmo visibility",
            default=True
        )

class CURSORPLUS_GGT_3d_cursor(bpy.types.GizmoGroup):
    bl_idname = "CURSORPLUS_GGT_3d_cursor"
    bl_label = "Gizmo for 3D Cursor"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D', 'PERSISTENT'}

    @classmethod
    def poll(cls, context):
        prefs = context.preferences.addons[__package__].preferences
        use_gizmo = prefs.use_3d_cursor_gizmo
        overlay = context.space_data.overlay
        if prefs.sync_with_3d_cursor:
            show_3dcursor = overlay.show_cursor and overlay.show_overlays
        else:
            show_3dcursor = True
        show_gizmo = context.space_data.shading.show_gizmo_cursor_plus
        return use_gizmo and show_3dcursor and show_gizmo \
            and context.area.type == 'VIEW_3D' and context.mode in {'OBJECT', 'EDIT_MESH'}

    def setup(self, context):
        prefs = context.preferences.addons[__package__].preferences
   
        # Real controlers. Visible only on hover. 
        real_gizmo = [                   
            ('x_inv', 'GIZMO_GT_arrow_3d', (True, False, False)),
            ('y_inv', 'GIZMO_GT_arrow_3d', (False, True, False)),
            ('z_inv', 'GIZMO_GT_arrow_3d', (False, False, True)),
            ('dot_inv', 'GIZMO_GT_move_3d', (False, False, False)) 
        ]
        self.r_gizmo = {}
        for axis, gizmo_type, constraint_axis in real_gizmo:
            gizmo1 = self.gizmos.new(gizmo_type)
            gizmo1.use_tooltip = False
            gizmo1.use_draw_modal = False
            gizmo1.use_draw_hover = True
            gizmo1.line_width = 2
            gizmo1.alpha = 1
            gizmo1.hide_select = False
            self.r_gizmo[axis] = gizmo1
            op = gizmo1.target_set_operator('transform.translate')
            op.constraint_axis = constraint_axis
            op.release_confirm = True
            op.cursor_transform = True
            op.orient_type = 'CURSOR'
        self.r_gizmo['dot_inv'].draw_options = {'FILL_SELECT', 'ALIGN_VIEW'}


        # Visible axes and a dot. Used to provide solid looks of 'gizmo' in all situations.
        visible_axes = [                       
            ('x', 'GIZMO_GT_arrow_3d', (True, False, False)),
            ('y', 'GIZMO_GT_arrow_3d', (False, True, False)),
            ('z', 'GIZMO_GT_arrow_3d', (False, False, True)),
            ('dot', 'GIZMO_GT_move_3d', (False, False, False))
        ]
        self.v_axes = {}
        for axis, gizmo_type, constraint_axis in visible_axes:
            gizmo2 = self.gizmos.new(gizmo_type)
            gizmo2.use_tooltip = False
            gizmo2.color = (0, 0, 0) 
            gizmo2.alpha = 1
            gizmo2.line_width = 2
            gizmo2.hide_select = True
            self.v_axes[axis] = gizmo2
        self.v_axes['dot'].draw_options = {'FILL_SELECT', 'ALIGN_VIEW'}

    def draw_prepare(self, context):
        self.refresh(context)

    def refresh(self, context):
        prefs = context.preferences.addons[__package__].preferences
        theme = context.preferences.themes[0].user_interface
        cursor = context.scene.cursor
        
        if prefs.preset_select:                 #Preset A
            if prefs.use_theme:
                axis_x_color = theme.axis_x
                axis_y_color = theme.axis_y
                axis_z_color = theme.axis_z
                dot_color = theme.gizmo_view_align
            else:            
                axis_x_color = prefs.axis_x_color
                axis_y_color = prefs.axis_y_color
                axis_z_color = prefs.axis_z_color
                dot_color = prefs.dot_color
            
            dot_scale = prefs.dot_scale/100
            dot_width = prefs.dot_width
            dot_gizmo = prefs.dot_gizmo
            custom_gizmo_size = prefs.custom_gizmo_size/100
            arrow_width = prefs.arrow_width
            arrow_length = prefs.arrow_length/100
            axes_gizmo = prefs.axes_gizmo
            alpha = prefs.alpha/100
            show_axes = prefs.show_axes
            show_dot = prefs.show_dot
        
        else:                                   #Preset G
            if prefs.use_theme2:
                axis_x_color = theme.axis_x
                axis_y_color = theme.axis_y
                axis_z_color = theme.axis_z
                dot_color = theme.gizmo_view_align
            else:
                axis_x_color = prefs.axis_x_color2
                axis_y_color = prefs.axis_y_color2
                axis_z_color = prefs.axis_z_color2
                dot_color = prefs.dot_color2
            
            dot_scale = prefs.dot_scale2/100
            dot_width = prefs.dot_width2
            dot_gizmo = prefs.dot_gizmo2
            custom_gizmo_size = prefs.custom_gizmo_size2/100
            arrow_width = prefs.arrow_width2
            arrow_length = prefs.arrow_length2/100
            axes_gizmo = prefs.axes_gizmo2
            alpha = prefs.alpha2/100
            show_axes = prefs.show_axes2
            show_dot = prefs.show_dot2
                         
        real_gizmo = [
            ('x_inv', cursor.matrix @ Matrix.Rotation(math.radians(90), 4, 'Y'), axis_x_color ),
            ('y_inv', cursor.matrix @ Matrix.Rotation(math.radians(-90), 4, 'X'), axis_y_color),
            ('z_inv', cursor.matrix, axis_z_color),
            ('dot_inv', cursor.matrix, dot_color )
        ]
        for axis, matrix, color in real_gizmo:
            gizmo1 = self.r_gizmo[axis]
            gizmo1.matrix_basis = matrix
            if axis == 'dot_inv':
                gizmo1.scale_basis = dot_scale
                gizmo1.line_width = dot_width
                gizmo1.hide_select = not dot_gizmo
            else:
                gizmo1.scale_basis = custom_gizmo_size
                gizmo1.line_width = arrow_width
                gizmo1.length = arrow_length
                gizmo1.hide_select = not axes_gizmo
            # Since use_draw_hover=True, use 'color/alpha' props instead of usual '_highlight'
            gizmo1.color = color
            gizmo1.alpha = 1
            gizmo1.hide = not show_axes
        self.r_gizmo['dot_inv'].hide = not show_dot
  
        
        visible_axes = [
            ('x', cursor.matrix @ Matrix.Rotation(math.radians(90), 4, 'Y'), axis_x_color),
            ('y', cursor.matrix @ Matrix.Rotation(math.radians(-90), 4, 'X'), axis_y_color),
            ('z', cursor.matrix, axis_z_color),
            ('dot', cursor.matrix, dot_color)
        ]
        for axis, matrix, color in visible_axes:
            gizmo2 = self.v_axes[axis]
            gizmo2.matrix_basis = matrix
            if axis == 'dot':
                gizmo2.scale_basis = dot_scale
                gizmo2.line_width = dot_width
            else:
                gizmo2.scale_basis = custom_gizmo_size
                gizmo2.line_width = arrow_width
                gizmo2.length = arrow_length
            gizmo2.hide_select = True
            gizmo2.color = color
            gizmo2.alpha = alpha
            gizmo2.hide = not show_axes
        self.v_axes['dot'].hide = not show_dot
        
        
def draw_gizmo_button(self, context):
    layout = self.layout
    shading = context.space_data.shading
    col = layout.column()
    col.label(text="3D Cursor")
    col.prop(shading, "show_gizmo_cursor_plus", text="Axes/Gizmo")
    col.separator()

# Register the classes
def register():
    add_overlay_gizmo_prop()
    bpy.types.VIEW3D_PT_gizmo_display.prepend(draw_gizmo_button)
    bpy.utils.register_class(CURSORPLUS_GGT_3d_cursor)

# Unregister the classes
def unregister():
    bpy.utils.unregister_class(CURSORPLUS_GGT_3d_cursor)
    bpy.types.VIEW3D_PT_gizmo_display.remove(draw_gizmo_button)
    del bpy.types.View3DShading.show_gizmo_cursor_plus       