# SPDX-FileCopyrightText: Copyright (c) OpenGeoSys Community (opengeosys.org)
# SPDX-License-Identifier: BSD-3-Clause

# %%
"""Project-file generator for the Kirsch ReleaseNodalForce benchmark.

Counterpart of :class:`mesh_tunnel.MeshGenerator` for the OGS project file.
This module defines only the model *structure*; all physical and numerical
parameter values are supplied by the caller (the notebook's "Model
parameters" and "Solver settings" cells).

The generated project reproduces the configuration used by ``01_tunnel_excavation_kirsch.ipynb``:
a quarter model with an initially stressed elastic medium, symmetry
conditions on the left and bottom, vertical far-field traction on the top,
and time-dependent release of the excavation forces on the tunnel arc.
"""

from pathlib import Path

import ogstools as ot


# %%
class PrjGenerator:
    """Create the Kirsch release-nodal-force OGS project file.

    All physical and numerical parameters are set in the constructor; the
    project is assembled and written by :meth:`generate_project`. Mesh file
    names are kept portable (``domain.vtu`` etc.) so the notebook and OGS
    can select the linear or quadratic mesh folder at run time.
    """

    mesh_names = ("domain", "left", "right", "top", "bottom", "arc")

    def __init__(
        self,
        *,
        youngs_modulus,
        poissons_ratio,
        vertical_stress,
        tunnel_radius,
        tunnel_center_y,
        excavation_duration,
        end_time,
        nonlinear_max_iter,
        linear_solver_type,
        preconditioner_type,
        linear_max_iter,
        linear_error_tolerance,
        linear_solver_scaling,
        element_order,
        mesh_dir=Path(),
        petsc_parameters=(
            "-ksp_type bcgs -pc_type bjacobi "
            "-ksp_rtol 1.e-18 -ksp_atol 1.e-18 -ksp_max_it 4000"
        ),
    ):
        if element_order not in (1, 2):
            raise ValueError("element_order must be 1 or 2")

        self.mesh_dir = Path(mesh_dir)
        self.element_order = element_order
        self.youngs_modulus = youngs_modulus
        self.poissons_ratio = poissons_ratio
        self.vertical_stress = vertical_stress
        self.tunnel_radius = tunnel_radius
        self.tunnel_center_y = tunnel_center_y
        self.excavation_duration = excavation_duration
        self.end_time = end_time
        self.nonlinear_max_iter = nonlinear_max_iter
        self.linear_solver_type = linear_solver_type
        self.preconditioner_type = preconditioner_type
        self.linear_max_iter = linear_max_iter
        self.linear_error_tolerance = linear_error_tolerance
        self.linear_solver_scaling = linear_solver_scaling
        self.petsc_parameters = petsc_parameters

        self.prj = None

    # --- Public API -----------------------------------------------------

    def generate_project(self, output_file="kirsch.prj"):
        """Assemble the project and write the ``.prj`` file."""
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        self.prj = ot.Project(output_file=output_file)

        self._add_meshes()
        self._add_process()
        self._add_media()
        self._add_parameters()
        self._add_initial_and_boundary_conditions()
        self._add_time_loop_and_output()
        self._add_solvers()

        self.prj.write_input()
        return self.prj

    # --- Project sections -----------------------------------------------

    def _add_meshes(self):
        for name in self.mesh_names:
            self.prj.mesh.add_mesh(filename=str(self.mesh_dir / f"{name}.vtu"))

    def _add_process(self):
        self.prj.processes.set_process(
            name="SD",
            type="SMALL_DEFORMATION",
            integration_order=4,
            specific_body_force="0 0",
        )
        self.prj.processes.set_constitutive_relation(
            id="*",
            type="LinearElasticIsotropic",
            youngs_modulus="E",
            poissons_ratio="nu",
        )
        self.prj.processes.add_process_variable(
            process_variable="process_variable",
            process_variable_name="displacement",
        )
        self.prj.processes.add_secondary_variable("epsilon", "epsilon")
        self.prj.processes.add_secondary_variable("sigma", "sigma")
        self.prj.add_element(
            parent_xpath="./processes/process",
            tag="initial_stress",
            text="sigma0",
        )

    def _add_media(self):
        self.prj.media.add_property(
            medium_id="*",
            phase_type="Solid",
            name="density",
            type="Constant",
            value=0.0,
        )

    def _add_parameters(self):
        parameters = self.prj.parameters
        parameters.set_constant_parameter(name="E", value=self.youngs_modulus)
        parameters.set_constant_parameter(name="nu", value=self.poissons_ratio)
        parameters.set_constant_parameter(name="zero", value=0.0)
        parameters.set_constant_parameter(
            name="initial_displacement", values="0 0"
        )

        # In-situ stress: uniaxial vertical compression outside the tunnel
        # radius. SMALL_DEFORMATION stores the 2D stress tensor as
        # [sigma_xx, sigma_yy, sigma_zz, sigma_xy]. For plane strain the
        # initial out-of-plane stress must satisfy epsilon_zz = 0, hence
        # sigma_zz = nu * (sigma_xx + sigma_yy).
        radial_distance = f"sqrt(x^2 + (y + {-self.tunnel_center_y})^2)"
        initial_vertical_stress = (
            f"if ({radial_distance}>{self.tunnel_radius}) "
            f"{-self.vertical_stress}; else 0.0"
        )
        initial_out_of_plane_stress = (
            f"if ({radial_distance}>{self.tunnel_radius}) "
            f"{-self.poissons_ratio * self.vertical_stress}; else 0.0"
        )
        parameters.set_function_parameter(
            name="sigma0",
            expression=[
                "0.0",
                initial_vertical_stress,
                initial_out_of_plane_stress,
                "0.0",
            ],
        )
        parameters.set_constant_parameter(
            name="sigma_top", value=-self.vertical_stress
        )

        # Time-decay function f(t) of the ReleaseNodalForce BC.
        parameters.set_function_parameter(
            name="decay_function",
            expression=(
                f"if (t>{self.excavation_duration}) 0.0; "
                f"else 1 - t/{self.excavation_duration}"
            ),
        )

    def _add_initial_and_boundary_conditions(self):
        self.prj.process_variables.set_ic(
            process_variable_name="displacement",
            components=2,
            order=self.element_order,
            initial_condition="initial_displacement",
            compensate_non_equilibrium_initial_residuum="true",
        )

        add_bc = self.prj.process_variables.add_bc
        add_bc(
            process_variable_name="displacement",
            type="Dirichlet",
            mesh="left",
            component=0,
            parameter="zero",
        )
        add_bc(
            process_variable_name="displacement",
            type="Dirichlet",
            mesh="bottom",
            component=1,
            parameter="zero",
        )
        add_bc(
            process_variable_name="displacement",
            type="Neumann",
            mesh="top",
            component=1,
            parameter="sigma_top",
        )

        # ogstools 0.8.1 does not yet expose ReleaseNodalForce through
        # add_bc(), so add this supported OGS block through the generic
        # project API.
        self.prj.add_block(
            blocktag="boundary_condition",
            parent_xpath=(
                './process_variables/process_variable[name="displacement"]/'
                "boundary_conditions"
            ),
            taglist=["mesh", "type", "time_decay_parameter"],
            textlist=["arc", "ReleaseNodalForce", "decay_function"],
        )

    def _add_time_loop_and_output(self):
        self.prj.time_loop.add_process(
            process="SD",
            nonlinear_solver_name="basic_newton",
            convergence_type="PerComponentDeltaX",
            norm_type="NORM2",
            abstols="1e-9 1e-9",
            reltols="1e-9 1e-9",
            time_discretization="BackwardEuler",
        )
        self.prj.time_loop.set_stepping(
            process="SD",
            type="IterationNumberBasedTimeStepping",
            t_initial=0.0,
            t_end=self.end_time,
            initial_dt=10000,
            minimum_dt=10,
            maximum_dt=17280,
            number_iterations="1 4 10 15 20 25 31",
            multiplier="1.5 1.3 1.2 1.1 0.8 0.7 0.6",
        )
        self.prj.time_loop.add_output(
            type="VTK",
            prefix="kirsch",
            suffix="_ts_{:timestep}_t_{:time}",
            data_mode="Ascii",
            compress_output=False,
            repeat=1,
            each_steps=1,
            variables=["displacement", "epsilon", "sigma"],
        )

    def _add_solvers(self):
        self.prj.nonlinear_solvers.add_non_lin_solver(
            # SMALL_DEFORMATION implements only the Newton assembly path.
            name="basic_newton",
            type="Newton",
            max_iter=self.nonlinear_max_iter,
            linear_solver="general_linear_solver",
        )
        # Options set to None (irrelevant for direct solvers such as
        # SparseLU) are left out of the project file.
        eigen_options = {"solver_type": self.linear_solver_type}
        if self.preconditioner_type is not None:
            eigen_options["precon_type"] = self.preconditioner_type
        if self.linear_max_iter is not None:
            eigen_options["max_iteration_step"] = self.linear_max_iter
        if self.linear_error_tolerance is not None:
            eigen_options["error_tolerance"] = self.linear_error_tolerance
        if self.linear_solver_scaling:
            # Requires an OGS build with USE_EIGEN_UNSUPPORTED.
            eigen_options["scaling"] = "true"
        self.prj.linear_solvers.add_lin_solver(
            name="general_linear_solver",
            kind="eigen",
            **eigen_options,
        )
        # Keep the PETSc alternative for OGS builds using PETSc.
        self.prj.linear_solvers.add_lin_solver(
            name="general_linear_solver",
            kind="petsc",
            parameters=self.petsc_parameters,
        )


