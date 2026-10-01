# SPDX-FileCopyrightText: Copyright (c) OpenGeoSys Community (opengeosys.org)
# SPDX-License-Identifier: BSD-3-Clause

# %%
import os
from pathlib import Path

import gmsh
import math
import ogstools as ot
import pyvista as pv


# %%
class MeshGenerator:
    """Mesh generator for tunnel_2d_geo_2.geo.

    Geometry: 15 points, 7 transfinite quadrilateral rock surfaces, and an
    optional triangular quarter-disc used to fill the cavern for excavation
    simulations. Physical groups: bottom, left, right, top, and arc.
    """

    def __init__(
        self,
        gmsh_model,
        lc=1,
        tunnel_radius_i=6.5,
        tunnel_radius_o=5,
        tunnel_center_x=0,
        tunnel_center_y=-857.0,
        width=70,
        height=70,
        width_m=35,
        height_m=35,
    ):
        self.gmsh_model = gmsh_model

        if not gmsh.isInitialized():
            gmsh.initialize()

        self.out_dir = None

        geo = gmsh.model.geo
        tunnel_radius = tunnel_radius_i + tunnel_radius_o

        # Entities are keyed by their tags in tunnel_2d_geo_2.geo.
        p, c, cl, s = {}, {}, {}, {}

        # --- Points ---
        coords = {
            0: (tunnel_center_x, tunnel_center_y),
            1: (tunnel_radius_i, tunnel_center_y),
            2: (width, tunnel_center_y),
            3: (width, height + tunnel_center_y),
            4: (0.0, height + tunnel_center_y),
            5: (0.0, tunnel_radius_i + tunnel_center_y),
            6: (width_m, tunnel_center_y),
            7: (width_m, height_m + tunnel_center_y),
            8: (0.0, height_m + tunnel_center_y),
            9: (width, height_m + tunnel_center_y),
            10: (height_m, height + tunnel_center_y),
            11: (
                tunnel_radius_i * math.cos(math.pi / 4),
                tunnel_radius_i * math.cos(math.pi / 4) + tunnel_center_y,
            ),
            12: (tunnel_radius, tunnel_center_y),
            13: (0.0, tunnel_radius + tunnel_center_y),
            14: (
                tunnel_radius * math.cos(math.pi / 4),
                tunnel_radius * math.cos(math.pi / 4) + tunnel_center_y,
            ),
        }
        for tag, (x, y) in coords.items():
            p[tag] = geo.addPoint(x, y, 0.0, lc, tag)

        # --- Lines ---
        lines = {
            1: (1, 12),
            2: (12, 6),
            3: (6, 2),
            4: (2, 9),
            5: (9, 3),
            6: (3, 10),
            7: (10, 4),
            8: (4, 8),
            9: (8, 13),
            10: (13, 5),
            11: (6, 7),
            12: (7, 9),
            13: (10, 7),
            14: (8, 7),
            15: (11, 14),
            16: (14, 7),
        }
        for tag, (start, end) in lines.items():
            c[tag] = geo.addLine(p[start], p[end], tag)

        # --- Circular arcs (start, centre, end) ---
        arcs = {
            17: (1, 0, 11),
            18: (11, 0, 5),
            19: (12, 0, 14),
            20: (14, 0, 13),
        }
        for tag, (start, centre, end) in arcs.items():
            c[tag] = geo.addCircleArc(p[start], p[centre], p[end], tag)

        # --- Curve loops and surfaces ---
        # A negative tag reverses the curve, exactly as in the .geo file.
        loops = {
            1: [-17, -15, 19, 1],
            2: [-19, -16, 11, 2],
            3: [-11, -12, 4, 3],
            4: [13, 12, 5, 6],
            5: [8, 14, -13, 7],
            6: [9, -20, 16, -14],
            7: [10, -18, 15, 20],
        }
        for tag, curve_tags in loops.items():
            curves = [c[t] if t > 0 else -c[-t] for t in curve_tags]
            cl[tag] = geo.addCurveLoop(curves, tag)
            s[tag] = geo.addPlaneSurface([cl[tag]], tag)

        # --- Optional cavern fill ---
        # These two radial lines and the inner arcs bound the quarter-disc.
        # The surface is written only when generate_meshes(with_cavern=True).
        c[21] = geo.addLine(p[0], p[5], 21)
        c[22] = geo.addLine(p[1], p[0], 22)
        cl[8] = geo.addCurveLoop([c[21], -c[18], -c[17], c[22]], 8)
        self.surface_cavern = geo.addPlaneSurface([cl[8]], 8)
        self.left_cavern_boundary = c[21]
        self.bottom_cavern_boundary = c[22]

        # --- Transfinite quadrilateral mesh ---
        for tag in (
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            11,
            12,
            13,
            14,
            16,
            17,
            18,
            19,
            20,
        ):
            geo.mesh.setTransfiniteCurve(c[tag], 21, "Progression", 1)

        for tag in (1, 10, 15):
            geo.mesh.setTransfiniteCurve(c[tag], 21, "Progression", 1)

        for tag in range(1, 8):
            geo.mesh.setTransfiniteSurface(s[tag])
            geo.mesh.setRecombine(2, s[tag])

        # --- Physical groups from tunnel_2d_geo_2.geo ---
        self.surfaces = [s[tag] for tag in range(1, 8)]
        self.bottom_boundary = [c[tag] for tag in (1, 2, 3)]
        # Curve 10 is also on x=0. It is missing from the source .geo physical
        # group, but belongs to the complete left exterior boundary.
        self.left_boundary = [c[tag] for tag in (8, 9, 10)]
        self.right_boundary = [c[tag] for tag in (4, 5)]
        self.top_boundary = [c[tag] for tag in (6, 7)]
        self.tunnel_boundary = [c[tag] for tag in (17, 18)]

        self.gmsh_model.geo.synchronize()

    def generate_meshes(self, out_dir="", order=1, with_cavern=False):
        self.out_dir = Path(out_dir)
        if not self.out_dir.exists():
            self.out_dir.mkdir(parents=True)

        gmsh.option.setNumber("Mesh.Algorithm", 5)
        gmsh.option.setNumber("Mesh.Format", 1)

        # Generate a linear Gmsh mesh first. OGS creates an order-2 mesh below
        # because NodeReordering cannot process Gmsh's higher-order output.
        gmsh.option.setNumber("Mesh.ElementOrder", 1)
        self.gmsh_model.mesh.generate(2)

        self.gmsh_model.removePhysicalGroups()
        self.gmsh_model.addPhysicalGroup(2, self.surfaces, 1, name="domain")

        # Use copies so repeated calls do not modify the base boundary lists.
        left_boundary = list(self.left_boundary)
        bottom_boundary = list(self.bottom_boundary)
        if with_cavern:
            self.gmsh_model.addPhysicalGroup(
                2, [self.surface_cavern], 2, name="cavern"
            )
            left_boundary.append(self.left_cavern_boundary)
            bottom_boundary.append(self.bottom_cavern_boundary)

        self.gmsh_model.addPhysicalGroup(1, bottom_boundary, name="bottom")
        self.gmsh_model.addPhysicalGroup(1, left_boundary, name="left")
        self.gmsh_model.addPhysicalGroup(1, self.right_boundary, name="right")
        self.gmsh_model.addPhysicalGroup(1, self.top_boundary, name="top")
        self.gmsh_model.addPhysicalGroup(1, self.tunnel_boundary, name="arc")

        bulk_mesh_name = Path(self.out_dir, "domain.vtu")
        gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
        mesh_file_name = Path(self.out_dir, "domain.msh")
        gmsh.write(str(mesh_file_name))

        meshes = ot.Meshes.from_gmsh(mesh_file_name)

        vtu_names = []
        for name, mesh in meshes.items():
            print(f"{name}: {mesh.n_cells} cells")
            if "physical_group_" in name:
                vtu_name = Path(
                    self.out_dir, f"{name.replace('physical_group_', '')}.vtu"
                )
            else:
                vtu_name = Path(self.out_dir, f"{name}.vtu")
            vtu_names.append(vtu_name)
            pv.save_meshio(vtu_name, mesh)

        ot.cli().NodeReordering("-i", bulk_mesh_name, "-o", bulk_mesh_name)
        if order == 2:
            files_to_process = {bulk_mesh_name, *vtu_names}
            for vtu_file_name in files_to_process:
                print(f"Create quadratic mesh for {vtu_file_name}")
                ot.cli().createQuadraticMesh(
                    "-i", vtu_file_name, "-o", vtu_file_name
                )

        # identifySubdomains treats -o as a filename prefix, not a directory.
        # A trailing separator keeps the output inside out_dir instead of
        # writing "<out_dir>arc.vtu" next to it.
        ot.cli().identifySubdomains(
            "-m",
            bulk_mesh_name,
            "-o",
            f"{self.out_dir}{os.sep}",
            "-f",
            "-s 1e-6",
            "--",
            *vtu_names,
        )


# %%
if __name__ == "__main__":
    gmsh.initialize(readConfigFiles=False)
    gmsh.model.add("tunnel_2d_geo_2")
    generator = MeshGenerator(gmsh.model)
    generator.generate_meshes(out_dir="input_meshes_tunnel")
    gmsh.finalize()
