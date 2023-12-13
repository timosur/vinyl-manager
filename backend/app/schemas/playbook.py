from pydantic import BaseModel
from typing import Any, Optional

class PlaybookFormData(BaseModel):
    numberOfWTGs: Any
    wtgCapacity: float
    region: str
    foundationType: str
    oem: str
    numberOfSubstations: int
    distanceFromOMPort: float
    operationalPeriod: str
    omGlobalStrategy: str
    rweShareholding: float

class CalculationResult(BaseModel):
    lifetime_cost_average: float
    wtg_cost_per_year: float
    mw_cost_per_year: float
    tba: str
    pba: str

class ProjectSchema(BaseModel):
    id: int
    project_name: str
    date_year: int
    number_of_wtgs: int
    oem: str
    wtg_capacity_mw: float
    region: str
    foundation_type: str
    number_of_substations: int
    distance_from_port_km: float
    lifetime_years: int
    annual_cost_per_wtg_eur: float
    annual_cost_per_mw_eur: float
    tba_percent: float
    pba_percent: float
    project_development_stage: str
    weight: Optional[float]  # Using Optional because 'weight' can be null