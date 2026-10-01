# Tunnel Excavation Problem — Kirsch Benchmark (OGS)

Self-contained materials for the tunnel convergence problem solved with the
release nodal force approach in OpenGeoSys, verified against the analytical
Kirsch solution.

## Contents

### Notebook and scripts

- `01_tunnel_excavation_kirsch.ipynb` — executed main notebook: mesh generation, project setup,
  OGS runs (release vs. standard approach, linear vs. quadratic elements),
  automated verification checks, and comparison with the Kirsch solution.
- `prj_tunnel.py` — `PrjGenerator` class that generates `kirsch.prj` with the
  ogstools `Project` API (in-situ stress, `ReleaseNodalForce` BC, decay
  function, time loop); used as `from prj_tunnel import PrjGenerator`.
- `mesh_tunnel.py` — gmsh-based mesh generator (`MeshGenerator`) for the
  quarter model (domain + boundary meshes), linear or quadratic elements.

### OGS input

- `kirsch.prj` — generated OGS project file (release nodal force setup).
- `input_meshes_linear/`, `input_meshes_quadratic/` — domain and boundary
  meshes (`domain`, `left`, `right`, `top`, `bottom`, `arc`) for both
  element orders.

### Documents

- `report/kirsch_release_nodal_force_report.pdf` — complete course report with
  the plane-strain derivation, Kirsch solution, weak-form and release-force
  formulation, OGS setup, numerical verification, and postprocessing guidance
  (`report/kirsch_release_nodal_force_report.tex` is the canonical source).
- `release_nodal_force_bc.pdf` and `release_nodal_force_bc.tex` — root-level
  compatibility copies/entry point for the report above.
- `kirsch_notebook.pdf` — PDF rendering of the executed notebook.

## Build the course report

The report uses the bundled TUBAF report class, fonts, cover, and course logos.
With TeX Live installed, build from the repository root:

```text
latexmk -pdf release_nodal_force_bc.tex
```

To rebuild the canonical PDF, run `latexmk -pdf
kirsch_release_nodal_force_report.tex` from `report/`.

## Model summary

Quarter model of a circular tunnel, radius 6.5 m, plane strain, linear
elasticity. The tension-positive initial stress is (0, -20, -6, 0) MPa, where
the -6 MPa out-of-plane component enforces the compatible plane-strain state.
Symmetry is imposed on the left and bottom; the right boundary is
traction-free. Excavation is simulated by releasing the
equivalent nodal forces on the tunnel wall (`arc`) with a linear time-decay
f(t) = 1 - t/t_e over t_e = 2 d = 1.728e5 s (f = 0 afterward).

## How to run

Python 3.11 or newer is required. The simplest setup is the same on macOS,
Windows PowerShell, and Linux:

```text
python -m venv .venv
```

Activate the environment:

- macOS/Linux: `source .venv/bin/activate`
- Windows PowerShell: `.venv\Scripts\Activate.ps1`
- Windows Command Prompt: `.venv\Scripts\activate.bat`

Then install the notebook dependencies and the OGS executable wheel:

```text
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m ipykernel install --user --name kirsch-ogs --display-name "Kirsch OGS"
python -m jupyter lab
```

Open `01_tunnel_excavation_kirsch.ipynb`, select the **Kirsch OGS** kernel, and run all cells. The
notebook regenerates the meshes and project file, runs all variants, and
produces comparisons with the analytical Kirsch solution. Generated paths use
`pathlib`, and OGS discovery supports both `ogs` on macOS/Linux and `ogs.exe`
on Windows.

Normally Jupyter starts in this repository. If it does not, set
`KIRSCH_PROJECT_ROOT` to the repository's absolute path before starting
Jupyter. `OGS_TESTRUNNER_OUT_DIR` can optionally select another output
directory. If OGS is installed separately and is not on `PATH`, pass either
its executable or its containing directory as `ogs_path` to `runBenchmark()`.

The executed course version was verified with OpenGeoSys 6.5.9.
