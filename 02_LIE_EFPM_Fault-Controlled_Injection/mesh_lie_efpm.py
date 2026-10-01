# SPDX-License-Identifier: BSD-3-Clause
"""Unified Python mesh generator for the LIE/EFPM benchmark."""

from pathlib import Path

import gmsh
import ogstools as ot

try:
    from .input_meshes_single_joint_LIE.mesh_generator import SingleJointLIEMesh
    from .input_meshes_single_joint_EFP.mesh_generator import SingleJointEFPMMesh
    from .input_meshes_two_joints_LIE.mesh_generator import TwoJointsLIEMesh
    from .input_meshes_two_joints_EFP.mesh_generator import TwoJointsEFPMMesh
except ImportError:
    from input_meshes_single_joint_LIE.mesh_generator import SingleJointLIEMesh
    from input_meshes_single_joint_EFP.mesh_generator import SingleJointEFPMMesh
    from input_meshes_two_joints_LIE.mesh_generator import TwoJointsLIEMesh
    from input_meshes_two_joints_EFP.mesh_generator import TwoJointsEFPMMesh


_CASES = {
    ("LIE", 1): (
        SingleJointLIEMesh,
        "SingleFractureMedium/LIE",
        "single_fracture_LIE_shifted",
        {0: 1, 1: 1, 2: 0},
    ),
    ("EFPM", 1): (
        SingleJointEFPMMesh,
        "SingleFractureMedium/EFP",
        "single_fracture_EFP_shifted",
        {0: 0, 1: 1, 2: 0},
    ),
    ("LIE", 2): (
        TwoJointsLIEMesh,
        "DoubleFractureMedium/LIE",
        "double_fracture_LIE_shifted",
        {0: 2, 1: 2, 2: 2, 3: 0, 4: 1},
    ),
    ("EFPM", 2): (
        TwoJointsEFPMMesh,
        "DoubleFractureMedium/EFP",
        "double_fracture_EFP_shifted",
        {0: 0, 1: 1, 2: 0, 3: 1, 4: 0},
    ),
}


class MeshGenerator:
    """Generate one- or two-fracture LIE/EFPM benchmark meshes.

    Gmsh must be initialized and a model must be added before construction,
    following the same lifecycle used by ``mesh_tunnel.MeshGenerator``.
    """

    def __init__(self, gmsh_model, approach="LIE", number_of_fractures=1):
        key = (approach.upper(), number_of_fractures)
        if key not in _CASES:
            raise ValueError(
                "Supported cases are LIE/EFPM with one or two fractures"
            )
        self.gmsh_model = gmsh_model
        self.approach, self.number_of_fractures = key
        generator_class, default_dir, output_stem, material_map = _CASES[key]
        self.default_out_dir = Path(default_dir)
        self.output_stem = output_stem
        self.material_map = material_map
        self.geometry = generator_class(gmsh_model)

    def _register_physical_groups(self):
        self.gmsh_model.removePhysicalGroups()
        geometry = self.geometry
        if self.approach == "EFPM":
            self.gmsh_model.addPhysicalGroup(
                2, geometry.fracture_surface, 101, name="FRACTURE"
            )
            self.gmsh_model.addPhysicalGroup(
                2, geometry.rock_surface, 201, name="ROCK"
            )
            return

        self.gmsh_model.addPhysicalGroup(2, geometry.surfaces, 201, name="ROCK")
        if self.number_of_fractures == 1:
            self.gmsh_model.addPhysicalGroup(
                1, geometry.fracture_boundary, 101, name="FRACTURE"
            )
        else:
            self.gmsh_model.addPhysicalGroup(
                1, geometry.fracture0_boundary, 101, name="FRACTURE0"
            )
            self.gmsh_model.addPhysicalGroup(
                1, geometry.fracture1_boundary, 102, name="FRACTURE1"
            )

    def generate_meshes(self, out_dir=None, order=2):
        """Generate the Gmsh mesh and return the final OGS VTU path."""
        out_dir = self.default_out_dir if out_dir is None else Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        self._register_physical_groups()

        gmsh.option.setNumber("Mesh.Algorithm", 5)
        gmsh.option.setNumber("Mesh.RecombineAll", 1)
        gmsh.option.setNumber("Mesh.ElementOrder", 1)
        gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
        self.gmsh_model.mesh.generate(2)

        msh_file = out_dir / "domain.msh"
        linear_vtu = out_dir / f"{self.output_stem}_.vtu"
        final_vtu = out_dir / f"{self.output_stem}.vtu"
        gmsh.write(str(msh_file))

        ot.cli().GMSH2OGS(
            "-i", msh_file, "-o", linear_vtu, "--gmsh2_physical_id"
        )
        if order == 2:
            ot.cli().createQuadraticMesh("-i", linear_vtu, "-o", final_vtu)
        else:
            final_vtu.write_bytes(linear_vtu.read_bytes())

        for old_id, new_id in self.material_map.items():
            ot.cli().editMaterialID(
                "-i", final_vtu, "-o", final_vtu,
                "-r", "-m", str(old_id), "-n", str(new_id),
            )
        return final_vtu
