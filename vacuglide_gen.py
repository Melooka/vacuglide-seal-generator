"""VacuGlide seal generator: builds the VacuGlide A seal ring with any inner diameter as STL and/or STEP.

Based on the profile of VacuGlide_A_10mm_38mm_TPU85A_0 (solid of revolution around Z, bottom at z=0).
Changing the inner diameter only moves the inner bead (R4.5) and its bottom chamfer radially;
all other dimensions stay the same (matches the 41 mm version modelled in SolidWorks).

This code was generated with AI (Claude by Anthropic).
"""
import math
import os
import sys

# ---- Geometry (mm) --------------------------------------------------------
BULB_R = 4.5            # radius of the inner bead
BULB_ZC = 4.5           # height of the bead centre
CHAMFER_Z = 1.414       # height where the bottom chamfer meets the bead
CHAMFER_DX = 1.943        # chamfer foot (z=0) offset from bead centre (as in 41 mm version)
TOP_LINE_END = 25.797   # start of the R1.2 fillet above the bead
D_MIN, D_MAX = 20.0, 42.5


def profile(d):
    """Closed profile (r, z) as a list of ('line', p0, p1) / ('arc', p0, pm, p1)."""
    cx = d / 2 + BULB_R                      # bead centre (radial)
    dz = BULB_ZC - CHAMFER_Z
    cham_top = (cx - math.sqrt(BULB_R ** 2 - dz ** 2), CHAMFER_Z)
    cham_foot = (cx - CHAMFER_DX, 0.0)
    bulb_mid = (cx - BULB_R, BULB_ZC)        # innermost point = inner diameter / 2
    bulb_end = (cx, BULB_ZC + BULB_R)        # top, tangent into the top face
    return [
        ('line', (30.64666, 4.7), (31.34659, 4.7)),
        ('line', (31.34659, 4.7), (31.30501, 5.001)),
        ('line', (31.30501, 5.001), (31.78872, 5.1)),
        ('arc', (31.78872, 5.1), (33.11399, 6.1), (33.36896, 9.3)),
        ('line', (33.36896, 9.3), (33.07138, 9.8)),
        ('arc', (33.07138, 9.8), (32.13158, 11.9), (31.7632, 13.5)),
        ('line', (31.7632, 13.5), (31.70682, 14.0)),
        ('line', (31.70682, 14.0), (31.63747, 15.0)),
        ('line', (31.63747, 15.0), (32.73735, 15.0)),
        ('arc', (32.73735, 15.0), (33.20105, 14.68815), (33.2373, 14.5)),
        ('line', (33.2373, 14.5), (33.92345, 12.4)),
        ('line', (33.92345, 12.4), (35.31474, 8.2)),
        ('line', (35.31474, 8.2), (35.31474, 2.4)),
        ('line', (35.31474, 2.4), (34.10851, 1.2)),
        ('line', (34.10851, 1.2), (32.91501, 0.0)),
        ('line', (32.91501, 0.0), cham_foot),
        ('line', cham_foot, cham_top),
        ('arc', cham_top, bulb_mid, bulb_end),
        ('line', bulb_end, (TOP_LINE_END, 9.0)),
        ('arc', (TOP_LINE_END, 9.0), (26.84844, 9.62032), (26.99505, 10.12888)),
        ('line', (26.99505, 10.12888), (26.99706, 14.3)),
        ('arc', (26.99706, 14.3), (27.24004, 14.83028), (27.67624, 15.0)),
        ('line', (27.67624, 15.0), (29.11756, 15.0)),
        ('line', (29.11756, 15.0), (29.75428, 5.9)),
        ('arc', (29.75428, 5.9), (30.14923, 5.2), (30.31333, 5.1)),
        ('line', (30.31333, 5.1), (30.7045, 5.001)),
        ('line', (30.7045, 5.001), (30.64666, 4.7)),
    ]


def build_solid(d):
    from OCP.gp import gp_Pnt, gp_Ax1, gp_Dir
    from OCP.GC import GC_MakeArcOfCircle, GC_MakeSegment
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire, BRepBuilderAPI_MakeFace
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeRevol
    from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
    from OCP.BRepCheck import BRepCheck_Analyzer

    P = lambda q: gp_Pnt(q[0], 0.0, q[1])
    wm = BRepBuilderAPI_MakeWire()
    for el in profile(d):
        if el[0] == 'line':
            curve = GC_MakeSegment(P(el[1]), P(el[2])).Value()
        else:
            curve = GC_MakeArcOfCircle(P(el[1]), P(el[2]), P(el[3])).Value()
        wm.Add(BRepBuilderAPI_MakeEdge(curve).Edge())
    if not wm.IsDone():
        raise RuntimeError("Profile is not closed")
    face = BRepBuilderAPI_MakeFace(wm.Wire(), True).Face()
    solid = BRepPrimAPI_MakeRevol(face, gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 2 * math.pi).Shape()
    u = ShapeUpgrade_UnifySameDomain(solid, True, True, True); u.Build(); solid = u.Shape()
    if not BRepCheck_Analyzer(solid).IsValid():
        raise RuntimeError("Generated solid is invalid")
    return solid


def volume(shape):
    from OCP.GProp import GProp_GProps
    from OCP.BRepGProp import BRepGProp
    g = GProp_GProps(); BRepGProp.VolumeProperties_s(shape, g)
    return g.Mass()


FORMATS = ("STL", "STEP", "STL + STEP")


def export(d, folder, fmt="STL", fine=True):
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.StlAPI import StlAPI_Writer
    from OCP.STEPControl import STEPControl_Writer, STEPControl_AsIs
    from OCP.Interface import Interface_Static
    from OCP.IFSelect import IFSelect_RetDone

    if not (D_MIN <= d <= D_MAX):
        raise ValueError(f"Inner diameter must be between {D_MIN:g} and {D_MAX:g} mm")
    if fmt not in FORMATS:
        raise ValueError(f"Unknown file type: {fmt}")
    solid = build_solid(d)
    name = f"VacuGlide_A_10mm_{d:g}mm_TPU85A_0"
    os.makedirs(folder, exist_ok=True)
    files = []
    if "STL" in fmt:
        stl = os.path.join(folder, name + ".stl")
        BRepMesh_IncrementalMesh(solid, 0.01 if fine else 0.03, False, 0.08 if fine else 0.15, True)
        w = StlAPI_Writer(); w.ASCIIMode = False
        if not w.Write(solid, stl):
            raise RuntimeError("Could not write STL file")
        files.append(stl)
    if "STEP" in fmt:
        Interface_Static.SetCVal_s("write.step.schema", "AP214")
        Interface_Static.SetCVal_s("write.step.unit", "MM")
        sw = STEPControl_Writer(); sw.Transfer(solid, STEPControl_AsIs)
        sp = os.path.join(folder, name + ".step")
        if sw.Write(sp) != IFSelect_RetDone:
            raise RuntimeError("Could not write STEP file")
        files.append(sp)
    return files, volume(solid)


DEFAULT_FOLDER = os.environ.get("VACUGLIDE_OUT") or os.path.join(os.path.expanduser("~"), "Documents", "VacuGlide")


def gui():
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox

    root = tk.Tk(); root.title("VacuGlide-Generator"); root.resizable(False, False)
    f = ttk.Frame(root, padding=14); f.grid()
    ttk.Label(f, text="Inner diameter (mm):").grid(row=0, column=0, sticky="w")
    dvar = tk.StringVar(value="38")
    only_num = (root.register(lambda s: all(c in "0123456789.," for c in s)), "%P")
    ent = ttk.Entry(f, textvariable=dvar, width=10, validate="key", validatecommand=only_num)
    ent.grid(row=0, column=1, sticky="w", padx=6)
    ent.focus(); ent.select_range(0, "end"); ent.icursor("end")
    ent.bind("<FocusIn>", lambda e: ent.select_range(0, "end"))
    ttk.Label(f, text=f"allowed: {D_MIN:g} – {D_MAX:g} mm", foreground="gray").grid(row=0, column=2, sticky="w")
    ttk.Label(f, text="File type:").grid(row=1, column=0, sticky="w", pady=(8, 0))
    tvar = tk.StringVar(value=FORMATS[0])
    ttk.Combobox(f, textvariable=tvar, values=FORMATS, state="readonly", width=12).grid(row=1, column=1, sticky="w", padx=6, pady=(8, 0))
    ttk.Label(f, text="Save to:").grid(row=2, column=0, sticky="w", pady=(8, 0))
    fvar = tk.StringVar(value=DEFAULT_FOLDER)
    ttk.Entry(f, textvariable=fvar, width=46).grid(row=2, column=1, columnspan=2, sticky="we", padx=6, pady=(8, 0))
    ttk.Button(f, text="…", width=3, command=lambda: fvar.set(filedialog.askdirectory(initialdir=fvar.get()) or fvar.get())).grid(row=2, column=3, pady=(8, 0))
    status = ttk.Label(f, text="", foreground="gray"); status.grid(row=4, column=0, columnspan=4, sticky="w", pady=(8, 0))

    def run(*_):
        try:
            d = float(dvar.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Error", "Please enter a number, e.g. 41 or 39.5"); return
        status.config(text="Generating …"); root.update()
        try:
            files, vol = export(d, fvar.get(), tvar.get())
        except Exception as e:
            status.config(text=""); messagebox.showerror("Error", str(e)); return
        status.config(text=f"Done: Ø{d:g} mm, volume {vol / 1000:.2f} cm³")
        messagebox.showinfo("Done", "Created:\n" + "\n".join(os.path.basename(x) for x in files) + f"\n\nin {fvar.get()}")

    ttk.Button(f, text="Generate", command=run).grid(row=3, column=0, columnspan=4, pady=(12, 0))
    root.bind("<Return>", run)
    root.mainloop()


if __name__ == "__main__":
    if len(sys.argv) > 1:   # command line: vacuglide_gen.py <diameter> [folder] [STL|STEP|"STL + STEP"]
        d = float(sys.argv[1].replace(",", "."))
        files, vol = export(d, sys.argv[2] if len(sys.argv) > 2 else DEFAULT_FOLDER,
                            sys.argv[3] if len(sys.argv) > 3 else "STL")
        print("\n".join(files), f"\nVolume: {vol:.1f} mm3")
    else:
        gui()
