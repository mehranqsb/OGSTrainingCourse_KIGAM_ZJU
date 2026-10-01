# SPDX-FileCopyrightText: Copyright (c) OpenGeoSys Community (opengeosys.org)
# SPDX-License-Identifier: BSD-3-Clause

# %%
"""Mesh generator for the TRM heater (HE) tunnel problem.

Adapted from the Kirsch example's ``mesh_tunnel.MeshGenerator``: the same
transfinite quarter-model topology, with the ring between the inner and
outer arc meshed as a separate material group (bentonite) from the
surrounding rock (clay). All dimensions are supplied by the caller (the
notebook's "Model parameters" cell).
"""

from pathlib import Path

import gmsh
import math
import ogstools as ot
import pyvista as pv


# %%
class MeshGenerator:
    """Transfinite quarter model of a lined circular opening.

    Geometry: quarter disc ring (bentonite buffer) between
    ``tunnel_radius_i`` and ``tunnel_radius_i + tunnel_radius_o``, embedded
    in a rectangular rock domain (clay). Physical groups: ``bentonite``,
    ``clay``, ``bottom``, ``left``, ``right``, ``top``, ``arc_inner``,
    ``arc_outer``.
    """

    def __init__(
        self,
        gmsh_model,
        *,
        tunnel_radius_i,
        tunnel_radius_o,
        width,
        height,
        width_m,
        height_m,
        tunnel_center_x=0.0,
        tunnel_center_y=0.0,
        lc=1.0,
        n_transfinite=21,
        n_ring=11,
    ):
        self.gmsh_model = gmsh_model

        if not gmsh.isInitialized():
            gmsh.initialize()

        self.out_dir = None

        geo = gmsh.model.geo
        tunnel_radius = tunnel_radius_i + tunnel_radius_o

        # Entities keyed by tag, same layout as the Kirsch example.
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
            geo.mesh.setTransfiniteCurve(c[tag], n_transfinite, "Progression", 1)

        # Radial curves across the buffer ring.
        for tag in (1, 10, 15):
            geo.mesh.setTransfiniteCurve(c[tag], n_ring, "Progression", 1)

        for tag in range(1, 8):
            geo.mesh.setTransfiniteSurface(s[tag])
            geo.mesh.setRecombine(2, s[tag])

        # --- Material and boundary groups ---
        # Ring sectors (0-45 deg and 45-90 deg) form the bentonite buffer.
        self.bentonite_surfaces = [s[1], s[7]]
        self.clay_surfaces = [s[tag] for tag in (2, 3, 4, 5, 6)]
        self.bottom_boundary = [c[tag] for tag in (1, 2, 3)]
        self.left_boundary = [c[tag] for tag in (8, 9, 10)]
        self.right_boundary = [c[tag] for tag in (4, 5)]
        self.top_boundary = [c[tag] for tag in (6, 7)]
        self.arc_inner_boundary = [c[tag] for tag in (17, 18)]
        self.arc_outer_boundary = [c[tag] for tag in (19, 20)]

        self.gmsh_model.geo.synchronize()

    def generate_meshes(self, out_dir="", order=1):
        self.out_dir = Path(out_dir)
        if not self.out_dir.exists():
            self.out_dir.mkdir(parents=True)

        gmsh.option.setNumber("Mesh.Algorithm", 5)
        gmsh.option.setNumber("Mesh.Format", 1)

        # Generate a linear Gmsh mesh first. OGS creates an order-2 mesh
        # below because NodeReordering cannot process Gmsh's higher-order
        # output.
        gmsh.option.setNumber("Mesh.ElementOrder", 1)
        self.gmsh_model.mesh.generate(2)

        self.gmsh_model.removePhysicalGroups()
        # Two material groups: MaterialIDs 0 (bentonite) and 1 (clay).
        self.gmsh_model.addPhysicalGroup(
            2, self.bentonite_surfaces, 1, name="bentonite"
        )
        self.gmsh_model.addPhysicalGroup(2, self.clay_surfaces, 2, name="clay")

        self.gmsh_model.addPhysicalGroup(1, self.bottom_boundary, name="bottom")
        self.gmsh_model.addPhysicalGroup(1, self.left_boundary, name="left")
        self.gmsh_model.addPhysicalGroup(1, self.right_boundary, name="right")
        self.gmsh_model.addPhysicalGroup(1, self.top_boundary, name="top")
        self.gmsh_model.addPhysicalGroup(
            1, self.arc_inner_boundary, name="arc_inner"
        )
        self.gmsh_model.addPhysicalGroup(
            1, self.arc_outer_boundary, name="arc_outer"
        )

        bulk_mesh_name = Path(self.out_dir, "domain.vtu")
        gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
        mesh_file_name = Path(self.out_dir, "domain.msh")
        gmsh.write(str(mesh_file_name))

        meshes = ot.Meshes.from_gmsh(mesh_file_name)

        vtu_names = []
        for name, mesh in meshes.items():
            print(f"{name}: {mesh.n_cells} cells")
            if "physical_group_" in name:
                group = name.replace("physical_group_", "")
                # Material groups are part of the bulk mesh (MaterialIDs);
                # only boundary groups are written as subdomain meshes.
                if group in ("bentonite", "clay"):
                    continue
                vtu_name = Path(self.out_dir, f"{group}.vtu")
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

        ot.cli().identifySubdomains(
            "-m",
            bulk_mesh_name,
            f"-o {self.out_dir}/",
            "-f",
            "-s 1e-6",
            "--",
            *vtu_names,
        )
