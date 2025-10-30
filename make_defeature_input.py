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
# Save Output
# ==========================================
def save_output(doc, filename):
    """Save result to ./output directory."""
    os.makedirs("./output", exist_ok=True)
    out_path = os.path.join("./output", filename)
    doc.saveAs(out_path)
    print(f"File saved: {out_path}")
    return out_path

# -----------------------------
# File paths
# -----------------------------
input_file = "DATA/input.step"
output_file_fcstd = "input_with_extra.FCStd"
output_file_step = "DATA/input_with_extra.step"

# -----------------------------
# Load the original STEP file
# -----------------------------
doc = App.newDocument("DefeaturePrep")
original_shape = Part.read(input_file)

# Add original shape to document
obj_original = doc.addObject("Part::Feature", "OriginalShape")
obj_original.Shape = original_shape
doc.recompute()

# -----------------------------
# Add small “extra” solids for defeature
# -----------------------------
# small box
small_box = Part.makeBox(1, 1, 1)
small_box.Placement.Base = App.Vector(0, 3, -1)
obj_small = doc.addObject("Part::Feature", "SmallBox")
obj_small.Shape = small_box

# small cylinder
small_cyl = Part.makeCylinder(0.5, 1.0)
small_cyl.Placement.Base = App.Vector(3, 3, -1)
obj_cyl = doc.addObject("Part::Feature", "SmallCylinder")
obj_cyl.Shape = small_cyl

doc.recompute()

# -----------------------------
# Combine everything into one compound
# -----------------------------
compound_shape = Part.makeCompound([obj_original.Shape, obj_small.Shape, obj_cyl.Shape])
obj_compound = doc.addObject("Part::Feature", "CompoundForDefeature")
obj_compound.Shape = compound_shape
doc.recompute()

# -----------------------------
# Optional: filter small faces/solids for reference
# -----------------------------
faces = obj_compound.Shape.Faces
solids = obj_compound.Shape.Solids

print("Total faces:", len(faces))
print("Faces smaller than area_threshold=2.0:", [f.Area for f in faces if f.Area < 2.0])
print("Total solids:", len(solids))
print("Solids smaller than volume_threshold=1:", [s.Volume for s in solids if s.Volume < 1])

# -----------------------------
# Export to STEP
# -----------------------------
Part.export([obj_compound], output_file_step)
save_output(doc, output_file_fcstd)
print(f"STEP file with extra small features saved: {output_file_step}")
