ops1 = "     PLUS Operators are intended to be accessed from a Pie menu and do not have their own \
dedicated shortcuts. However, if you want to have them or to add an operator to 'Quick Favorites', \
you can easily do so by right-clicking the desired button on the 3D Cursor Plus panel at the sidebar. \
New shortcuts will appear here. Worth mentioning that Blender considers assigning a shortcut as a \
change in 'Preferences'. Although 'Auto-Save Preferences' is enabled by default, if you have turned \
it off, make sure to manually press 'Save Preferences'."


header0 = " Recommended tweaks:"

set_sug1a = "    1. Mouse event: PRESS -> CLICK/RELEASE.  If you've ever tried to move your 3D Cursor \
along any axis using 'Shift + drag-RMB' + 'X/Y/Z', you've found out that it doesn't work as expected. \
In order to initiate a 'Shift + drag-RMB' event you inevitably start with PRESSING, and \
'Shift + press-RMB' is the shortcut that places the 3D Cursor under your mouse cursor. Thus, the movement \
with 'Axis Lock' starts from a new and irrelevant point. Changing the mouse event to 'CLICK' or \
'RELEASE' allows you to avoid triggering this function and to start moving the cursor from its current \
position. If you're not a big fan of gizmos, this tweak might give you more control over the 3D Cursor. \
And you will still be able to place the cursor with a single click." 

set_sug1b = "    1. Mouse event: PRESS -> CLICK/RELEASE.  If you've ever tried to move your 3D Cursor \
along any axis using 'drag-LMB' + 'X/Y/Z', you've found out that it doesn't work as expected. \
In order to initiate a 'drag-LMB' event you inevitably start with PRESSING, and \
'press-LMB' is the shortcut that places the 3D Cursor under your mouse cursor. Thus, the movement \
with 'Axis Lock' starts from a new and irrelevant point. Changing the mouse event to 'CLICK' or \
'RELEASE' allows you to avoid triggering this function and to start moving the cursor from its current \
position. If you're not a big fan of gizmos, this tweak might give you more control over the 3D Cursor. \
And you will still be able to place the cursor with a single click." 

set_sug2 = "    2. Orientation: View -> Geometry / Transform.  Default 'View' orientation doesn't \
bring much benefit, while 'Geometry' works like 'Snap to Face' + 'Align Rotation to Target' and, \
basically, creates an easily accessible custom orientation. In combination with 'PLUS Ops' and \
'Override' options, it might significantly speed up your modeling workflow."


move_sug1 = "   1. Orientation: Cursor.  Basically, it adds a second option to the 'Axis Lock' mode when \
you move your cursor and press 'X', 'Y' or 'Z' twice. If you're not a gizmo user, you might find this \
tweak pretty convenient for moving the 3D Cursor along its own axes without having to switch \
'Transformation Orientation' modes back and forth."

move_sug2 = "   2. Use Snapping Options = 'Enabled'. 'Vertex'(+ Edge Center, or your choice).   How often do you \
need to move your cursor without snapping it to any type of geometry? In most cases, instead of \
pressing 'Shift+S' - 'Snap to Selected' you can simply use 'Snap' with 'Vertex' option selected, \
and directly move the cursor where you want it to be. But what if you work with grids and increments, or \
don't want to constantly change 'Snap' options just to place the cursor? You can enable it by default \
ONLY for the cursor. And it will have its own separate list of elements to snap, which you can customize \
to fit your needs. It will complement the 'Snap 3D Cursor' PLUS operator, that has the same \
functionality, and grant you even more control at cursor placement."

move_sug3 = "   3. Snap Base. Click to enable and chose any option except 'Active'.   If 'Active' \
is enabled in your global 'Snap Base' options, and you have an object selected (or while in 'Edit mode'), \
and your cursor is not at this object's origin, attempting to move and snap the cursor somewhere \
will result in it snapping with an offset equal to the distance between the cusor and objects' origin point. \
It's a specific situation, but not so rare, and we can easily prevent it from happening with two clicks."


undo1 = " 1. For the sake of simplicity, this function only considers changes in these three parameters:"
undo2 = " 2. Changes in its Quaternion and Axis Rotations are ignored due to their redundancy, cursor-wise."
undo3 = " 3. Change detection has a tiny (~0.3sec) delay to filter out unnecessary transformations. So, if \
you attempt a 'rapid' cursor placement (more than 3 per sec), probably only the last one will be detected."
undo4 = " 4. This limitation does not apply to Undo and Redo operations themselves. "