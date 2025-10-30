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


def _to_shape(item):
    if item is None:
        return None
    if hasattr(item, "Shape"):
        return item.Shape
    if hasattr(item, "ShapeType") or hasattr(item, "Edges") or hasattr(item, "Faces"):
        return item
    return None

def remove_element_from_object(obj, element_type='Face', index=0):
    if obj is None:
        raise ValueError("obj must be a FreeCAD document object")

    shape = obj.Shape

    if element_type == 'Face':
        items = list(shape.Faces)
    elif element_type == 'Edge':
        items = list(shape.Edges)
    elif element_type == 'Vertex':
        items = list(shape.Vertexes)
    elif element_type == 'Solid':
        items = list(shape.Solids)
    elif element_type == 'Wire':
        items = list(shape.Wires)
    elif element_type == 'Shell':
        items = list(shape.Shells)
    else:
        raise ValueError("element_type must be one of: Face, Edge, Vertex, Solid, Wire, Shell")

    total = len(items)
    if total == 0:
        raise ValueError(f"The shape has no elements of type {element_type}")

    if index < 0 or index >= total:
        raise IndexError(f"{element_type} index out of range. Total: {total}")

    remaining_raw = [i for j, i in enumerate(items) if j != index]
    remaining = []
    for it in remaining_raw:
        s = _to_shape(it)
        if s is not None:
            remaining.append(s)

    if len(remaining) == 0:
        try:
            doc = obj.Document
            doc.removeObject(obj.Name)
            print(f"Removed object {obj.Name} because no remaining {element_type} left.")
            return None
        except Exception:
            raise RuntimeError("No remaining elements and failed to remove object.")

    new_shape = None
    try:
        if element_type == 'Face':
            try:
                shell = Part.Shell(remaining)
                if shell.isValid():
                    if shell.isClosed():
                        new_shape = Part.Solid(shell)
                    else:
                        new_shape = shell
                else:
                    new_shape = Part.makeCompound(remaining)
            except Exception:
                new_shape = Part.makeCompound(remaining)

        elif element_type == 'Edge':
            try:
                wire = Part.Wire(remaining)
                if wire.isValid():
                    new_shape = wire
                else:
                    new_shape = Part.makeCompound(remaining)
            except Exception:
                new_shape = Part.makeCompound(remaining)

        elif element_type == 'Vertex':
            # Vertex -> compound
            new_shape = Part.makeCompound(remaining)

        elif element_type == 'Wire':
            if len(remaining) == 1:
                new_shape = remaining[0]
            else:
                new_shape = Part.makeCompound(remaining)

        elif element_type == 'Shell':
            # remaining are shells -> try compound or single shell
            if len(remaining) == 1:
                new_shape = remaining[0]
            else:
                new_shape = Part.makeCompound(remaining)

        elif element_type == 'Solid':
            # remaining are solids -> compound of solids
            if len(remaining) == 1:
                new_shape = remaining[0]
            else:
                new_shape = Part.makeCompound(remaining)

        else:
            new_shape = Part.makeCompound(remaining)

        if hasattr(new_shape, "isValid") and not new_shape.isValid():
            try:
                new_shape = Part.makeCompound(remaining)
            except Exception as e:
                raise RuntimeError("Failed to construct a valid replacement shape: " + str(e))

    except Exception as e:
        raise RuntimeError("Error while building new shape: " + str(e))

    # Gán shape mới cho object
    obj.Shape = new_shape
    obj.Document.recompute()

    return new_shape

doc = App.newDocument("RemoveDemo")

# Create a box and cylinder
box = Part.makeBox(10, 10, 10)
cyl = Part.makeCylinder(5, 15, App.Vector(10, 0, 0), App.Vector(1, 0, 0))
cyl2 = Part.makeCylinder(5, 20)

obj_box = doc.addObject("Part::Feature", "Box")
obj_box.Shape = box

obj_cyl = doc.addObject("Part::Feature", "Cylinder")
obj_cyl.Shape = cyl

obj_cyl2 = doc.addObject("Part::Feature", "Cylinder")
obj_cyl2.Shape = cyl2

# Make Compound
compound = Part.makeCompound([obj_box.Shape, obj_cyl.Shape, obj_cyl2.Shape])
obj_comp = doc.addObject("Part::Feature", "Compound")
obj_comp.Shape = compound

output_path = os.path.join('./output', "before.FCStd")
App.ActiveDocument.saveAs(output_path)

remove_element_from_object(obj_comp, element_type='Solid', index=1)
print("Removed first Solid from Compound")

# remove_element_from_object(obj_cyl, element_type='Face', index=0)
# print("Removed first Face from Cylinder")

output_path = os.path.join('./output', "after.FCStd")
App.ActiveDocument.saveAs(output_path)

print(len(obj_comp.Shape.Solids))
print(obj_comp.Shape.Solids[0].ShapeType)



