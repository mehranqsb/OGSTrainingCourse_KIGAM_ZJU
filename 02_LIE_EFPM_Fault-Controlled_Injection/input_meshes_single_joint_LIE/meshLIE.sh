#!/bin/bash

rm -f \#* *~ *.vtu

gmsh geo2d.geo -2 -format msh2 -o mesh.msh
~/build/release/bin/GMSH2OGS -i mesh.msh -o single_fracture_LIE_shifted_.vtu --gmsh2_physical_id
~/build/release/bin/createQuadraticMesh -i single_fracture_LIE_shifted_.vtu -o single_fracture_LIE_shifted.vtu

~/build/release/bin/editMaterialID -i single_fracture_LIE_shifted.vtu -o single_fracture_LIE_shifted.vtu -r -m 0 -n 1
~/build/release/bin/editMaterialID -i single_fracture_LIE_shifted.vtu -o single_fracture_LIE_shifted.vtu -r -m 1 -n 1
~/build/release/bin/editMaterialID -i single_fracture_LIE_shifted.vtu -o single_fracture_LIE_shifted.vtu -r -m 2 -n 0
