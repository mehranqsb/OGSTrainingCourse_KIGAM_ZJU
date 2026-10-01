##!/bin/bash

rm -f *_ts_* *.pvd *~ \#*
# mkdir -p ./out_ortho_LTRB_PardisoLU
# mkdir -p ./out_ortho_LTRB_SparseLU
# mkdir -p ./out_ortho_LTRB_BiCGSTAB_ILUT
# mkdir -p ./out_ortho_LTRB
mkdir -p ./out_ortho_LTRB_GMRES_ILUT

# OMP_NUM_THREADS=12 OGS_ASM_THREADS=12 ~/build/release/bin/ogs -o out_ortho_LTRB_PardisoLU tunnel_ortho_LTRB_90_roller_PardisoLU.prj > ./out_ortho_LTRB_PardisoLU/out.txt
# OMP_NUM_THREADS=12 OGS_ASM_THREADS=12 ~/build/release/bin/ogs -o out_ortho_LTRB_BiCGSTAB_ILUT tunnel_ortho_LTRB_90_roller_BiCGSTAB_ILUT.prj > ./out_ortho_LTRB_BiCGSTAB_ILUT/out.txt
# ogs -o out_ortho_LTRB_SparseLU tunnel_ortho_LTRB_90_roller_SparseLU.prj > ./out_ortho_LTRB_SparseLU/out.txt
OMP_NUM_THREADS=12 OGS_ASM_THREADS=12 ~/build/release/bin/ogs -o out_ortho_LTRB_GMRES_ILUT tunnel_ortho_LTRB_90_roller_GMRES_ILUT.prj > ./out_ortho_LTRB_GMRES_ILUT/out.txt
