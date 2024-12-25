# Axes / Gizmo
Customize two presets for different looks or behaviors of your 3D cursor's gizmo. Toggle between them using a shortcut, a button on a panel, or the Quick Favorites menu. Change visibility, colors, and other parameters.

#  Undo
Allows you to undo/redo your 3D cursor's transformation.
For the sake of simplicity, this function only considers changes in these three parameters:
* 3D Cursor's location
* 3D Cursor's Euler Rotation
* 3D Cursor's Rotation Mode

Changes in its Quaternion and Axis Rotations are ignored due to their redundancy, cursor-wise.
Change detection has a tiny (~0.3sec) delay to filter out unnecessary transformations. So, if you attempt a 'rapid' cursor placement (more than 3 per sec), probably only the last one will be detected.
This limitation does not apply to Undo and Redo operations themselves.

#  Cursor related operators
PLUS Operators are intended to be accessed from a Pie menu and do not have their own 
dedicated shortcuts. However, if you want to have them or to add an operator to 'Quick Favourites', you can easily do so by right-clicking the desired button on the 3D Cursor Plus panel at the sidebar. Blender considers adding a shortcut as a change in 'Preferences'. Although 'Auto-Save Preferences' is enabled by default, if you've turned it off, make sure to press 'Save Preferences' manually.

## Snap to
Move your 3D cursor with the 'Snap' option enabled and a separate 'Snap List'.

**Tweak Snapping:** Choose elements to snap to and enable or disable aligning the cursor's rotation with the snapping target.

## Move 
Move the selection along the 3D cursor's axis. The default is the Z axis.

## Rotate 
Pivot the selection around the 3D cursor.

## Scale 
Scale the selection using the 3D cursor as a transform point.

## Copy Rotation 
Copy the rotation of the 3D cursor to the selected object(s).

## Clear Rotation 
Clear the 3D cursor's rotation

## Override
Override the current Transform Orientation and/or Pivot Point to 'Cursor'
