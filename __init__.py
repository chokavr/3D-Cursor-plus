import bpy

from . import preset_management
from . import cursor_gizmo
from . import cursor_plus
from . import cursor_undo
from . import preferences


def register():
    preferences.register()
    preset_management.register()
    cursor_gizmo.register()
    cursor_plus.register()
    cursor_undo.register()

def unregister():
    cursor_undo.unregister()
    cursor_plus.unregister()
    cursor_gizmo.unregister()
    preferences.unregister()
    preset_management.unregister()