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

# ==========================================
# Import CAD File
# ==========================================
def import_cad_file(file_path):
    """
    Import a CAD file (.STEP, .IGES, .STL) and return FreeCAD document + object.
    """
    doc = App.newDocument("AutomationProcess")

    ext = os.path.splitext(file_path)[-1].lower()
    if ext in ['.step', '.stp', '.iges', '.igs']:
        shape = Part.read(file_path)
        obj = doc.addObject("Part::Feature", "ImportedShape")
        obj.Shape = shape

    elif ext == '.stl':
        import Mesh
        mesh = Mesh.Mesh(file_path)
        obj = doc.addObject("Mesh::Feature", "ImportedMesh")
        obj.Mesh = mesh
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    doc.recompute()
    print(f"Imported CAD file: {file_path}")
    return doc, obj


# ==========================================
# Cut Solid (Boolean Cut)
# ==========================================
def cut_solids(solid_a, solid_b, doc):
    """
    Perform boolean cut (A - B) and return result object.
    """
    result_shape = solid_a.Shape.cut(solid_b.Shape)
    result_obj = doc.addObject("Part::Feature", "CutResult")
    result_obj.Shape = result_shape
    doc.recompute()
    print("Cut operation complete")
    return result_obj


# ==========================================
# Defeaturing
# ==========================================
def defeature_object(obj, area_threshold=1.0, volume_threshold=None):
    """
    Remove small faces or solids below given thresholds.
    - area_threshold: remove faces smaller than this ()
    - volume_threshold: remove solids smaller than this ()
    """
    shape = obj.Shape

    if hasattr(shape, "Solids") and len(shape.Solids) > 1 and volume_threshold:
        kept_solids = [s for s in shape.Solids if s.Volume > volume_threshold]
        if not kept_solids:
            raise RuntimeError("All solids smaller than threshold, cannot defeature.")
        simplified_shape = Part.makeCompound(kept_solids)
        print(f"Removed solids < {volume_threshold} ")
    else:
        faces = [f for f in shape.Faces if f.Area > area_threshold]
        if not faces:
            raise RuntimeError("All faces smaller than threshold, cannot defeature.")
        simplified_shape = Part.makeSolid(Part.makeShell(faces))
        print(f"Removed faces < {area_threshold}")

    simplified_obj = obj.Document.addObject("Part::Feature", "Defeatured")
    simplified_obj.Shape = simplified_shape
    obj.Document.recompute()
    print("Defeaturing complete")
    return simplified_obj


# ==========================================
# Save Output
# ==========================================
def save_output(doc, filename):
    """Save result to ./output directory."""
    os.makedirs("./output", exist_ok=True)
    out_path = os.path.join("./output", filename)
    doc.saveAs(out_path)
    print(f"File saved: {out_path}")
    return out_path


# ==========================================
#  MAIN PIPELINE
# ==========================================
if __name__ == "__main__":
    INPUT_FILE = "DATA/input_with_extra.step"

    # === Step 1: Import CAD ===
    doc, imported_obj = import_cad_file(INPUT_FILE)

    # === Step 2: Create a cutting box ===
    box_obj = doc.addObject("Part::Box", "CutBox")
    box_obj.Length = 10
    box_obj.Width = 10
    box_obj.Height = 10
    box_obj.Placement.Base = App.Vector(5, 5, 5)
    doc.recompute()

    # === Step 3: Cut solid ===
    cut_obj = cut_solids(imported_obj, box_obj, doc)

    # === Step 4: Defeaturing (area < 2.0  or volume < 1 ) ===
    defeatured_obj = defeature_object(cut_obj, area_threshold=2.0, volume_threshold=1)

    # === Step 5: Save output ===
    save_output(doc, "AutomationResult.FCStd")

    print("Automation pipeline finished successfully!")
