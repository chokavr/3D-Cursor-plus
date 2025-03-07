# Axes / Gizmo
If you ever wanted to see the cursor's axes more clearly or have a gizmo for easier manipulation, here they are. You'll have two separate presets; use any or both, and toggle between them with a shortcut, a button on a panel, or a pie menu. Adjust them to fit your needs: change colors and sizes, choose the desired behavior for each preset, define visibility in separate areas, link with the 3D cursor, or use it instead of the cursor.

![AxesGizmo](https://github.com/user-attachments/assets/2bc9c224-a024-4406-b36c-13cd0e38dee9)

# Undo
If enabled, makes undo and redo work for your 3D cursor too.
For the sake of simplicity, this function only considers changes in these three parameters: Cursor's Location, Euler Rotation and Rotation Mode.
Changes in its Quaternion and Axis Rotations are ignored due to their redundancy, cursor-wise. Change detection has a tiny (~0.3 sec) delay to filter out unnecessary transformations. So, if you attempt a 'rapid' cursor placement (more than 3 per second), probably only the last one will be detected.
This limitation does not apply to Undo and Redo operations themselves.

![Undo](https://github.com/user-attachments/assets/9a8a4f08-d52a-4cf9-b80d-578c8655a048)

# Cursor Related Operators
PLUS Operators are intended to streamline your workflow by providing easy access to default Blender operators that have been slightly tweaked to work with reference to the 3D Cursor. They work both in 'Object' and 'Edit' modes, 
and some of the operators have modifiers that can alter their default behavior if 'SHIFT' or 'ALT' is held prior to calling them.

## Snap To (with Op Modifiers)
Move your 3D cursor with the 'Snap' option enabled and a separate 'Snap List', independent from your global snap options.

* Tweak Snapping: You can choose elements to snap via panel, pie menu, or shortcuts, and enable or disable 'Aligning Rotation to Target'.
* SHIFT: temporarily invert the current rotation mode.
* ALT: snap with the cursor's rotation reset.
  
![SnapTo](https://github.com/user-attachments/assets/ea880df9-9e9d-4508-83f7-7edc5c4c7ddb)

## Move
Move the selection along the 3D cursor's axis. The default is the Z axis.

![Move](https://github.com/user-attachments/assets/14829af8-a7aa-41cb-92f1-f54b938c34c7)

## Rotate
Pivot the selection around the 3D cursor.

![Rotate](https://github.com/user-attachments/assets/372c6115-a131-41a2-b1f2-5d8fec8d263f)

## Scale
Scale the selection using the 3D cursor as a transform point.

![Scale](https://github.com/user-attachments/assets/bda83967-b187-4ec9-b061-dc3793553412)

## Copy Rotation
Copy the rotation of the 3D cursor to the selected object(s).

![CopyRotation](https://github.com/user-attachments/assets/4ba11e29-df60-4c59-a8d2-5236eb44c4e6)

## Reset 3D Cursor (with Op Modifiers)
Clear the 3D cursor's rotation, location, or both, and even 'Frame All' after that. Clearing both is the default action.

* SHIFT: Reset only rotation.
* ALT: Reset only location.
* SHIFT+ALT: Call the built-in 'Center Cursor and Frame All' function (default Blender shortcut - Shift+C).
 
![ResetCursor](https://github.com/user-attachments/assets/12cff5d5-2906-4950-91ff-c79033b4910b)

## Override (with Op Modifiers)
Override the current Transform Orientation and/or Pivot Point to 'Cursor'.
It is possible to assign to the pie menu a callable 'Override' panel with 3 separate buttons, or to use the 'Override' as a single button with two available modifiers:
* SHIFT: Override Transform Orientation.
* ALT: Override Pivot Point.
* By default, it will do both.

![OverRide](https://github.com/user-attachments/assets/f6856341-48ef-4c88-b7b9-6707ae17b909)

