from enum import Enum
from typing import Optional
from scipy.spatial import ConvexHull
from shapely import Polygon
from dataclasses import dataclass
from pydantic import Field as dataclass_field
from moapy.auto_convert import auto_schema, MBaseModel
from abc import ABC, abstractmethod

from concreteproperties.pre import add_bar
from concreteproperties.concrete_section import ConcreteSection
from concreteproperties.prestressed_section import PrestressedSection
from concreteproperties.material import Concrete, SteelBar, SteelStrand

import sectionproperties.pre.geometry as geometry
import sectionproperties.pre.pre as pre
import concreteproperties.stress_strain_profile as ssp
import concreteproperties.utils as utils
import concreteproperties.results
import numpy as np
import trimesh

# ==== Unit & Design Code ====
class Force(MBaseModel):
    """Force class

    Args:
        Nz (float): Axial force
        Mx (float): Moment about x-axis
        My (float): Moment about y-axis
    """
    Nz: float = dataclass_field(default=0.0, description="Axial force")
    Mx: float = dataclass_field(default=0.0, description="Moment about x-axis")
    My: float = dataclass_field(default=0.0, description="Moment about y-axis")

    class Config(MBaseModel.Config):
        title = "Force"
        description = "Force class"

class Mesh3DPM(MBaseModel):
    """
    3D P-M onion mesh result class

    Args:
        mesh3dpm (list[Force]): onion mesh result
    """
    mesh3dpm : list[Force] = dataclass_field(default=[], description="onion mesh result")

    class Config(MBaseModel.Config):
        title = "3DPM onion mesh result"

class Lcom(MBaseModel):
    """
    Lcom result class

    Args:
        name (str): load combination name
        f (Force): load combination force
    """
    name: str = dataclass_field(default="lcom", description="load combination name")
    f: Force = dataclass_field(default=Force(), description="load combination force")

    class Config(MBaseModel.Config):
        title = "Lcom Result"

class Lcoms(MBaseModel):
    """
    Strength result class
    
    Args:
        lcoms (list[Lcom]): load combination result
    """
    lcoms: list[Lcom] = dataclass_field(default=[Lcom(name="uls1", f=Force(Nz=100.0, Mx=10.0, My=50.0))], description="load combination result")

    class Config(MBaseModel.Config):
        title = "Strength Result"

class Result3DPM(MBaseModel):
    """
    GSD 3DPM result class
    
    Args:
        meshes (Mesh3DPM): 3DPM onion result
        lcbs (list[Lcom]): Load combination
        strength (list[Lcom]): Strength result
    """
    meshes: Mesh3DPM = dataclass_field(default=Mesh3DPM(), description="3DPM onion result")
    lcbs: list[Lcom] = dataclass_field(default=[], description="Load combination")
    strength: list[Lcom] = dataclass_field(default=[], description="Strength result")

    class Config(MBaseModel.Config):
        title = "GSD 3DPM Result"
        widget = "3DPM_Widget"

class Unit(MBaseModel):
    """
    GSD global unit class
    
    Args:
        force (str): Force unit
        length (str): Length unit
        section_dimension (str): Section dimension unit
        pressure (str): Pressure unit
        strain (str): Strain unit
    """
    force: str = dataclass_field(
        default="kN", description="Force unit")
    length: str = dataclass_field(
        default="m", description="Length unit")
    section_dimension: str = dataclass_field(
        default="mm", description="Section dimension unit")
    pressure: str = dataclass_field(
        default="MPa", description="Pressure unit")
    strain: str = dataclass_field(
        default="%", description="Strain unit")

    class Config(MBaseModel.Config):
        title = "GSD Unit"

class DesignCode(MBaseModel):
    """Design Code class

    Args:
        design_code (str): Design code
        sub_code (str): Sub code
    """    
    design_code: str = dataclass_field(default="ACI 318-19", max_length=30)
    sub_code: str = dataclass_field(default="SI")

    class Config(MBaseModel.Config):
        title = "GSD Design Code"


# ==== Stress Strain Curve ====
class Stress_Strain_Component(MBaseModel):
    """Stress Strain Component class

    Args:
        stress (float): Stress
        strain (float): Strain
    """
    stress: float = dataclass_field(default=0.0, description="Stress")
    strain: float = dataclass_field(default=0.0, description="Strain")

    class Config(MBaseModel.Config):
        title = "Stress Strain Component"

# ==== Concrete Material ====
class ConcreteGrade(MBaseModel):
    """
    GSD concrete class

    Args:
        design_code (str): Design code
        grade (str): Grade of the concrete
    """
    design_code: str = dataclass_field(
        default="ACI318M-19", description="Design code")
    grade: str = dataclass_field(
        default="C12", description="Grade of the concrete")

    class Config(MBaseModel.Config):
        title = "GSD Concrete Grade"

class Concrete_General_Properties(MBaseModel):
    """
    GSD concrete general properties for calculation
    
    Args:
        strength (int): Grade of the concrete
        elastic_modulus (float): Elastic modulus of the concrete
        density (float): Density of the concrete
        thermal_expansion_coefficient (float): Thermal expansion coefficient of the concrete
        poisson_ratio (float): Poisson ratio of the concrete
    """
    strength: int = dataclass_field(
        gt=0, default=12, description="Grade of the concrete")
    elastic_modulus: float = dataclass_field(
        gt=0, default=30000, description="Elastic modulus of the concrete")
    density: float = dataclass_field(
        gt=0, default=2400, description="Density of the concrete")
    thermal_expansion_coefficient: float = dataclass_field(
        gt=0, default=0.00001, description="Thermal expansion coefficient of the concrete")
    poisson_ratio: float = dataclass_field(
        gt=0, default=0.2, description="Poisson ratio of the concrete")

    class Config(MBaseModel.Config):
        title = "GSD Concrete General Properties"

class Concrete_Stress_ULS_Options_ACI(MBaseModel):
    """
    GSD concrete stress options for ULS
    
    Args:
        material_model (str): Material model for ULS
        factor_b1 (float): Plastic strain limit for ULS
        compressive_failure_strain (float): Failure strain limit for ULS
    """
    material_model: str = dataclass_field(
        default="Rectangle", description="Material model for ULS")
    factor_b1: float = dataclass_field(
        default=0.85, description="Plastic strain limit for ULS")
    compressive_failure_strain: float = dataclass_field(
        default=0.003, description="Failure strain limit for ULS")

    class Config(MBaseModel.Config):
        title = "GSD Concrete Stress Options for ULS"

class Concrete_Stress_ULS_Options_Eurocode(MBaseModel):
    """
    GSD concrete stress options for ULS
    
    Args:
        material_model (str): Material model for ULS
        partial_factor_case (float): Partial factor case for ULS
        partial_factor (float): Partial factor for ULS
        compressive_failure_strain (float): Failure strain limit for ULS
    """
    material_model: str = dataclass_field(
        default="Rectangle", description="Material model for ULS")
    partial_factor_case: float = dataclass_field(
        default=1.0, description="Partial factor case for ULS")
    partial_factor: float = dataclass_field(
        default=1.5, description="Partial factor for ULS")
    compressive_failure_strain: float = dataclass_field(
        default=0.003, description="Failure strain limit for ULS")

    class Config(MBaseModel.Config):
        title = "GSD Concrete Stress Options for ULS"

class Concrete_SLS_Options(MBaseModel):
    """
    GSD concrete stress options for SLS
    
    Args:
        material_model (str): Material model for SLS
        plastic_strain_limit (float): Plastic strain limit for SLS
        failure_compression_limit (float): Failure compression limit for SLS
        material_model_tension (str): Material model for SLS tension
        failure_tension_limit (float): Failure tension limit for SLS
    """
    material_model: str = dataclass_field(
        default="Linear", description="Material model for SLS")
    plastic_strain_limit: float = dataclass_field(
        default=0.002, description="Plastic strain limit for SLS")
    failure_compression_limit: float = dataclass_field(
        default=0.003, description="Failure compression limit for SLS")
    material_model_tension: str = dataclass_field(
        default="interpolated", description="Material model for SLS tension")
    failure_tension_limit: float = dataclass_field(
        default=0.003, description="Failure tension limit for SLS")

    class Config(MBaseModel.Config):
        title = "GSD Concrete Stress Options for SLS"

# ==== Rebar & Tendon Materials ====
class RebarGrade(MBaseModel):
    """
    GSD rebar grade class
    
    Args:
        design_code (str): Design code
        grade (str): Grade of the rebar
    """
    design_code: str = dataclass_field(
        default="ACI318M-19", description="Design code")
    grade: str = dataclass_field(
        default="Grade 420", description="Grade of the rebar")

    class Config(MBaseModel.Config):
        title = "GSD Rebar Grade"

class TendonGrade(MBaseModel):
    """
    GSD Tendon grade class
    
    Args:
        design_code (str): Design code
        grade (str): Grade of the tendon
    """
    design_code: str = dataclass_field(
        default="ACI318M-19", description="Design code")
    grade: str = dataclass_field(default="Grade 420", description="Grade of the tendon")

    class Config(MBaseModel.Config):
        title = "GSD Tendon Grade"

class RebarProp(MBaseModel):
    """
    GSD rebar prop
    
    Args:
        area (float): Area of the rebar
        material (RebarGrade): Material of the rebar
    """
    area: float = dataclass_field(default=287.0, description="Area of the rebar")
    material: RebarGrade = dataclass_field(default=RebarGrade(), description="Material of the rebar")

    class Config(MBaseModel.Config):
        title = "GSD Rebar Properties"

class TendonProp(MBaseModel):
    """
    GSD Tendon prop
    
    Args:
        area (float): Area of the tendon
        material (TendonGrade): Material of the tendon
        prestress (float): Prestress of the tendon
    """
    area: float = dataclass_field(default=287.0, description="Area of the tendon")
    material: TendonGrade = dataclass_field(default=TendonGrade(), description="Material of the tendon")
    prestress: float = dataclass_field(default=0.0, description="Prestress of the tendon")

    class Config(MBaseModel.Config):
        title = "GSD Tendon Properties"

class Rebar_General_Properties(MBaseModel):
    """
    GSD rebar general properties for calculation
    
    Args:
        strength (int): Grade of the rebar
        elastic_modulus (float): Elastic modulus of the rebar
        density (float): Density of the rebar
        thermal_expansion_coefficient (float): Thermal expansion coefficient of the rebar
        poisson_ratio (float): Poisson ratio of the rebar
    """
    strength: int = dataclass_field(
        default=420, description="Grade of the rebar")
    elastic_modulus: float = dataclass_field(
        default=200000, description="Elastic modulus of the rebar")
    density: float = dataclass_field(
        default=7850, description="Density of the rebar")
    thermal_expansion_coefficient: float = dataclass_field(
        default=0.00001, description="Thermal expansion coefficient of the rebar")
    poisson_ratio: float = dataclass_field(
        default=0.3, description="Poisson ratio of the rebar")

    class Config(MBaseModel.Config):
        title = "GSD Rebar General Properties"

class Rebar_Stress_ULS_Options_ACI(MBaseModel):
    """
    GSD rebar stress options for ULS
    
    Args:
        material_model (str): Material model for ULS
        failure_strain (float): Failure strain limit for ULS
    """
    material_model: str = dataclass_field(
        default="Elastic-Plastic", description="Material model for ULS")
    failure_strain: float = dataclass_field(
        default=0.7, description="Failure strain limit for ULS")

    class Config(MBaseModel.Config):
        title = "GSD Rebar Stress Options for ULS"

class Rebar_Stress_SLS_Options(MBaseModel):
    """
    GSD rebar stress options for SLS
    
    Args:
        material_model (str): Material model for SLS
        failure_strain (float): Failure strain limit for SLS
    """
    material_model: str = dataclass_field(
        default="Elastic-Plastic", description="Material model for SLS")
    failure_strain: float = dataclass_field(
        default=0.7, metadata={"default" : 0.7, "description": "Failure strain limit for SLS"})

    class Config(MBaseModel.Config):
        title = "GSD Rebar Stress Options for SLS"

class MaterialRebar(MBaseModel):
    """
    GSD rebar class
    
    Args:
        grade (RebarGrade): Grade of the rebar
        curve_uls (list[Stress_Strain_Component]): Stress strain curve for ULS
        curve_sls (list[Stress_Strain_Component]): Stress strain curve for SLS
    """
    grade: RebarGrade = dataclass_field(
        default=RebarGrade(), description="Grade of the rebar")
    curve_uls: list[Stress_Strain_Component] = dataclass_field(default=[Stress_Strain_Component(strain=0.0, stress=0.0), Stress_Strain_Component(strain=0.0025, stress=500.0), Stress_Strain_Component(strain=0.05, stress=500.0)], description="Stress strain curve")
    curve_sls: list[Stress_Strain_Component] = dataclass_field(default=[Stress_Strain_Component(strain=0.0, stress=0.0), Stress_Strain_Component(strain=0.0025, stress=500.0), Stress_Strain_Component(strain=0.05, stress=500.0)], description="Stress strain curve")

    class Config(MBaseModel.Config):
        title = "GSD Material Rebar"

class MaterialTendon(MBaseModel):
    """
    GSD tendon class
    
    Args:
        grade (TendonGrade): Grade of the tendon
        curve_uls (list[Stress_Strain_Component]): Stress strain curve for ULS
        curve_sls (list[Stress_Strain_Component]): Stress strain curve for SLS
    """
    grade: TendonGrade = dataclass_field(default=TendonGrade(), description="Grade of the tendon")
    curve_uls: list[Stress_Strain_Component] = dataclass_field(default=[Stress_Strain_Component(strain=0.0, stress=0.0), Stress_Strain_Component(strain=0.00725, stress=1450.0), Stress_Strain_Component(strain=0.05, stress=1750.0)], description="Stress strain curve")
    curve_sls: list[Stress_Strain_Component] = dataclass_field(default=[Stress_Strain_Component(strain=0.0, stress=0.0), Stress_Strain_Component(strain=0.00725, stress=1450.0), Stress_Strain_Component(strain=0.05, stress=1750.0)], description="Stress strain curve")

    class Config(MBaseModel.Config):
        title = "GSD Material Tendon"

class MaterialConcrete(MBaseModel):
    """
    GSD material for Concrete class
    
    Args:
        grade (ConcreteGrade): Grade of the concrete
        curve_uls (list[Stress_Strain_Component]): Stress strain curve concrete ULS
        curve_sls (list[Stress_Strain_Component]): Stress strain curve
    """
    grade: ConcreteGrade = dataclass_field(
        default=ConcreteGrade(), description="Grade of the concrete")
    curve_uls: list[Stress_Strain_Component] = dataclass_field(default=[Stress_Strain_Component(strain=0.0, stress=0.0), Stress_Strain_Component(strain=0.0006, stress=0.0), Stress_Strain_Component(strain=0.0006, stress=34.0), Stress_Strain_Component(strain=0.003, stress=34.0)], description="Stress strain curve concrete ULS")
    curve_sls: list[Stress_Strain_Component] = dataclass_field(default=[Stress_Strain_Component(strain=0.0, stress=0.0), Stress_Strain_Component(strain=0.001, stress=32.8)], description="Stress strain curve")

    class Config(MBaseModel.Config):
        title = "GSD Material Concrete"

class Material(MBaseModel):
    """
    GSD concrete class

    Args:
        concrete (MaterialConcrete): Concrete properties
        rebar (MaterialRebar): Rebar properties
        tendon (MaterialTendon): Tendon properties
    """
    concrete: MaterialConcrete = dataclass_field(default=MaterialConcrete(), description="Concrete properties")
    rebar: Optional[MaterialRebar] = dataclass_field(default=MaterialRebar(), description="Rebar properties")
    tendon: Optional[MaterialTendon] = dataclass_field(default=MaterialTendon(), description="Tendon properties")

    def __post_init__(self):
        if self.rebar is None and self.tendon is None:
            raise ValueError("Either rebar or tendon must be provided.")

    class Config(MBaseModel.Config):
        title = "GSD Material"

# ==== Geometry ====
class Point(MBaseModel):
    """
    Point class
    
    Args:
        x (float): x-coordinate
        y (float): y-coordinate
    """
    x: float
    y: float

    class Config(MBaseModel.Config):
        title = "Point"

class Points(MBaseModel):
    """
    GSD Points class

    Args:
        points (list[Point]): Points
    """
    points: list[Point] = dataclass_field(default=[Point(x=0.0, y=0.0), Point(x=400.0, y=0.0), Point(x=400.0, y=600.0), Point(x=0.0, y=600.0)], description="Points")

    class Config(MBaseModel.Config):
        title = "GSD Points"

class OuterPolygon(MBaseModel):
    """
    GSD Outer Polygon class

    Args:
        points (list[Point]): Points
    """
    points: list[Point] = dataclass_field(default=[Point(x=0.0, y=0.0), Point(x=400.0, y=0.0), Point(x=400.0, y=600.0), Point(x=0.0, y=600.0)], description="Outer Polygon")

    class Config(MBaseModel.Config):
        title = "GSD Outer Polygon"

class InnerPolygon(MBaseModel):
    """
    GSD Inner Polygon class

    Args:
        points (list[Point]): Points
    """
    points: list[Point] = dataclass_field(default=[Point(x=0.0, y=0.0), Point(x=400.0, y=0.0), Point(x=400.0, y=600.0), Point(x=0.0, y=600.0)], description="Inner Polygon")

    class Config(MBaseModel.Config):
        title = "GSD Inner Polygon"

class ConcreteGeometry(MBaseModel):
    """
    GSD concrete geometry class
    
    Args:
        material (ConcreteGrade): Material of the concrete
        outerPolygon (list[Point]): Outer polygon of the concrete
        innerPolygon (list[Point]): Inner polygon of the concrete
    """
    material: ConcreteGrade = dataclass_field(default=ConcreteGrade(), description="Material of the concrete")
    outerPolygon: list[Point] = dataclass_field(default=[Point(x=0.0, y=0.0), Point(x=400.0, y=0.0), Point(x=400.0, y=600.0), Point(x=0.0, y=600.0)], description="Outer polygon of the concrete")
    innerPolygon: list[Point] = dataclass_field(default=[Point(x=80.0, y=80.0), Point(x=320.0, y=80.0), Point(x=320.0, y=520.0), Point(x=80.0, y=520.0)], description="Inner polygon of the concrete")

    class Config(MBaseModel.Config):
        title = "GSD Concrete Geometry"

class RebarGeometry(MBaseModel):
    """
    GSD rebar geometry class

    Args:
        prop (RebarProp): properties of the rebar
        points (list[Point]): Rebar Points
    """
    prop: RebarProp = dataclass_field(default=RebarProp(), description="properties of the rebar")
    points: list[Point] = dataclass_field(default=[Point(x=40.0, y=40.0), Point(x=360.0, y=40.0), Point(x=360.0, y=560.0), Point(x=40.0, y=560.0)], description="Rebar Points")

    class Config(MBaseModel.Config):
        title = "GSD Rebar Geometry"

class TendonGeometry(MBaseModel):
    """
    GSD tendon geometry class
    
    Args:
        prop (TendonProp): properties of the tendon
        points (list[Point]): Tendon Points
    """
    prop: TendonProp = dataclass_field(default=TendonProp(), description="properties of the tendon")
    points: list[Point] = dataclass_field(default=[], description="Tendon Points")

    class Config(MBaseModel.Config):
        title = "GSD Tendon Geometry"

class Geometry(MBaseModel):
    """
    GSD geometry class
    
    Args:
        concrete (ConcreteGeometry): Concrete geometry
        rebar (RebarGeometry): Rebar geometry
        tendon (TendonGeometry): Tendon geometry
    """
    concrete: ConcreteGeometry = dataclass_field(default=ConcreteGeometry(), description="Concrete geometry")
    rebar: Optional[RebarGeometry] = dataclass_field(default=RebarGeometry(), description="Rebar geometry")
    tendon: Optional[TendonGeometry] = dataclass_field(default=TendonGeometry(), description="Tendon geometry")

    class Config(MBaseModel.Config):
        title = "GSD Geometry"

class Lcb(MBaseModel):
    """
    GSD load combination class
    
    Args:
        uls (Lcoms): uls load combination
    """
    uls: Lcoms = dataclass_field(default=Lcoms(), description="uls load combination")

    class Config(MBaseModel.Config):
        title = "GSD Load Combination"

class enDgnCode(Enum):
    """
    Enum for Design Code
    """
    ACI318M_19 = "ACI318M-19"
    Eurocode2_04 = "Eurocode2-04"

class enEccPu(Enum):
    """
    Enum for Design Code
    """
    ecc = "ecc"
    p_u = "P-U"

# Enum 값을 리스트로 변환하는 함수
def enum_to_list(enum_class):
    return [member.value for member in enum_class]

# ==== options ====
class PMOptions(MBaseModel):
    """
    GSD options class
    
    Args:
        dgncode (str): Design code
        by_ecc_pu (str): ecc
    """
    dgncode: str = dataclass_field(default=enDgnCode.Eurocode2_04, description="Design code", enum=enum_to_list(enDgnCode))
    by_ecc_pu: str = dataclass_field(default="ecc", description="ecc or P-U", enum=enum_to_list(enEccPu))

    class Config(MBaseModel.Config):
        title = "GSD Options"

# ==== functions ====
@auto_schema
def conc_properties_design(
    general: Concrete_General_Properties,
    uls: Concrete_Stress_ULS_Options_ACI,
    sls: Concrete_SLS_Options
) -> MaterialConcrete:
    """
    Return the concrete material properties based on the design code

    Args:
        general: general concrete properties
        uls: concrete stress options for ULS
        sls: concrete stress options for SLS

    return:
        MaterialConcrete: material properties of selected data
    """
    if general is None:
        general = Concrete_General_Properties()
    if uls is None:
        uls = Concrete_Stress_ULS_Options_ACI()
    if sls is None:
        sls = Concrete_SLS_Options()

    if uls.material_model == 'Rectangle':
        _uls_strains = [
            0,
            uls.compressive_failure_strain * (1 - uls.factor_b1),
            uls.compressive_failure_strain * (1 - uls.factor_b1),
            uls.compressive_failure_strain,
        ]
        _uls_stress = [
            0,
            0,
            uls.factor_b1 * general.strength,
            uls.factor_b1 * general.strength,
        ]

    if sls.material_model == 'Linear':
        _sls_strains = [
            0,
            sls.failure_compression_limit,
        ]
        _sls_stress = [
            0,
            general.strength,
        ]

    ss_uls_components = [Stress_Strain_Component(stress=_uls_stress[i], strain=_uls_strains[i]) for i in range(len(_uls_strains))]
    ss_sls_components = [Stress_Strain_Component(stress=_sls_stress[i], strain=_sls_strains[i]) for i in range(len(_sls_strains))]
    return MaterialConcrete(curve_uls=ss_uls_components, curve_sls=ss_sls_components)

@auto_schema
def rebar_properties_design(
    general: Rebar_General_Properties,
    uls: Rebar_Stress_ULS_Options_ACI,
    sls: Rebar_Stress_SLS_Options
) -> MaterialRebar:
    """
    Return the material properties based on the design code

    Args:
        general: general rebar properties
        uls: rebar stress options for ULS
        sls: rebar stress options for SLS

    return:
        MaterialRebar: material properties of selected data
    """
    yield_strain = general.strength / general.elastic_modulus

    _sls_strains = [
        0,
        yield_strain,
        sls.failure_strain
    ]
    _sls_stress = [
        0,
        general.strength,
        general.strength,
    ]

    _uls_strains = [
        0,
        yield_strain,
        uls.failure_strain
    ]
    _uls_stress = [
        0,
        general.strength,
        general.strength
    ]

    ss_uls_components = [Stress_Strain_Component(stress=_uls_stress[i], strain=_uls_strains[i]) for i in range(len(_uls_strains))]
    ss_sls_components = [Stress_Strain_Component(stress=_sls_stress[i], strain=_sls_strains[i]) for i in range(len(_sls_strains))]

    return MaterialRebar(curve_uls=ss_uls_components, curve_sls=ss_sls_components)

class MSection:
    def __init__(self, matl=Material, geom=Geometry):
        if hasattr(matl, "concrete"):
            self.conc = matl.concrete
            if self.conc is not None:
                self.concrete_material_uls = self.conc.curve_uls
                self.concrete_material_sls = self.conc.curve_sls

        if hasattr(matl, "rebar"):
            self.rebar = matl.rebar
            if self.rebar is not None:
                self.rebar_material_uls = self.rebar.curve_uls
                self.rebar_material_sls = self.rebar.curve_sls

        if hasattr(matl, "tendon"):
            self.tendon = matl.tendon
            if self.tendon is not None:
                self.tendon_material_uls = self.tendon.curve_uls
                self.tendon_material_sls = self.tendon.curve_sls

        self.geom = geom
        if self.geom is not None:
            self.concrete_geom = self.geom.concrete
            if hasattr(self.geom, "rebar"):
                self.rebar_geom = self.geom.rebar

            if hasattr(self.geom, "tendon"):
                self.tendon_geom = self.geom.tendon

    def get_concrete_material_curve(self, type_):
        if type_ == "uls":
            curve_data = self.concrete_material_uls
        elif type_ == "sls":
            curve_data = self.concrete_material_sls

        return [component.stress for component in curve_data], [component.strain for component in curve_data]

    def get_rebar_material_curve(self, type_):
        if type_ == "uls":
            curve_data = self.rebar_material_uls
        elif type_ == "sls":
            curve_data = self.rebar_material_sls

        return [component.stress for component in curve_data], [component.strain for component in curve_data]

    def get_tendon_material_curve(self, type_):
        if type_ == "uls":
            curve_data = self.tendon_material_uls
        elif type_ == "sls":
            curve_data = self.tendon_material_sls

        return [component.stress for component in curve_data], [component.strain for component in curve_data]

    def get_concrete_geom(self):
        return self.concrete_geom

    def get_rebar_geom(self):
        if hasattr(self, 'rebar_geom'):
            return self.rebar_geom
        return None

    def get_tendon_geom(self):
        if hasattr(self, 'tendon_geom'):
            if (self.tendon_geom.points is not None) and (len(self.tendon_geom.points) > 0):
                return self.tendon_geom

        return None

    def check_data(self):
        if self.conc is None or self.geom is None:
            return "Data is not enough."

        return True

    def compound_section(
        self,
        concrete: list[dict],
        rebar: list[dict],
        tendon: list[dict],
        conc_mat: pre.Material = pre.DEFAULT_MATERIAL,
        steel_mat: pre.Material = pre.DEFAULT_MATERIAL,
        tendon_mat: pre.Material = pre.DEFAULT_MATERIAL
    ) -> geometry.CompoundGeometry:
        def convert_points_to_list(points):
            return [[point.x, point.y] for point in points]

        outpolygon = Polygon(convert_points_to_list(concrete.outerPolygon))
        outer = geometry.Geometry(geom=outpolygon, material=conc_mat)
        if (concrete.innerPolygon is not None) and (len(concrete.innerPolygon) > 0):
            inpolygon = Polygon(convert_points_to_list(concrete.innerPolygon))
            inner = geometry.Geometry(geom=inpolygon).align_center(align_to=outer)
            concrete_geometry = outer - inner
        else:
            concrete_geometry = outer

        # cnosider rebar
        if rebar is not None:
            area = rebar.prop.area
            posi = rebar.points
            trans_pos = convert_points_to_list(posi)

            for x, y in trans_pos:
                concrete_geometry = add_bar(
                    geometry=concrete_geometry,
                    area=area,
                    material=steel_mat,
                    x=x,
                    y=y,
                    n=4
                )

        # consider tendon
        if tendon is not None:
            t_area = tendon.prop.area
            t_posi = tendon.points
            t_trans_pos = convert_points_to_list(t_posi)

            for x, y in t_trans_pos:
                concrete_geometry = add_bar(
                    geometry=concrete_geometry,
                    area=t_area,
                    material=tendon_mat,
                    x=x,
                    y=y,
                )

        if isinstance(concrete_geometry, geometry.CompoundGeometry):
            return concrete_geometry
        else:
            raise ValueError("Concrete section generation failed.")

    def has_rebar(self):
        hasRebar = True if self.get_rebar_geom() is not None else False
        return hasRebar

    def calc_compound_section(self):
        ecu = 0.003
        esu = 0.05
        fck = 30.0

        ss_uls = self.get_concrete_material_curve("uls")
        ss_sls = self.get_concrete_material_curve("sls")
        ss_conc_uls = ssp.ConcreteUltimateProfile(stresses=ss_uls[0], strains=ss_uls[1], compressive_strength=fck)
        ss_conc_ser = ssp.ConcreteServiceProfile(stresses=ss_sls[0], strains=ss_sls[1], ultimate_strain=ecu)

        # ss_rebar_uls = ssp.StressStrainProfile(self.get_rebar_material_curve("uls")["Strain"], self.get_rebar_material_curve("uls")["Stress"])
        # ss_rebar_sls = ssp.StressStrainProfile(self.get_rebar_material_curve("sls")["Strain"], self.get_rebar_material_curve("sls")["Stress"])

        concrete_matl = Concrete(
            name=self.conc.grade.grade,
            density=2.4e-6,
            stress_strain_profile=ss_conc_ser,
            ultimate_stress_strain_profile=ss_conc_uls,
            flexural_tensile_strength=0.6 * np.sqrt(40),
            colour="lightgrey",
        )

        if hasattr(self, 'rebar'):
            steel_matl = SteelBar(
                name=self.rebar.grade.grade,
                density=7.85e-6,
                stress_strain_profile=ssp.SteelElasticPlastic(
                    yield_strength=500,
                    elastic_modulus=200e3,
                    fracture_strain=esu,
                ),
                colour="grey",
            )
        else:
            steel_matl = None

        if hasattr(self, 'tendon_geom'):
            tendon_matl = SteelStrand(
                name="1830 MPa Strand",
                density=7.85e-6,
                stress_strain_profile=ssp.StrandHardening(
                    yield_strength=1500,
                    elastic_modulus=200e3,
                    fracture_strain=0.035,
                    breaking_strength=1830,
                ),
                colour="slategrey",
                prestress_stress=self.tendon_geom.prop.prestress,
            )
        else:
            tendon_matl = None

        # reference geometry
        compound_sect = self.compound_section(self.get_concrete_geom(), self.get_rebar_geom(), self.get_tendon_geom(), concrete_matl, steel_matl, tendon_matl)
        if self.get_tendon_geom() is not None:
            compSect = PrestressedSection(compound_sect)
        else:
            compSect = ConcreteSection(compound_sect)

        return compSect

class PM3DCurve:
    """
    Class for PM3D Curve Calculation

    Args:
        matl (Material): Material properties
        geom (Geometry): Geometry properties
        opt (PMOptions
    """
    def __init__(self, matl=Material, geom=Geometry, opt=PMOptions):
        self.sect = MSection(matl, geom)
        self.option = opt

    def get_option_by_ecc_pu(self):
        return self.option.by_ecc_pu

    # TODO Tendon 만 있을 경우 Cb값에 대해 처리해줘야되나?
    def get_Cb(self, sect, theta_rad, ecu, esu):
        d_ext, _ = sect.extreme_bar(theta=theta_rad)
        return (ecu / (ecu + esu)) * d_ext

    def calc_compound_section(self):
        return self.sect.calc_compound_section()

    def make_3dpm_data(self):
        # TODO 이 변수들 지걸로 맞춰줘야되!!
        beta1 = 0.8
        ecu = 0.003
        esu = 0.05
        comp_sect = self.calc_compound_section()

        hasRebar = self.sect.has_rebar()

        results = []
        theta_range = np.arange(0.0, 361.0, 15.0).tolist()

        for theta in theta_range:
            theta_rad = np.radians(theta)
            x11_max, x11_min, y22_max, y22_min = utils.calculate_local_extents( 
                geometry=comp_sect.compound_geometry,
                cx=comp_sect.gross_properties.cx,
                cy=comp_sect.gross_properties.cy,
                theta=theta_rad
            )

            C_Max = abs(y22_max - y22_min) / beta1
            d_n_range = np.linspace(0.01, C_Max * 1.1, 10).tolist()  # numpy 배열을 float 리스트로 변환

            if hasRebar is True:
                Cb = self.get_Cb(comp_sect, theta_rad, ecu, esu)
                d_n_range.append(Cb)

            for d_n in d_n_range:
                res = concreteproperties.results.UltimateBendingResults(theta_rad)
                res = comp_sect.calculate_ultimate_section_actions(d_n, res)
                results.append(res)

        return results

class DgnCode(ABC):
    """
    Class for Design Code
    """
    def __init__(self) -> None:
        pass

    @abstractmethod
    def make_3dpm_data(self, material: Material, geometry: Geometry, opt: PMOptions):
        pm = PM3DCurve(material, geometry, opt)
        return pm.make_3dpm_data()

    def get_option_by_ecc_pu(self, opt: PMOptions):
        return opt.by_ecc_pu

    def calc_compound_section(self, material: Material, geometry: Geometry, opt: PMOptions = None):
        if opt is None:
            opt = PMOptions()

        pm = PM3DCurve(material, geometry, opt)
        return pm.calc_compound_section()

class DgnCodeUS(DgnCode):
    """
    Class for Design Code US
    """
    def __init__(self) -> None:
        super().__init__()

    def make_3dpm_data(self, material: Material, geometry: Geometry, opt: PMOptions):
        res = super().make_3dpm_data(material, geometry, opt)
        # 원래 데이터를 갖고 있는게 좋을지는 기획 내용에 따라 다를 수 있음
        pnmax = max(res, key=lambda x: x.n).n
        pnmax *= 0.8
        for result in res:
            _et = 0.003 * (result.k_u**-1 - 1.0)
            _phi_tens = 0.85
            _phi_comp = 0.65
            _e_tens = 0.005
            _e_comp = 0.002
            if _et >= _e_tens:
                phi = _phi_tens
            elif _et <= _e_comp:
                phi = _phi_comp
            else:
                phi = _phi_comp + (_phi_tens - _phi_comp) * (_e_tens - _e_comp) / (_e_tens - _e_comp)

            _tmp = result.n * phi
            result.n = min(_tmp, pnmax)
            result.m_x *= phi
            result.m_y *= phi
            result.m_xy *= phi

        return res

class DgnCodeEU(DgnCode):
    """
    Class for Design Code EU
    """
    def __init__(self) -> None:
        super().__init__()

    def make_3dpm_data(self, material: Material, geometry: Geometry, opt: PMOptions):
        return super().make_3dpm_data(material, geometry, opt)

class ResultCrackedProperties(MBaseModel):
    """
    Class for Cracked Properties
    """
    d_nr: float = dataclass_field(default=0.0, description="neutral axis depth")
    i_cr: float = dataclass_field(default=0.0, description="cracked inertia")

def get_dgncode(dgncode: str):
    if dgncode == "ACI318M-19":
        return DgnCodeUS()
    else:
        return DgnCodeEU()

@auto_schema
def make_3dpm(material: Material, geometry: Geometry, opt: PMOptions):
    """
    3D Axial-Moment Curvature Analysis
    
    Args:
        material: Material
        geometry: Geometry
        opt: PMOptions
        
    Returns:
        list[UltimateBendingResults]: 3D Axial-Moment Curvature Analysis results
    """
    pm = get_dgncode(opt.dgncode)
    results = pm.make_3dpm_data(material, geometry, opt)
    return results

@auto_schema
def calc_3dpm(material: Material, geometry: Geometry, lcb: Lcb, opt: PMOptions) -> Result3DPM:
    """
    Return the 3D PM Curve & norminal strength points

    Args:
        material: Material
        geometry: Geometry
        lcb: Lcb
        opt: PMOptions

    return:
        Result3DPM: 3DPM curve & norminal strength points about lcom
    """
    results = make_3dpm(material, geometry, opt)

    d_n_values = [result.n for result in results]
    m_x_values = [result.m_x for result in results]
    m_y_values = [result.m_y for result in results]

    points = np.column_stack((m_x_values, m_y_values, d_n_values))
    hull = ConvexHull(points)
    mesh1 = trimesh.Trimesh(vertices=hull.points, faces=hull.simplices)
    ray = trimesh.ray.ray_pyembree.RayMeshIntersector(mesh1)

    result_lcom_uls = []
    lcoms_uls = []
    for lcom in lcb.uls.lcoms:
        lcom_name = lcom.name
        lcom_point = [lcom.f.Mx, lcom.f.My, lcom.f.Nz]

        if opt.by_ecc_pu == "ecc":
            origin = np.array([0, 0, 0])
        else:
            origin = np.array([0, 0, lcom_point[2]])

        direction = lcom_point - origin
        direction = direction / np.linalg.norm(direction)

        locations, index_ray, index_tri = ray.intersects_location(
            ray_origins=np.array([origin]),
            ray_directions=np.array([direction])
        )

        lcoms_uls.append(lcom)
        result_lcom_uls.append(Lcom(name=lcom_name, f=Force(Nz=locations[0, 2], Mx=locations[0, 0], My=locations[0, 1])))

    meshres = []
    for i in range(len(hull.points)):
        meshres.append(Force(Mx=hull.points[i][0], My=hull.points[i][1], Nz=hull.points[i][2]))

    meshData = Mesh3DPM(mesh3dpm=meshres)
    return Result3DPM(meshes=meshData, lcbs=lcoms_uls, strength=result_lcom_uls)

# dummy functions
@auto_schema
def concrete_geometry(outerPolygon: OuterPolygon, innerPolygon: InnerPolygon, matl: ConcreteGrade) -> ConcreteGeometry:
    """Return the concrete geometry
    
    Args:
        outerPolygon (OuterPolygon): outer polygon of the concrete
        innerPolygon (InnerPolygon): inner polygon of the concrete
        matl (ConcreteGrade): material of the concrete
    """
    return ConcreteGeometry(outerPolygon=outerPolygon.points, innerPolygon=innerPolygon.points, material=matl)

@auto_schema
def rebar_geometry(position: Points, prop: RebarProp) -> RebarGeometry:
    """Return the rebar geometry
    
    Args:
        position (Points): rebar position
        prop (RebarProp): rebar properties
    
    Returns:
        RebarGeometry: rebar geometry
    """
    return RebarGeometry(position=position.points, prop=prop)

@auto_schema
def tendon_geometry(points: Points, prop: TendonProp) -> TendonGeometry:
    """Return the tendon geometry
    
    Args:
        position (Points): tendon position
        prop (TendonProp): tendon properties
        
    Returns:
        TendonGeometry: tendon geometry
    """
    return TendonGeometry(points=points.points, prop=prop)

@auto_schema
def geometry_design(concrete: ConcreteGeometry, rebar: RebarGeometry) -> Geometry:
    """Return the geometry
    
    Args:
        concrete (ConcreteGeometry): concrete geometry
        rebar (RebarGeometry): rebar geometry
    
    Returns:
        Geometry: geometry
    """
    return Geometry(concrete=concrete, rebar=rebar)

@auto_schema
def material_properties_design(conc: MaterialConcrete, rebar: MaterialRebar) -> Material:
    """Return the material properties
    
    Args:
        conc (MaterialConcrete): concrete properties
        rebar (MaterialRebar): rebar properties
    
    Returns:
        Material: material properties
    """
    return Material(concrete=conc, rebar=rebar)

@auto_schema
def lcom_design(uls: Lcoms) -> Lcb:
    """Return the load combination
    
    Args:
        uls (Lcoms): uls load combination
    Returns:
        Lcb: load combination
    """
    return Lcb(uls=uls)

@auto_schema
def options_design(opt: PMOptions) -> PMOptions:
    """Return the options
    
    Args:
        opt (PMOptions): options
    
    Returns:
        PMOptions: options
    """
    return PMOptions(dgncode=opt.dgncode, by_ecc_pu=opt.by_ecc_pu)

# res = rebar_geometry(**{
#   "position": {
#     "points": [
#       {
#         "x": 0,
#         "y": 0
#       },
#       {
#         "x": 400,
#         "y": 0
#       },
#       {
#         "x": 400,
#         "y": 600
#       },
#       {
#         "x": 0,
#         "y": 600
#       }
#     ]
#   },
#   "prop": {
#     "area": 287,
#     "material": {
#       "design_code": "ACI318M-19",
#       "grade": "Grade 420"
#     }
#   }
# })

# print(res)

# _material = Material()
# _geometry = Geometry()
# _lcb = Lcb()
# res=calc_uncracked_stress(_material, _geometry,_lcb)
# print(res)

# from dataclasses import dataclass, asdict
# res = MaterialRebar()
# data_dict = [component.__dict__ for component in res.curve_uls]
# print(data_dict)

# res = calc_3dpm(Material(), Geometry(), Lcb(), PMOptions())
# print(res)