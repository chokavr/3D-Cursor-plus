# Core idea is to create a ghost-like empty, leave it in Blender's objects and protect it from purging with
# 'fake user'. Then tie it with the cursor, forcing both of them to copy each other's transformations. Even
# if the ghost is not present in any scenes it still can have location, rotation, and rotation mode. So, what
# the user actually undoes is the transformation of the ghost, and the cursor is forced to repeat after it.

import bpy
from mathutils import Vector
from bpy.app.handlers import persistent

cursor_changed = False  
cursor_still = False

ghost_name = "x undo"


def toggleUndo(self, context):
    prefs = context.preferences.addons[__package__].preferences    
    if prefs.plus_undo:
        bpy.app.timers.register(initUndo, first_interval = 0.1)
    else:
        terminateUndo()


# Main handler. Check if the ghost moved first, if it is still - check the cursor.  
@persistent
def on_cursor_transform(scene):
    global last_loc, last_rot, last_mode, cursor_changed, cursor_still
    # Skip if transformation is already have been detected and are waitng for it to end
    if not cursor_changed:
        cursor = bpy.context.scene.cursor    
        ghost = bpy.data.objects.get(ghost_name)
        if not ghost:
            summon_ghost()
            return  
        # Move cursor to ghost if ghost was moved (only ways are with Undo and Redo)
        if ghost.location != last_loc \
        or ghost.rotation_euler != last_rot \
        or ghost.rotation_mode != last_mode:
            last_loc = ghost.location.copy()
            last_rot = ghost.rotation_euler.copy()
            last_mode = ghost.rotation_mode
            cursor.location = last_loc
            cursor.rotation_euler = last_rot
            cursor.rotation_mode = last_mode
            return
        # Start checking if transformation is over if cursor moved.        
        if cursor.location.copy() != last_loc \
        or cursor.rotation_euler.copy() != last_rot \
        or cursor.rotation_mode != last_mode:
            cursor_changed = True
            cursor_still = False
            bpy.app.timers.register(modal_timer, first_interval = 0.3)
            bpy.app.timers.register(transform_timer, first_interval = 0.01)


def modal_timer():   
    global last_loc, last_rot, last_mode, cursor_changed, cursor_still
    running = bpy.context.window.modal_operators.keys()
    # Do not capture changes until the modal transformation is over
    if 'TRANSFORM_OT_translate' in running or 'TRANSFORM_OT_rotate' in running:
        cursor_still = True
        return 0.01
    # Wait for cursor to stop moving for more than 0.3 sec. Covered by transform_timer()
    if not cursor_still:
        return 0.01  
    # Cursor stop detected. Update varaibles and move the ghost to the new cursor's location.
    scene = bpy.context.scene
    cursor = bpy.context.scene.cursor
    ghost = bpy.data.objects.get(ghost_name)        
    last_loc = cursor.location.copy()
    last_rot = cursor.rotation_euler.copy()
    last_mode = cursor.rotation_mode           
    # Use temp_override to ensure that operator runs in the correct context  
    for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'VIEW_3D':
                    with bpy.context.temp_override(area=area):
                        bpy.context.area.tag_redraw()
    bpy.ops.object.plus_ghost_to_cursor(True)
    cursor_changed = False
    return None   


# Slightly smoothing out a non-operator loc/rot change of the 3D Cursor(e.g. via sidebar tab)
def transform_timer(): 
    global last_loc, last_rot, cursor_still
    cursor = bpy.context.scene.cursor
    if not cursor_still:
        if cursor.location.copy() != last_loc or cursor.rotation_euler.copy() != last_rot:
            last_loc = cursor.location.copy()
            last_rot = cursor.rotation_euler.copy()        
            return 0.3    
    cursor_still = True   
    return None 


# Operator which user will actually undo and redo. 
class CURSORPLUS_OT_move_ghost_to_cursor(bpy.types.Operator):
    bl_idname = "object.plus_ghost_to_cursor"
    bl_label = "Transform 3D Cursor"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, contex):
        global last_loc, last_rot, last_mode
        current_mode = 'OBJECT'
        active_object = bpy.context.active_object
        # Workaround for undo to work in edit mode. Classic mode toggle + hacky undo_push+undo combo. 
        if active_object is not None:
            current_mode = active_object.mode
            if current_mode == 'EDIT':
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.ed.undo_push(message="Transform 3D Cursor(Edit)")
                bpy.ops.ed.undo()
                
        ghost = bpy.data.objects.get(ghost_name)
        if not ghost:
            return
        ghost.location = last_loc
        ghost.rotation_euler = last_rot
        ghost.rotation_mode = last_mode
        if active_object and current_mode == 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')
        return {'FINISHED'}


# Register with timers and handlers. Helps to wait for proper context to appepar
def initUndo():
    summon_ghost()
    bpy.app.handlers.depsgraph_update_post.append(on_cursor_transform)
    return None
    
# Create an empty without linking it to any scene. Protect with 'fake user'
def summon_ghost():
    global last_loc, last_rot, last_mode
    scene = bpy.context.scene
    if not bpy.data.objects.get(ghost_name):     
        bpy.data.objects.new(ghost_name, None)
    cursor = bpy.context.scene.cursor
    last_loc = cursor.location.copy()
    last_rot = cursor.rotation_euler.copy()
    last_mode = cursor.rotation_mode 

    ghost = bpy.data.objects.get(ghost_name) 
    ghost.use_fake_user = True
    ghost.location = last_loc
    ghost.rotation_euler = last_rot
    ghost.rotation_mode = last_mode


def terminateUndo():
    if on_cursor_transform in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(on_cursor_transform)
    ghost = bpy.data.objects.get(ghost_name)
    if ghost: 
        bpy.data.objects.remove(ghost)

# Remove the ghost to not contaminate saved file with unnecessary object 
@persistent
def presave(scene):
    terminateUndo()

@persistent    
def postsave(scene):
    initUndo()
    
    
def register():
    bpy.utils.register_class(CURSORPLUS_OT_move_ghost_to_cursor)
    bpy.app.timers.register(initUndo, first_interval = 0.3)
    bpy.app.handlers.save_pre.append(presave)
    bpy.app.handlers.save_post.append(postsave)
    bpy.app.handlers.save_post_fail.append(postsave)      


def unregister():
    bpy.utils.unregister_class(CURSORPLUS_OT_move_ghost_to_cursor)
    terminateUndo()
    bpy.app.handlers.save_pre.remove(presave)
    bpy.app.handlers.save_post.remove(postsave)
    bpy.app.handlers.save_post_fail.remove(postsave)    

