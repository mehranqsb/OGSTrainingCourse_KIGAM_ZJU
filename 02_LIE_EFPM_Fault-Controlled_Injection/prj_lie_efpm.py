# SPDX-License-Identifier: BSD-3-Clause
"""Unified Python project-file generator for the LIE/EFPM benchmark.

Builds the four OGS project files (LIE/EFPM x one/two fractures) with the
``ogstools.Project`` API instead of shipping static prj files, following
https://ogstools.opengeosys.org/stable/auto_examples/howto_prjfile/plot_creation.html

Usage (mirrors ``mesh_lie_efpm.MeshGenerator``)::

    from prj_lie_efpm import ProjectGenerator

    prj_file = ProjectGenerator(approach="LIE", number_of_fractures=1).generate_project()
"""

from pathlib import Path

import ogstools as ot

_TIME_STEPPING = {
    "type": "IterationNumberBasedTimeStepping",
    "t_initial": "0.0",
    "t_end": "1500",
    "initial_dt": "10",
    "minimum_dt": "0.1",
    "number_iterations": ["1", "4", "8", "10", "16"],
    "multiplier": ["3.5", "2.5", "1.01", "0.5", "0.25"],
}

_CURVE_COORDS = [0, 100, 1000, 1100, 2000]

_CASES = {
    ("LIE", 1): {
        "out_dir": "SingleFractureMedium/LIE",
        "stem": "single_fracture_LIE",
        "mesh": "single_fracture_LIE_shifted.vtu",
        "gml": "single_fracture_LIE_shifted.gml",
        "geometrical_set": "single_fracture",
        "fracture_material_ids": [0],
        "matrix_medium_id": "1",
        "fracture_medium_id": "0",
        "abstols": "1e-2 1e-8 1e-8 1e-8 1e-8 1e-8 1e-8",
        "maximum_dt": "20",
        "damping": "1.0",
        "damping_reduction": "8",
        "pressure_bcs": [("POINT5", "Dirichlet"), ("POINT4", "Neumann")],
        "jump_bcs": {"displacement_jump1": ["POINT5", "POINT4"]},
    },
    ("LIE", 2): {
        "out_dir": "DoubleFractureMedium/LIE",
        "stem": "double_fracture_LIE",
        "mesh": "double_fracture_LIE_shifted.vtu",
        "gml": "double_fracture_LIE_shifted.gml",
        "geometrical_set": "double_fracture",
        "fracture_material_ids": [0, 1],
        "matrix_medium_id": "2",
        "fracture_medium_id": "0, 1",
        "abstols": "1e-2 1e-8 1e-8 1e-8 1e-8 1e-8 1e-8 1e-8 1e-8",
        "maximum_dt": "50",
        "damping": "1.0",
        "damping_reduction": "8",
        "pressure_bcs": [
            ("POINT5", "Dirichlet"),
            ("POINT4", "Neumann"),
            ("POINT7", "Dirichlet"),
            ("POINT6", "Neumann"),
        ],
        "jump_bcs": {
            "displacement_jump1": ["POINT5", "POINT4"],
            "displacement_jump2": ["POINT6", "POINT7"],
        },
    },
    ("EFPM", 1): {
        "out_dir": "SingleFractureMedium/EFP",
        "stem": "single_fracture_EFP",
        "mesh": "single_fracture_EFP_shifted.vtu",
        "gml": "single_fracture_EFP_shifted.gml",
        "geometrical_set": "single_fracture",
        "fracture_medium_id": "1",
        "maximum_dt": "20",
        "damping": "1.0",
        "damping_reduction": "8",
        "pressure_bcs": [("Frac_in", "Neumann"), ("Frac_out", "Dirichlet")],
    },
    ("EFPM", 2): {
        "out_dir": "DoubleFractureMedium/EFP",
        "stem": "double_fracture_EFP",
        "mesh": "double_fracture_EFP_shifted.vtu",
        "gml": "double_fracture_EFP_shifted.gml",
        "geometrical_set": "double_fracture",
        "fracture_medium_id": "1,2",
        "maximum_dt": "20",
        "damping": "1.0",
        "damping_reduction": "6",
        "pressure_bcs": [
            ("Frac0_in", "Neumann"),
            ("Frac0_out", "Dirichlet"),
            ("Frac1_in", "Neumann"),
            ("Frac1_out", "Dirichlet"),
        ],
    },
}


class ProjectGenerator:
    """Generate the prj file for one LIE/EFPM benchmark case."""

    def __init__(self, approach="LIE", number_of_fractures=1):
        key = (approach.upper(), number_of_fractures)
        if key not in _CASES:
            raise ValueError(
                "Supported cases are LIE/EFPM with one or two fractures"
            )
        self.approach, self.number_of_fractures = key
        self.case = _CASES[key]

    def generate_project(self, out_dir=None):
        """Write the prj file and return its path."""
        out_dir = (
            Path(self.case["out_dir"]) if out_dir is None else Path(out_dir)
        )
        out_dir.mkdir(parents=True, exist_ok=True)
        prj_path = out_dir / f"{self.case['stem']}.prj"

        prj = ot.Project(output_file=prj_path)
        # CubicLawPermeability has no extra tags but is unknown to the
        # generic MPL-property registry of ogstools.
        prj.media.properties.setdefault("CubicLawPermeability", [])

        prj.mesh.add_mesh(filename=self.case["mesh"], axially_symmetric=False)
        prj.geometry.add_geometry(self.case["gml"])
        if self.approach == "LIE":
            self._build_lie(prj)
        else:
            self._build_efpm(prj)
        self._build_solvers(prj)
        prj.write_input()
        return prj_path

    # -- process / time loop -------------------------------------------------

    def _build_lie(self, prj):
        case = self.case
        jumps = list(case["jump_bcs"])
        prj.processes.set_process(
            name="HM",
            type="HYDRO_MECHANICS_WITH_LIE",
            integration_order="2",
            specific_body_force="0 0",
            initial_effective_stress="effective_stress0",
            initial_fracture_effective_stress="fracture_effective_stress0",
        )
        for pv in ["pressure", "displacement", *jumps]:
            prj.processes.add_process_variable(
                process_variable="process_variable", process_variable_name=pv
            )
        prj.processes.set_constitutive_relation(
            type="LinearElasticIsotropic",
            youngs_modulus="E",
            poissons_ratio="nu",
        )
        prj.add_block(
            "fracture_model",
            parent_xpath="./processes/process",
            taglist=[
                "type",
                "normal_stiffness",
                "shear_stiffness",
                "penalty_aperture_cutoff",
                "tension_cutoff",
            ],
            textlist=["LinearElasticIsotropic", "Kn", "Ks", "1e-5", "0"],
        )
        for material_id in case["fracture_material_ids"]:
            prj.add_block(
                "fracture_properties",
                parent_xpath="./processes/process",
                taglist=["material_id", "initial_aperture"],
                textlist=[str(material_id), "b"],
            )
        prj.add_block("secondary_variables", parent_xpath="./processes/process")

        self._build_time_loop(prj, abstols=case["abstols"], variables=[])

        self._add_lie_media(prj)
        self._add_lie_parameters(prj)
        prj.curves.add_curve(
            name="curve_q_in",
            coords=_CURVE_COORDS,
            values=[0.0, 2.0e-8, 2.0e-8, -2.0e-8, -2.0e-8],
        )
        self._add_lie_process_variables(prj)

    def _build_efpm(self, prj):
        prj.processes.set_process(
            name="HM",
            type="HYDRO_MECHANICS",
            integration_order="3",
            specific_body_force="0 0",
            initial_stress="effective_stress0",
            mass_lumping="true",
        )
        prj.processes.set_constitutive_relation(
            type="LinearElasticIsotropic",
            youngs_modulus="E",
            poissons_ratio="nu",
        )
        prj.processes.add_process_variable(
            process_variable="pressure", process_variable_name="pressure"
        )
        prj.processes.add_process_variable(
            process_variable="displacement",
            process_variable_name="displacement",
        )
        for name in ["sigma", "epsilon"]:
            prj.processes.add_secondary_variable(
                internal_name=name, output_name=name
            )

        self._build_time_loop(
            prj,
            abstols="1e0 1e-10 1e-10",
            variables=["pressure_interpolated", "displacement"],
        )

        self._add_efpm_media(prj)
        self._add_efpm_parameters(prj)
        prj.curves.add_curve(
            name="curve_q_in",
            coords=_CURVE_COORDS,
            values=[0.0, 2.0e-2, 2.0e-2, -2.0e-2, -2.0e-2],
        )
        prj.curves.add_curve(
            name="curve_p_in",
            coords=[1, 1000, 1005, 2000],
            values=[0.9e6, 0.9e6, -0.9e6, -0.9e6],
        )
        self._add_efpm_process_variables(prj)

    def _build_time_loop(self, prj, abstols, variables):
        case = self.case
        prj.time_loop.add_process(
            process="HM",
            nonlinear_solver_name="basic_newton",
            convergence_type="PerComponentDeltaX",
            norm_type="NORM2",
            abstols=abstols,
            time_discretization="BackwardEuler",
        )
        prj.time_loop.set_stepping(
            process="HM", maximum_dt=case["maximum_dt"], **_TIME_STEPPING
        )
        output_args = {
            "type": "VTK",
            "prefix": case["stem"],
            "repeat": "1",
            "each_steps": "1",
            "variables": variables,
        }
        if self.approach == "LIE":
            output_args["suffix"] = "_LIE_ts_{:timestep}_t_{:time}"
        prj.time_loop.add_output(**output_args)

    # -- media ---------------------------------------------------------------

    def _add_lie_media(self, prj):
        case = self.case
        for medium_id in [case["matrix_medium_id"], case["fracture_medium_id"]]:
            for phase_type, name, parameter in [
                ("AqueousLiquid", "viscosity", "mu"),
                ("AqueousLiquid", "density", "rho_fr"),
                ("Solid", "density", "rho_sr"),
            ]:
                prj.media.add_property(
                    medium_id=medium_id,
                    phase_type=phase_type,
                    name=name,
                    type="Parameter",
                    parameter_name=parameter,
                )
            prj.media.add_property(
                medium_id=medium_id,
                name="reference_temperature",
                type="Constant",
                value="293.15",
            )
        # Porous matrix.
        for name, parameter in [
            ("permeability", "k"),
            ("porosity", "phi"),
            ("storage", "S"),
            ("biot_coefficient", "biot_m"),
        ]:
            prj.media.add_property(
                medium_id=case["matrix_medium_id"],
                name=name,
                type="Parameter",
                parameter_name=parameter,
            )
        # Fracture.
        prj.media.add_property(
            medium_id=case["fracture_medium_id"],
            name="permeability",
            type="CubicLawPermeability",
        )
        prj.media.add_property(
            medium_id=case["fracture_medium_id"],
            name="porosity",
            type="Constant",
            value="0.0",
        )
        for name, parameter in [("storage", "S_f"), ("biot_coefficient", "biot_f")]:
            prj.media.add_property(
                medium_id=case["fracture_medium_id"],
                name=name,
                type="Parameter",
                parameter_name=parameter,
            )

    def _add_efpm_media(self, prj):
        case = self.case
        for medium_id in ["0", case["fracture_medium_id"]]:
            prj.media.add_property(
                medium_id=medium_id,
                phase_type="Gas",
                name="viscosity",
                type="Constant",
                value="0.001",
            )
            prj.media.add_property(
                medium_id=medium_id,
                phase_type="Gas",
                name="density",
                type="Linear",
                reference_value="1000.0",
                independent_variables={
                    "gas_phase_pressure": {
                        "reference_condition": "0",
                        "slope": "1e-07",
                    }
                },
            )
            prj.media.add_property(
                medium_id=medium_id,
                phase_type="Solid",
                name="density",
                type="Constant",
                value="2716.0",
            )
            for name, value in [
                ("porosity", "0.001"),
                ("biot_coefficient", "1"),
                ("reference_temperature", "293.15"),
            ]:
                prj.media.add_property(
                    medium_id=medium_id, name=name, type="Constant", value=value
                )
        prj.media.add_property(
            medium_id="0",
            name="permeability",
            type="Constant",
            value="1e-21",
        )
        prj.media.add_property(
            medium_id=case["fracture_medium_id"],
            name="permeability",
            type="EmbeddedFracturePermeability",
            intrinsic_permeability="0.0",
            initial_aperture="0.0",
            mean_frac_distance="1.00e-03",
            threshold_strain="-1.00e-02",
            fracture_normal="0 1 0",
            fracture_rotation_xy="zero",
            fracture_rotation_yz="zero",
            jacobian_factor="1",
        )

    # -- parameters ----------------------------------------------------------

    def _add_lie_parameters(self, prj):
        constants = [
            # Fluid phase properties
            ("rho_fr", "1000.0"),
            ("mu", "0.001"),
            # Solid phase properties
            ("rho_sr", "2716.0"),
            # Porous medium properties
            ("phi", "0.001"),
            ("k", "1e-21"),
            ("S", "1.00e-10"),
            ("biot_m", "1"),
            ("E", "6.00e+10"),
            ("nu", "0"),
            # Fracture properties
            ("b", "1e-05"),
            ("S_f", "1.00e-10"),
            ("biot_f", "1"),
            ("Kn", "1.00e+11"),
            ("Ks", "1.00e+11"),
            # Flow properties
            ("p0", "1.10e+07"),
        ]
        for name, value in constants:
            prj.parameters.add_parameter(name=name, type="Constant", value=value)
        prj.parameters.add_parameter(
            name="q_in",
            type="CurveScaled",
            curve="curve_q_in",
            parameter="q_in_start",
        )
        prj.parameters.add_parameter(
            name="q_in_start", type="Constant", value="1"
        )
        prj.parameters.add_parameter(
            name="area_parameter", type="Constant", value="1"
        )
        prj.parameters.add_parameter(
            name="displacement0", type="Constant", values="0 0"
        )
        prj.parameters.add_parameter(
            name="effective_stress0",
            type="Constant",
            values="0 -3.90e+07 0 0",
        )
        prj.parameters.add_parameter(
            name="fracture_effective_stress0",
            type="Constant",
            values="0 -3.90e+07",
        )
        prj.parameters.add_parameter(name="zero_u", type="Constant", value="0")
        prj.parameters.add_parameter(
            name="load", type="Constant", value="-5.00e+07"
        )

    def _add_efpm_parameters(self, prj):
        prj.parameters.set_group_parameter(
            name="E",
            group_id_property="MaterialIDs",
            index_values={0: "60e9", 1: "9.98e7"},
        )
        constants = [
            ("nu", "0"),
            ("k", "0.0"),
            ("p0", "0.00e+00"),
        ]
        for name, value in constants:
            prj.parameters.add_parameter(name=name, type="Constant", value=value)
        prj.parameters.add_parameter(
            name="q_in",
            type="CurveScaled",
            curve="curve_q_in",
            parameter="q_in_start",
        )
        prj.parameters.add_parameter(
            name="q_in_start", type="Constant", value="1"
        )
        prj.parameters.add_parameter(
            name="displacement0", type="Constant", values="0 0"
        )
        prj.parameters.add_parameter(
            name="effective_stress0", type="Constant", values="0 0.00e+00 0 0"
        )
        prj.parameters.add_parameter(name="zero", type="Constant", value="0")
        prj.parameters.add_parameter(
            name="load", type="Constant", value="0.00e+00"
        )

    # -- process variables / boundary conditions -----------------------------

    def _add_lie_process_variables(self, prj):
        case = self.case
        gset = case["geometrical_set"]
        prj.process_variables.set_ic(
            process_variable_name="pressure",
            components="1",
            order="1",
            initial_condition="p0",
        )
        for geometry, bc_type in case["pressure_bcs"]:
            bc_args = {
                "geometrical_set": gset,
                "geometry": geometry,
                "component": "0",
            }
            if bc_type == "Neumann":
                bc_args["area_parameter"] = "area_parameter"
                bc_args["parameter"] = "q_in"
            else:
                bc_args["parameter"] = "p0"
            prj.process_variables.add_bc(
                process_variable_name="pressure", type=bc_type, **bc_args
            )

        prj.process_variables.set_ic(
            process_variable_name="displacement",
            components="2",
            order="2",
            initial_condition="displacement0",
        )
        for geometry, component, parameter, bc_type in [
            ("PLY_SOUTH", "1", "zero_u", "Dirichlet"),
            ("PLY_WEST", "0", "zero_u", "Dirichlet"),
            ("PLY_EAST", "0", "zero_u", "Dirichlet"),
            ("PLY_NORTH", "1", "load", "Neumann"),
        ]:
            prj.process_variables.add_bc(
                process_variable_name="displacement",
                type=bc_type,
                geometrical_set=gset,
                geometry=geometry,
                component=component,
                parameter=parameter,
            )

        for jump, geometries in case["jump_bcs"].items():
            prj.process_variables.set_ic(
                process_variable_name=jump,
                components="2",
                order="2",
                initial_condition="displacement0",
            )
            for geometry in geometries:
                prj.process_variables.add_bc(
                    process_variable_name=jump,
                    type="Dirichlet",
                    geometrical_set=gset,
                    geometry=geometry,
                    component="0",
                    parameter="zero_u",
                )

    def _add_efpm_process_variables(self, prj):
        case = self.case
        gset = case["geometrical_set"]
        prj.process_variables.set_ic(
            process_variable_name="pressure",
            components="1",
            order="1",
            initial_condition="p0",
        )
        for geometry, bc_type in case["pressure_bcs"]:
            prj.process_variables.add_bc(
                process_variable_name="pressure",
                type=bc_type,
                geometrical_set=gset,
                geometry=geometry,
                component="0",
                parameter="q_in" if bc_type == "Neumann" else "p0",
            )

        prj.process_variables.set_ic(
            process_variable_name="displacement",
            components="2",
            order="2",
            initial_condition="displacement0",
        )
        for geometry, component, parameter, bc_type in [
            ("Bot", "1", "zero", "Dirichlet"),
            ("Left", "0", "zero", "Dirichlet"),
            ("Right", "0", "zero", "Dirichlet"),
            ("Top", "1", "load", "Neumann"),
        ]:
            prj.process_variables.add_bc(
                process_variable_name="displacement",
                type=bc_type,
                geometrical_set=gset,
                geometry=geometry,
                component=component,
                parameter=parameter,
            )

    # -- solvers -------------------------------------------------------------

    def _build_solvers(self, prj):
        case = self.case
        prj.nonlinear_solvers.add_non_lin_solver(
            name="basic_newton",
            type="Newton",
            max_iter="50",
            damping=case["damping"],
            linear_solver="general_linear_solver",
        )
        prj.add_element(
            parent_xpath="./nonlinear_solvers/nonlinear_solver",
            tag="damping_reduction",
            text=case["damping_reduction"],
        )
        if self.approach == "EFPM":
            prj.linear_solvers.add_lin_solver(
                name="general_linear_solver",
                kind="lis",
                lis="-i SparseLU -p diagonal -tol 1e-12 -maxiter 50000",
            )
        prj.linear_solvers.add_lin_solver(
            name="general_linear_solver",
            kind="eigen",
            solver_type="SparseLU",
            scaling="1",
        )
