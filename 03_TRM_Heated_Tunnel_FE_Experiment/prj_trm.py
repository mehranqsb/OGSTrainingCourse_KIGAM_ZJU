# SPDX-FileCopyrightText: Copyright (c) OpenGeoSys Community (opengeosys.org)
# SPDX-License-Identifier: BSD-3-Clause

# %%
"""Project-file generator for the TRM heater (HE/FE) tunnel problem.

Counterpart of :class:`mesh_tunnel_trm.MeshGenerator` for the OGS project
file, following the same route as the Kirsch example's ``prj_tunnel.py``.
This module defines only the model *structure*: the THERMO_RICHARDS_MECHANICS
process in its fully saturated form, with the material properties, boundary
conditions, and initial conditions of the legacy THM project
``legacy_thm/tunnel_ortho_LTRB_90_roller_SparseLU.prj`` (two materials:
isotropic bentonite buffer and orthotropic Opalinus Clay with a local
coordinate system). All physical and numerical parameter values are
supplied by the caller (the notebook's "Model parameters" and "Solver
settings" cells).
"""

from pathlib import Path

import numpy as np
import ogstools as ot

# IAPWS-based water viscosity mu(T) table, as used in the DECOVALEX Task C
# benchmark (physical reference data, not a model tuning parameter). Used
# by the partially saturated variant.
WATER_VISCOSITY_TEMPERATURES = [273.15 + 5.0 * i for i in range(37)]
WATER_VISCOSITY_VALUES = [
    0.001791443824493071, 0.001518096315579494, 0.001306005897987292,
    0.001137740703477269, 0.001001761870211410, 0.000890153572198349,
    0.000797321713362585, 0.000719212401364518, 0.000652823923857197,
    0.000595891721429222, 0.000546679133154530, 0.000503834893499928,
    0.000466293936304618, 0.000433206989018526, 0.000403889725629819,
    0.000377785466842696, 0.000354437428880606, 0.000333467809699829,
    0.000314561842102885, 0.000297455502677900, 0.000281925944210631,
    0.000267783979663162, 0.000254868127533467, 0.000243039856904272,
    0.000232179762477740, 0.000222184466506006, 0.000212964093284412,
    0.000204440197918893, 0.000196544057975752, 0.000189215256869282,
    0.000182400503210232, 0.000176052642092791, 0.000170129823355037,
    0.000164594798874974, 0.000159414326452323, 0.000154558662138820,
    0.000150001126288821,
]


# %%
class PrjGenerator:
    """Create the TRM heater OGS project file (fully saturated).

    Two media share the liquid phase description: medium 0 is the
    bentonite buffer (isotropic linear elasticity), medium 1 the Opalinus
    Clay (orthotropic elasticity and anisotropic permeability/thermal
    conductivity, oriented by a local coordinate system). The heater is
    represented by a heat-flux Neumann condition on ``arc_inner``;
    displacement boundary conditions are rollers on the outer boundaries
    (LTRB) with the heater surface fixed. Mesh file names are kept
    portable (``domain.vtu`` etc.).
    """

    mesh_names = (
        "domain",
        "left",
        "right",
        "top",
        "bottom",
        "arc_inner",
        "arc_outer",
    )

    def __init__(
        self,
        *,
        saturation_model,
        bedding_angle_deg,
        liquid,
        bentonite,
        clay,
        tunnel_radius,
        biot_coefficient,
        heater_flux,
        initial_temperature,
        initial_pressure,
        initial_stress,
        t_end,
        initial_dt,
        minimum_dt,
        maximum_dt,
        number_iterations,
        multiplier,
        reltols,
        nonlinear_max_iter,
        linear_solver_type,
        preconditioner_type,
        linear_max_iter,
        linear_error_tolerance,
        linear_solver_scaling,
        element_order,
        output_prefix,
        mesh_dir=Path(),
        petsc_parameters=(
            "-ksp_type bcgs -pc_type bjacobi "
            "-ksp_rtol 1.e-18 -ksp_atol 1.e-18 -ksp_max_it 4000"
        ),
    ):
        if element_order not in (1, 2):
            raise ValueError("element_order must be 1 or 2")
        if saturation_model not in ("saturated", "partially_saturated"):
            raise ValueError(
                "saturation_model must be 'saturated' or "
                "'partially_saturated'"
            )
        if bedding_angle_deg not in (0, 90):
            raise ValueError("bedding_angle_deg must be 0 or 90")

        self.saturation_model = saturation_model
        self.bedding_angle_deg = bedding_angle_deg
        self.liquid = liquid
        self.bentonite = bentonite
        self.clay = clay
        self.tunnel_radius = tunnel_radius
        self.biot_coefficient = biot_coefficient
        self.heater_flux = heater_flux
        self.initial_temperature = initial_temperature
        self.initial_pressure = initial_pressure
        self.initial_stress = initial_stress
        self.t_end = t_end
        self.initial_dt = initial_dt
        self.minimum_dt = minimum_dt
        self.maximum_dt = maximum_dt
        self.number_iterations = number_iterations
        self.multiplier = multiplier
        self.reltols = reltols
        self.nonlinear_max_iter = nonlinear_max_iter
        self.linear_solver_type = linear_solver_type
        self.preconditioner_type = preconditioner_type
        self.linear_max_iter = linear_max_iter
        self.linear_error_tolerance = linear_error_tolerance
        self.linear_solver_scaling = linear_solver_scaling
        self.element_order = element_order
        self.output_prefix = output_prefix
        self.mesh_dir = Path(mesh_dir)
        self.petsc_parameters = petsc_parameters

        self.prj = None

    # --- Public API -----------------------------------------------------

    def generate_project(self, output_file="trm_tunnel.prj"):
        """Assemble the project and write the ``.prj`` file."""
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        self.prj = ot.Project(output_file=output_file)

        self._add_meshes()
        self._add_process()
        self._add_media()
        self._add_local_coordinate_system()
        self._add_parameters()
        self._add_curves()
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
            name="TRM",
            type="THERMO_RICHARDS_MECHANICS",
            integration_order=4,
            specific_body_force="0 0",
        )
        if self.saturation_model == "partially_saturated":
            # As in the Task C benchmark: stabilizes the sharp
            # saturation fronts of the dry-out zone.
            self.prj.add_element(
                parent_xpath="./processes/process",
                tag="mass_lumping",
                text="true",
            )
        # Medium 0: isotropic bentonite buffer.
        self.prj.processes.set_constitutive_relation(
            id="0",
            type="LinearElasticIsotropic",
            youngs_modulus="E_bent",
            poissons_ratio="nu_bent",
        )
        # Medium 1: orthotropic Opalinus Clay.
        self.prj.add_block(
            blocktag="constitutive_relation",
            block_attrib={"id": "1"},
            parent_xpath="./processes/process",
            taglist=[
                "type",
                "youngs_moduli",
                "shear_moduli",
                "poissons_ratios",
            ],
            textlist=[
                "LinearElasticOrthotropic",
                "E_clay",
                "G_clay",
                "nu_clay",
            ],
        )
        for pv in ("temperature", "pressure", "displacement"):
            self.prj.processes.add_process_variable(
                process_variable=pv, process_variable_name=pv
            )
        for sv in ("sigma", "epsilon", "saturation", "velocity"):
            self.prj.processes.add_secondary_variable(sv, sv)
        self.prj.add_element(
            parent_xpath="./processes/process",
            tag="initial_stress",
            text="initial_stress",
        )

    def _add_medium_saturated(self, medium_id, solid):
        """One medium: shared liquid phase + material-specific solid."""
        add = self.prj.media.add_property

        # --- AqueousLiquid phase (identical in both media) --------------
        liquid = self.liquid
        add(
            medium_id=medium_id,
            phase_type="AqueousLiquid",
            name="specific_heat_capacity",
            type="Constant",
            value=liquid["specific_heat_capacity"],
        )
        add(
            medium_id=medium_id,
            phase_type="AqueousLiquid",
            name="thermal_conductivity",
            type="Constant",
            value=liquid["thermal_conductivity"],
        )
        add(
            medium_id=medium_id,
            phase_type="AqueousLiquid",
            name="density",
            type="Linear",
            reference_value=liquid["density_reference"],
            independent_variables={
                "temperature": {
                    "reference_condition": liquid[
                        "density_reference_temperature"
                    ],
                    "slope": liquid["density_slope_temperature"],
                },
                "liquid_phase_pressure": {
                    "reference_condition": liquid[
                        "density_reference_pressure"
                    ],
                    "slope": liquid["density_slope_pressure"],
                },
            },
        )
        add(
            medium_id=medium_id,
            phase_type="AqueousLiquid",
            name="thermal_expansivity",
            type="Constant",
            value=liquid["thermal_expansivity"],
        )
        add(
            medium_id=medium_id,
            phase_type="AqueousLiquid",
            name="viscosity",
            type="Constant",
            value=liquid["viscosity"],
        )

        # --- Solid phase -------------------------------------------------
        for name in (
            "density",
            "specific_heat_capacity",
            "thermal_conductivity",
            "thermal_expansivity",
        ):
            add(
                medium_id=medium_id,
                phase_type="Solid",
                name=name,
                type="Constant",
                value=solid[name],
            )

        # --- Medium properties -------------------------------------------
        add(
            medium_id=medium_id,
            name="permeability",
            type="Constant",
            value=solid["permeability"],
        )
        add(
            medium_id=medium_id,
            name="porosity",
            type="Constant",
            value=solid["porosity"],
        )
        add(
            medium_id=medium_id,
            name="biot_coefficient",
            type="Constant",
            value=self.biot_coefficient,
        )
        # Fully saturated TRM variant: S_L = 1.
        add(
            medium_id=medium_id,
            name="saturation",
            type="Constant",
            value=1.0,
        )
        add(
            medium_id=medium_id,
            name="relative_permeability",
            type="Constant",
            value=1.0,
        )
        add(
            medium_id=medium_id,
            name="bishops_effective_stress",
            type="BishopsPowerLaw",
            exponent=1.0,
        )
        add(
            medium_id=medium_id,
            name="thermal_conductivity",
            type="EffectiveThermalConductivityPorosityMixing",
        )

    def _add_medium_partially_saturated(self, medium_id, solid):
        """Gas phase with water vapour, van Genuchten retention."""
        add = self.prj.media.add_property

        # --- Gas phase: water vapour diffusion --------------------------
        for name, type_ in (
            ("density", "WaterVapourDensity"),
            ("diffusion", "VapourDiffusionFEBEX"),
            ("specific_latent_heat", "LinearWaterVapourLatentHeat"),
        ):
            add(medium_id=medium_id, phase_type="Gas", name=name, type=type_)
        add(
            medium_id=medium_id,
            phase_type="Gas",
            name="thermal_diffusion_enhancement_factor",
            type="Constant",
            value=1.0,
        )
        add(
            medium_id=medium_id,
            phase_type="Gas",
            name="specific_heat_capacity",
            type="Constant",
            value=0.0,
        )

        # --- AqueousLiquid phase ----------------------------------------
        liquid = self.liquid
        add(
            medium_id=medium_id,
            phase_type="AqueousLiquid",
            name="specific_heat_capacity",
            type="Constant",
            value=liquid["specific_heat_capacity"],
        )
        add(
            medium_id=medium_id,
            phase_type="AqueousLiquid",
            name="density",
            type="Linear",
            reference_value=liquid["density_reference"],
            independent_variables={
                "temperature": {
                    "reference_condition": liquid[
                        "density_reference_temperature"
                    ],
                    "slope": liquid["density_slope_temperature"],
                },
                "liquid_phase_pressure": {
                    "reference_condition": liquid[
                        "density_reference_pressure"
                    ],
                    "slope": liquid["density_slope_pressure"],
                },
            },
        )
        add(
            medium_id=medium_id,
            phase_type="AqueousLiquid",
            name="viscosity",
            type="Curve",
            curve="viscosity_water",
            independent_variable="temperature",
        )

        # --- Solid phase (no solid thermal conductivity: the medium
        # property below covers the mixture) -----------------------------
        for name in ("density", "specific_heat_capacity",
                     "thermal_expansivity"):
            add(
                medium_id=medium_id,
                phase_type="Solid",
                name=name,
                type="Constant",
                value=solid[name],
            )

        # --- Medium properties ------------------------------------------
        add(
            medium_id=medium_id,
            name="tortuosity",
            type="Constant",
            value=solid["tortuosity"],
        )
        add(
            medium_id=medium_id,
            name="porosity",
            type="Constant",
            value=solid["porosity"],
        )
        add(
            medium_id=medium_id,
            name="biot_coefficient",
            type="Constant",
            value=self.biot_coefficient,
        )
        add(
            medium_id=medium_id,
            name="permeability",
            type="Constant",
            value=solid["permeability"],
        )
        add(
            medium_id=medium_id,
            name="relative_permeability",
            type="RelativePermeabilityVanGenuchten",
            residual_liquid_saturation=solid["residual_liquid_saturation"],
            residual_gas_saturation=solid["residual_gas_saturation"],
            exponent=solid["vg_exponent"],
            minimum_relative_permeability_liquid=solid[
                "minimum_relative_permeability"
            ],
        )
        add(
            medium_id=medium_id,
            name="saturation",
            type="SaturationVanGenuchten",
            residual_liquid_saturation=solid["residual_liquid_saturation"],
            residual_gas_saturation=solid["residual_gas_saturation"],
            exponent=solid["vg_exponent"],
            p_b=solid["vg_p_b"],
        )
        add(
            medium_id=medium_id,
            name="bishops_effective_stress",
            type="BishopsSaturationCutoff",
            cutoff_value=1.0,
        )
        if "thermal_conductivity_dry" in solid:
            # Buffer: linear lambda(S_L) between dry and saturated value.
            add(
                medium_id=medium_id,
                name="thermal_conductivity",
                type="Curve",
                curve="thermal_conductivity_bentonite",
                independent_variable="liquid_saturation",
            )
        else:
            add(
                medium_id=medium_id,
                name="thermal_conductivity",
                type="Constant",
                value=solid["thermal_conductivity"],
            )

    def _add_media(self):
        if self.saturation_model == "saturated":
            self._add_medium_saturated(medium_id=0, solid=self.bentonite)
            self._add_medium_saturated(medium_id=1, solid=self.clay)
        else:
            self._add_medium_partially_saturated(
                medium_id=0, solid=self.bentonite
            )
            self._add_medium_partially_saturated(
                medium_id=1, solid=self.clay
            )

    def _add_local_coordinate_system(self):
        # Bedding orientation of the Opalinus Clay. The basis vectors e0/e1
        # are set in _add_parameters from bedding_angle_deg (90 degrees is
        # the legacy configuration: e0 = (0, 1), e1 = (-1, 0)).
        self.prj.add_block(
            blocktag="local_coordinate_system",
            parent_xpath=".",
            taglist=["basis_vector_0", "basis_vector_1"],
            textlist=["e0", "e1"],
        )

    def _add_parameters(self):
        parameters = self.prj.parameters
        if self.bedding_angle_deg == 90:
            basis = {"e0": "0. 1.", "e1": "-1. 0."}
        else:  # 0 degrees: material axes aligned with x/y
            basis = {"e0": "1. 0.", "e1": "0. 1."}
        for name, values in basis.items():
            parameters.set_constant_parameter(name=name, values=values)

        parameters.set_constant_parameter(
            name="E_bent", value=self.bentonite["youngs_modulus"]
        )
        parameters.set_constant_parameter(
            name="nu_bent", value=self.bentonite["poissons_ratio"]
        )
        parameters.set_constant_parameter(
            name="E_clay", values=self.clay["youngs_moduli"]
        )
        parameters.set_constant_parameter(
            name="nu_clay", values=self.clay["poissons_ratios"]
        )
        parameters.set_function_parameter(
            name="G_clay", expression=self.clay["shear_moduli"]
        )

        parameters.set_constant_parameter(
            name="displacement_ic", values="0 0"
        )
        parameters.set_constant_parameter(name="zero", value=0.0)
        if self.saturation_model == "saturated":
            parameters.set_constant_parameter(
                name="pressure_ic", value=self.initial_pressure
            )
        else:
            # High suction in the buffer, in-situ pore pressure in the
            # clay; interface nodes get the buffer value, i.e. the
            # suction jump sits exactly at the contact (as in the paper).
            radius = "sqrt(x^2 + y^2)"
            parameters.set_function_parameter(
                name="pressure_ic",
                expression=(
                    f"if ({radius} <= {self.tunnel_radius + 1e-6}) "
                    f"{self.bentonite['initial_pressure']}; "
                    f"else {self.clay['initial_pressure']}"
                ),
            )
        parameters.set_constant_parameter(
            name="temperature_ic", value=self.initial_temperature
        )
        parameters.set_constant_parameter(
            name="initial_stress", values=self.initial_stress
        )
        parameters.set_constant_parameter(
            name="heater", value=self.heater_flux
        )

    def _add_curves(self):
        if self.saturation_model == "saturated":
            return
        # Buffer thermal conductivity: linear in saturation between the
        # dry and water-saturated values (as in the Task C benchmark).
        lam = np.linspace(
            self.bentonite["thermal_conductivity_dry"],
            self.bentonite["thermal_conductivity_saturated"],
            21,
        )
        self.prj.curves.add_curve(
            name="thermal_conductivity_bentonite",
            coords=[f"{v:.2f}" for v in np.linspace(0.0, 1.0, 21)],
            values=[f"{v:.6g}" for v in lam],
        )
        self.prj.curves.add_curve(
            name="viscosity_water",
            coords=[f"{t:.2f}" for t in WATER_VISCOSITY_TEMPERATURES],
            values=[f"{v:.15g}" for v in WATER_VISCOSITY_VALUES],
        )

    def _add_initial_and_boundary_conditions(self):
        set_ic = self.prj.process_variables.set_ic
        set_ic(
            process_variable_name="displacement",
            components=2,
            order=self.element_order,
            initial_condition="displacement_ic",
        )
        set_ic(
            process_variable_name="pressure",
            components=1,
            order=1,
            initial_condition="pressure_ic",
        )
        set_ic(
            process_variable_name="temperature",
            components=1,
            order=1,
            initial_condition="temperature_ic",
        )

        add_bc = self.prj.process_variables.add_bc
        # Rollers on all outer boundaries (LTRB), heater surface fixed,
        # as in the legacy project.
        for mesh, component in (
            ("left", 0),
            ("right", 0),
            ("bottom", 1),
            ("top", 1),
        ):
            add_bc(
                process_variable_name="displacement",
                type="Dirichlet",
                mesh=mesh,
                component=component,
                parameter="zero",
            )
        for component in (0, 1):
            add_bc(
                process_variable_name="displacement",
                type="Dirichlet",
                mesh="arc_inner",
                component=component,
                parameter="zero",
            )
        # Heater: heat flux on the inner arc; all other thermal and all
        # hydraulic boundaries are natural (no flow).
        add_bc(
            process_variable_name="temperature",
            type="Neumann",
            mesh="arc_inner",
            parameter="heater",
        )

    def _add_time_loop_and_output(self):
        self.prj.time_loop.add_process(
            process="TRM",
            nonlinear_solver_name="basic_newton",
            convergence_type="PerComponentDeltaX",
            norm_type="NORM2",
            reltols=self.reltols,
            time_discretization="BackwardEuler",
        )
        self.prj.time_loop.set_stepping(
            process="TRM",
            type="IterationNumberBasedTimeStepping",
            t_initial=0.0,
            t_end=self.t_end,
            initial_dt=self.initial_dt,
            minimum_dt=self.minimum_dt,
            maximum_dt=self.maximum_dt,
            number_iterations=self.number_iterations,
            multiplier=self.multiplier,
        )
        self.prj.time_loop.add_output(
            type="VTK",
            prefix=self.output_prefix,
            suffix="_ts_{:timestep}_t_{:time}",
            repeat=1,
            each_steps=1,
            variables=[
                "displacement",
                "pressure",
                "temperature",
                # Interpolations of the order-1 variables onto all nodes
                # of the order-2 mesh (midside nodes included).
                "pressure_interpolated",
                "temperature_interpolated",
                "sigma",
                "epsilon",
                "saturation",
                "velocity",
            ],
        )

    def _add_solvers(self):
        self.prj.nonlinear_solvers.add_non_lin_solver(
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
