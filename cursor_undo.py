# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Core idea is to create a ghost-like empty, leave it in Blender's objects and protect it from 
# purging with 'fake user'. Then tie it with the cursor, forcing both of them to copy each other's 
# transformations. Even if the ghost is not present in any scenes it still can have location, 
# rotation, and rotation mode. So, what the user actually undoes is the transformation of the ghost,
# and the cursor is forced to repeat after it.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

import bpy
import math
from mathutils import Vector
from bpy.props import EnumProperty 
from bpy.app.handlers import persistent

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

cursor_changed = False  
cursor_still = False
cursor_returned = False
orig_set_from_edit = False
allow_ghost = False
st_loc = (0, 0, 0)
st_rot = (0, 0, 0)
st_rot_q = (1, 0, 0, 0)
st_rot_a = (0, 0, 1, 0)
st_rot_m = None
stored_name = ''

ghost_name = "x undo"
toler = 0.0001

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def toggleUndo(self, context):
    prefs = context.preferences.addons[__package__].preferences    
    if prefs.plus_undo:
        bpy.app.timers.register(initUndo, first_interval = 0.1)
    else:
        terminateUndo()

def redraw_area():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                with bpy.context.temp_override(area=area):
                    bpy.context.area.tag_redraw()
    return None 

def compare(v1, v2, size): 
    for i in range(size):
        if not math.isclose(v1[i], v2[i], rel_tol=toler):
            return False  
    return True 

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Main handler. Check if the object changed. Check either the ghost or the cursor has moved first.  
@persistent
def on_cursor_transform(scene):
    global last_loc, last_rot, last_mode, temp_loc, temp_rot, cur_cur_loc, \
            st_loc, st_rot, st_rot_q, st_rot_a, st_rot_m, stored_name, \
            cursor_changed, cursor_still, cursor_returned, orig_set_from_edit

    current_mode = 'OBJECT'
    a_obj = bpy.context.active_object
    if a_obj is not None:
        if a_obj.name != stored_name:
            stored_name = a_obj.name
            st_loc = a_obj.location.copy()
            st_rot_m = a_obj.rotation_mode 
            st_rot = a_obj.rotation_euler.copy() 
            st_rot_q = a_obj.rotation_quaternion.copy()
            st_rot_a = tuple(a_obj.rotation_axis_angle)
            orig_set_from_edit = False

        # Look for a sign of setting the Origin or changing the object rotation while in edit mode
        elif a_obj.mode != 'OBJECT':
            same = compare(a_obj.location, st_loc, 3)
            mode = a_obj.rotation_mode
            if same and mode == st_rot_m:
                if mode == 'AXIS_ANGLE':
                    same = compare(a_obj.rotation_axis_angle, st_rot_a, 4)   
                elif mode == 'QUATERNION':
                    same = compare(a_obj.rotation_quaternion, st_rot_q, 4)
                else:
                    same = compare(a_obj.rotation_euler, st_rot, 3)
            else:
                same = False

            if not same:
                orig_set_from_edit = True
                st_loc = a_obj.location.copy()
                st_rot_m = a_obj.rotation_mode
                st_rot = a_obj.rotation_euler.copy() 
                st_rot_q = a_obj.rotation_quaternion.copy()
                st_rot_a = tuple(a_obj.rotation_axis_angle)

    # Skip if the transformation is already have been detected and you are waitng for it to end    
    if not cursor_changed:
        cursor = bpy.context.scene.cursor    
        ghost = bpy.data.objects.get(ghost_name)
        # Store the first location change of the cursor as an evidance, if it'll snap back to place
        cur_cur_loc = cursor.location.copy()
        
        # Reset the flag if the user quit back to the Object mode or changed the object with Alt+Q
        if orig_set_from_edit:
            a_obj = bpy.context.active_object
            if a_obj is None:
                orig_set_from_edit = False
            elif a_obj.mode == 'OBJECT':
                orig_set_from_edit = False

        if not ghost:
            summon_ghost()
            return  
        # Move cursor to the ghost if the ghost has(= was) moved (only ways are with Undo and Redo)
        if ghost.location != last_loc \
        or ghost.rotation_euler != last_rot \
        or ghost.rotation_mode != last_mode:

            last_loc = ghost.location.copy()
            last_rot = ghost.rotation_euler.copy() 
            last_mode = ghost.rotation_mode

            temp_loc = ghost.location.copy()
            temp_rot = ghost.rotation_euler.copy()

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
            cursor_returned = False
            bpy.app.timers.register(modal_timer, first_interval = 0.3)
            bpy.app.timers.register(transform_timer, first_interval = 0.01)


def modal_timer():   
    global last_loc, last_rot, last_mode, temp_loc, temp_rot, cur_cur_loc, \
            cursor_changed, cursor_still, cursor_returned, orig_set_from_edit, allow_ghost

    scene = bpy.context.scene
    cursor = scene.cursor
    running = bpy.context.window.modal_operators.keys()

    # Do not capture changes until the modal transformation is over
    if 'TRANSFORM_OT_translate' in running \
    or 'TRANSFORM_OT_rotate' in running \
    or 'OBJECT_OT_cursor_plus_snap_combo' in running:
        # If the modal is running, there is no need in transform_timer, so shut it down
        cursor_still = True
        return 0.01

    # Wait for the cursor to stop moving for more than 0.3 secm if needed. By transform_timer()
    if not cursor_still:
        return 0.01

    # Cursor stop detected. Check if it snapped back to where it was before.
    if cursor.location.copy() == last_loc \
    and cursor.rotation_euler.copy() == last_rot \
    and cursor.rotation_mode == last_mode:
        cursor_returned = True
        orig_set_from_edit = False

        # Suppose that it happended because the origin was just set via orientation_to_cursor
        a_obj = bpy.context.active_object
        if a_obj is not None:
            if a_obj.mode == 'EDIT' and compare(a_obj.location, cur_cur_loc, 3):
                orig_set_from_edit = True

    # Update varaibles and move the ghost to the new cursor location
    last_loc = cursor.location.copy()
    last_rot = cursor.rotation_euler.copy()
    last_mode = cursor.rotation_mode 

    temp_loc = cursor.location.copy()
    temp_rot = cursor.rotation_euler.copy()

    redraw_area()

    # Skip moving the ghost if the cursor appeared where it was before
    if not cursor_returned:
        # Poll variable marks the only line where the operator could be called from
        allow_ghost = True          
        bpy.ops.object.plus_ghost_to_cursor(True)

    cursor_changed = False
    allow_ghost = False
    return None


# Slightly smoothing out a non-operator loc/rot change of the 3D Cursor(e.g. via sidebar tab)
def transform_timer(): 
    global temp_loc, temp_rot, cursor_still
    cursor = bpy.context.scene.cursor
    if not cursor_still:
        # Compare current and previous loc and rot every 0.3sec
        if cursor.location.copy() != temp_loc or cursor.rotation_euler.copy() != temp_rot:
            temp_loc = cursor.location.copy()
            temp_rot = cursor.rotation_euler.copy()
            return 0.3    

    cursor_still = True   
    return None 

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

# Operator which user will actually undo and redo. 
class CURSORPLUS_OT_move_ghost_to_cursor(bpy.types.Operator):
    bl_idname = "object.plus_ghost_to_cursor"
    bl_label = "Transform 3D Cursor"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    # Prevent possible issues caused by Shift+R
    @classmethod
    def poll(cls, context):
        global allow_ghost
        return allow_ghost

    def execute(self, contex):
        global last_loc, last_rot, last_mode, cursor_still, orig_set_from_edit

        # Workaround for undo to work in edit mode. Classic mode toggle + hacky undo_push+undo combo.            
        current_mode = 'OBJECT'
        a_obj = bpy.context.active_object
        if a_obj is not None:
            current_mode = a_obj.mode
            if current_mode == 'EDIT':
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.ed.undo_push(message="Transform 3D Cursor(Mesh)")
                bpy.ops.ed.undo()
                if orig_set_from_edit:
                    bpy.ops.ed.redo()

                bpy.ops.object.mode_set(mode='EDIT')
                orig_set_from_edit = False

        ghost = bpy.data.objects.get(ghost_name)
        if not ghost:
            bpy.data.objects.new(ghost_name, None)
            ghost = bpy.data.objects.get(ghost_name) 
            ghost.use_fake_user = True

        ghost.location = last_loc
        ghost.rotation_euler = last_rot
        ghost.rotation_mode = last_mode

        return {'FINISHED'}

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Register with timers and handlers. Helps to wait for proper context to appepar
def initUndo():
    summon_ghost()
    bpy.app.handlers.depsgraph_update_post.append(on_cursor_transform)
    return None

# Create an empty without linking it to any scene. Protect it with 'fake user'
def summon_ghost():
    global last_loc, last_rot, last_mode, temp_loc, temp_rot
    scene = bpy.context.scene
    if not bpy.data.objects.get(ghost_name):     
        bpy.data.objects.new(ghost_name, None)
        cursor = bpy.context.scene.cursor
        last_loc = cursor.location.copy()
        last_rot = cursor.rotation_euler.copy()
        last_mode = cursor.rotation_mode

        temp_loc = cursor.location.copy()
        temp_rot = cursor.rotation_euler.copy()

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
    

