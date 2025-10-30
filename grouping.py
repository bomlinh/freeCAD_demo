import sys
import os

# ==========================================
# Setup FreeCAD environment (in case of MacOS only)
# ==========================================
FREECAD_LIB_PATH = "/Applications/FreeCAD.app/Contents/Resources/lib"
SITE_PACKAGES_PATH = "/Applications/FreeCAD.app/Contents/Resources/lib/python3.11/site-packages"

if FREECAD_LIB_PATH not in sys.path:
    sys.path.append(FREECAD_LIB_PATH)
if SITE_PACKAGES_PATH not in sys.path:
    sys.path.append(SITE_PACKAGES_PATH)

import FreeCAD as App
import Part

HAS_GUI = hasattr(App, "GuiUp") and App.GuiUp
if HAS_GUI:
    import FreeCADGui as Gui
    print("FreeCAD is running with GUI mode.")
else:
    print("Running in headless mode (no GUI).")

doc = App.newDocument("GroupingAutomation")

box = Part.makeBox(10, 10, 10)
cyl = Part.makeCylinder(5, 15)
sphere = Part.makeSphere(6)

obj_box = doc.addObject("Part::Feature", "Box")
obj_box.Shape = box

obj_cyl = doc.addObject("Part::Feature", "Cylinder")
obj_cyl.Shape = cyl

obj_sphere = doc.addObject("Part::Feature", "Sphere")
obj_sphere.Shape = sphere

obj_box.Placement.Base = App.Vector(0, 0, 0)
obj_cyl.Placement.Base = App.Vector(15, 0, 0)
obj_sphere.Placement.Base = App.Vector(30, 0, 0)

group = doc.addObject("App::DocumentObjectGroup", "MyGroup")
group.addObject(obj_box)
group.addObject(obj_cyl)
group.addObject(obj_sphere)

doc.recompute()
if HAS_GUI:
    Gui.ActiveDocument.ActiveView.fitAll()

output_path = os.path.join('./output', "grouping.FCStd")
App.ActiveDocument.saveAs(output_path)

print(f"Grouping automation completed successfully!")
print(f"Saved to: {output_path}")
