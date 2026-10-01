# Heated Tunnel Problem — TRM (HE/FE Experiment)

"FE" stands for the Full-scale Emplacement heater experiment at the
Mont Terri rock laboratory (not "finite element").

Coupled THM simulation of a heat-emitting tunnel (bentonite buffer in
Opalinus Clay) with the OpenGeoSys `THERMO_RICHARDS_MECHANICS` process,
following the fully saturated TRM-S case of Pitz et al. (2023), IJRMMS 170,
105534 (DECOVALEX 2023 Task C; the reference paper is included as a PDF).
The workflow mirrors the Kirsch example in `../01_Tunnel_Excavation_Kirsch/`.

## Contents

### Notebook and scripts

- `03_trm_heated_tunnel.ipynb` — main notebook: parameters, mesh and project
  generation, OGS run, temperature/pressure histories and contours.
- `mesh_tunnel_trm.py` — `MeshGenerator`, adapted from the Kirsch example's
  transfinite quarter model: buffer ring (MaterialID 0) and clay
  (MaterialID 1), boundaries `left/right/top/bottom/arc_inner/arc_outer`.
- `prj_trm.py` — `PrjGenerator` for the TRM process (two media, orthotropic
  clay with local coordinate system, heater Neumann BC); all values come
  from the notebook.

### OGS input

- `_prj/trm_tunnel.prj` — generated project file.
- `input_meshes_trm/` — generated quadratic meshes; results are written to `_out/`.

### Model summary

Quarter of a 50 m × 50 m domain; heater surface at r = 0.525 m, tunnel wall
at R = 1.24 m. Heater heat flux 89 W/m² on `arc_inner`; rollers on all outer
boundaries; heater surface fixed; hydraulic/thermal boundaries otherwise
natural. Initial state: 15 °C, zero pore pressure, fully saturated. Heating
phase of 5 years; SparseLU (scaled) direct solver.

### Legacy files

- `legacy_thm/` — earlier THERMO_HYDRO_MECHANICS project files, runs,
  and meshes that this notebook-based TRM workflow replaces.

## How to run

Open `03_trm_heated_tunnel.ipynb` in Jupyter (requires `ogstools`, `gmsh`, `pyvista`,
and OGS). Running all cells regenerates the meshes and project file, runs
OGS into `_out/`, and produces the result plots.
