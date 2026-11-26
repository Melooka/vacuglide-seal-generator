# VacuGlide Seal Generator

Generates the **VacuGlide** seal ring (TPU 85A) with any inner diameter as **STL** (for 3D printing) and/or **STEP** (real CAD geometry for SolidWorks etc.).

> **Note:** The code in this repository was generated with AI (Claude by Anthropic), based on my own seal design. Check the generated parts before use.

**Credits:** The seal design is based on a design by [iambriansloan](https://www.reddit.com/user/iambriansloan/).

The part is a solid of revolution. Changing the inner diameter moves only the inner bead (R4.5) and its bottom chamfer; all other dimensions stay the same:

| | |
|---|---|
| Outer diameter | 70.6 mm |
| Height | 15 mm |
| Inner diameter | 20 – 42.5 mm (default 38 mm) |

Above 42.5 mm the bead would run into the R1.2 fillet of the inner wall, so larger sizes need a different profile.

## Setup (Windows)

```powershell
py -3.12 -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Usage

**GUI**

```powershell
.\venv\Scripts\pythonw.exe vacuglide_gen.py
```

Enter the inner diameter, choose the file type (`STL`, `STEP` or `STL + STEP`), pick the output folder and click **Generate**.

**Command line**

```powershell
.\venv\Scripts\python.exe vacuglide_gen.py <inner diameter> [output folder] [STL|STEP|"STL + STEP"]
.\venv\Scripts\python.exe vacuglide_gen.py 39.5 . "STL + STEP"
```

Output files are named `VacuGlide_A_10mm_<d>mm_TPU85A_0.stl/.step`.
The default output folder is `Documents\VacuGlide`; set the environment variable `VACUGLIDE_OUT` to change it.
