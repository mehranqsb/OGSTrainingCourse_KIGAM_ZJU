#!/bin/bash

rm -f \#* *~ *.vtu

gmsh geo2d.geo -2 -format msh2 -o mesh.msh
~/build/release/bin/GMSH2OGS -i mesh.msh -o double_fracture_EFP_shifted_.vtu --gmsh2_physical_id
~/build/release/bin/createQuadraticMesh  -i double_fracture_EFP_shifted_.vtu -o double_fracture_EFP_shifted.vtu

~/build/release/bin/editMaterialID -i double_fracture_EFP_shifted.vtu -o double_fracture_EFP_shifted.vtu -r -m 0 -n 0
~/build/release/bin/editMaterialID -i double_fracture_EFP_shifted.vtu -o double_fracture_EFP_shifted.vtu -r -m 1 -n 1
~/build/release/bin/editMaterialID -i double_fracture_EFP_shifted.vtu -o double_fracture_EFP_shifted.vtu -r -m 2 -n 0
~/build/release/bin/editMaterialID -i double_fracture_EFP_shifted.vtu -o double_fracture_EFP_shifted.vtu -r -m 3 -n 1
~/build/release/bin/editMaterialID -i double_fracture_EFP_shifted.vtu -o double_fracture_EFP_shifted.vtu -r -m 4 -n 0
