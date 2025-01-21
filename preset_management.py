import bpy
import json
from bpy.types import AddonPreferences
from bpy.props import StringProperty, EnumProperty 
from bpy_extras.io_utils import ExportHelper, ImportHelper


class CURSORPLUS_OT_save_presets(bpy.types.Operator, ExportHelper):
    bl_idname = "cursorplus.save_presets"
    bl_label = "Save Presets"
    bl_description = "Save Gizmo presets and Pie configuration"
    
    filename_ext = ".json"
    
    filter_glob: StringProperty(
        default='*.json',
        options={'HIDDEN'}
    )
    
    def invoke(self, context, events):
        self.filepath = "3DCursorPlusPrefs.json"
        return super().invoke(context, events)
    
    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        data = {
            "pie_left": prefs.pie_left,
            "pie_right": prefs.pie_right,
            "pie_bottom": prefs.pie_bottom,
            "pie_top": prefs.pie_top,
            "pie_top_left": prefs.pie_top_left,
            "pie_top_right": prefs.pie_top_right,
            "pie_bottom_left": prefs.pie_bottom_left,
            "pie_bottom_right": prefs.pie_bottom_right,
            
            # Preset A
            "show_axes": prefs.show_axes,
            "axes_gizmo": prefs.axes_gizmo,
            "show_dot": prefs.show_dot,
            "dot_gizmo": prefs.dot_gizmo,
            "custom_gizmo_size": prefs.custom_gizmo_size,
            "arrow_length": prefs.arrow_length,
            "arrow_width": prefs.arrow_width,
            "dot_scale": prefs.dot_scale,
            "dot_width": prefs.dot_width,
            
            "use_theme": prefs.use_theme,
            "axis_x_color": list(prefs.axis_x_color),
            "axis_y_color": list(prefs.axis_y_color),
            "axis_z_color": list(prefs.axis_z_color),
            "dot_color": list(prefs.dot_color),
            "alpha": prefs.alpha,
            
            # Preset B
            "show_axes2": prefs.show_axes2,
            "axes_gizmo2": prefs.axes_gizmo2,
            "show_dot2": prefs.show_dot2,
            "dot_gizmo2": prefs.dot_gizmo2,
            "custom_gizmo_size2": prefs.custom_gizmo_size2,
            "arrow_length2": prefs.arrow_length2,
            "arrow_width2": prefs.arrow_width2,
            "dot_scale2": prefs.dot_scale2,
            "dot_width2": prefs.dot_width2,
            
            "use_theme2": prefs.use_theme2,
            "axis_x_color2": list(prefs.axis_x_color2),
            "axis_y_color2": list(prefs.axis_y_color2),
            "axis_z_color2": list(prefs.axis_z_color2),
            "dot_color2": list(prefs.dot_color2),
            "alpha2": prefs.alpha2,
        }
        
        # Save to JSON file
        with open(self.filepath, 'w') as f:
            json.dump(data, f, indent=4)

        self.report({'INFO'}, "Preferences saved to JSON.")
        return {'FINISHED'}


class CURSORPLUS_OT_load_presets(bpy.types.Operator, ImportHelper):
    bl_idname = "cursorplus.load_presets"
    bl_label = "Load Presets"
    bl_description = "Load Gizmo presets and Pie configuration"
    
    filename_ext = ".json"
    
    filter_glob: StringProperty(
        default='*.json',
        options={'HIDDEN'}
    )
    
    def invoke(self, context, events):
        self.filepath = "3DCursorPlusPrefs.json"
        return super().invoke(context, events)
   
    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        
        # Load from JSON file
        try:
            with open(self.filepath, 'r') as f:
                data = json.load(f)
                        
                # Update the properties
                prefs.pie_left = data.get("pie_left", "MOVECURSOR")
                prefs.pie_right = data.get("pie_right", "MOVE")
                prefs.pie_bottom = data.get("pie_bottom", "ROTATE")
                prefs.pie_top = data.get("pie_top", "SCALE")
                prefs.pie_top_left = data.get("pie_top_left", "TWEAK")
                prefs.pie_top_right = data.get("pie_top_right", "OVER")
                prefs.pie_bottom_left = data.get("pie_bottom_left", "PRESET")
                prefs.pie_bottom_right = data.get("pie_bottom_right", "CLEAR")
                
                # Preset A
                prefs.show_axes = data.get("show_axes", True)
                prefs.axes_gizmo = data.get("axes_gizmo", False)
                prefs.show_dot = data.get("show_dot", True)
                prefs.dot_gizmo = data.get("dot_gizmo", False)
                
                prefs.custom_gizmo_size = data.get("custom_gizmo_size", 5)
                prefs.arrow_length = data.get("arrow_length", 600)
                prefs.arrow_width = data.get("arrow_width", 2.5)
                prefs.dot_scale = data.get("dot_scale", 14)
                prefs.dot_width = data.get("dot_width", 3.5)
                
                prefs.use_theme = data.get("use_theme", False)
                prefs.axis_x_color = data.get("axis_x_color", (1.0, 0.211766, 0.325486))
                prefs.axis_y_color = data.get("axis_y_color", (0.541176, 0.85883, 0.0))
                prefs.axis_z_color = data.get("axis_z_color", (0.172551, 0.560786, 1.0))
                prefs.dot_color = data.get("dot_color", (0.0, 0.0, 0.0))
                prefs.alpha = data.get("alpha", 100)
                
                # Preset G
                prefs.show_axes2 = data.get("show_axes2", True)
                prefs.axes_gizmo2 = data.get("axes_gizmo2", True)
                prefs.show_dot2 = data.get("show_dot2", True)
                prefs.dot_gizmo2 = data.get("dot_gizmo2", True)
                
                prefs.custom_gizmo_size2 = data.get("custom_gizmo_size2", 100)
                prefs.arrow_length2 = data.get("arrow_length2", 100)
                prefs.arrow_width2 = data.get("arrow_width2", 2.0)
                prefs.dot_scale2 = data.get("dot_scale2", 14)
                prefs.dot_width2 = data.get("dot_width2", 2.0)
                
                prefs.use_theme2 = data.get("use_theme2", True)
                prefs.axis_x_color2 = data.get("axis_x_color2", (1.0, 0.211766, 0.325486))
                prefs.axis_y_color2 = data.get("axis_y_color2", (0.541176, 0.85883, 0.0))
                prefs.axis_z_color2 = data.get("axis_z_color2", (0.172551, 0.560786, 1.0))
                prefs.dot_color2 = data.get("dot_color2", (1.0, 1.0, 1.0))
                prefs.alpha2 = data.get("alpha2", 60)

                 
            self.report({'INFO'}, "Presets loaded successfully.")
            return {'FINISHED'}
        except FileNotFoundError:
            self.report({'ERROR'}, f"File not found: {self.filepath}")
            return {'CANCELLED'}
        except json.JSONDecodeError:
            self.report({'ERROR'}, "Error decoding JSON.")
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"An error occurred: {str(e)}")
            return {'CANCELLED'}    
        # Load from JSON file
        with open(self.filepath, 'r') as f:
            data = json.load(f)

classes = (
    CURSORPLUS_OT_save_presets,
    CURSORPLUS_OT_load_presets,
)
  
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
  
    
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)