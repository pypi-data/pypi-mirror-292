from __future__ import annotations
import typing as t
from pydantic import BaseModel
from .unit_types import kW, V, dec, Wm2, deg, degC, kWh, Whm2, m2
from .generation_models import SolarResource


class BaseTimeSeries(BaseModel):
    r""":meta private:"""

    def default_include(self):
        r""":meta private:"""
        return {k: True for k in self.schema()["required"]}


class BusTimeSeries(BaseTimeSeries):
    r"""-"""

    power: t.List[kW]


class DCBusTimeSeries(BusTimeSeries):
    r"""-"""

    voltage: t.List[V]


class InverterTimeSeries(BaseTimeSeries):
    r"""-"""

    clipping_loss: t.List[kW]

    efficiency: t.List[dec]

    tare_loss: t.List[kW]

    consumption_loss: t.List[kW]


class TransformerTimeSeries(BaseTimeSeries):
    r"""-"""

    total_loss: t.List[kW]

    load_loss: t.Optional[t.List[kW]]

    no_load_loss: t.Optional[t.List[kW]]


class ACWiringTimeSeries(BaseTimeSeries):
    r"""-"""

    loss: t.List[kW]


class TransmissionTimeSeries(BaseTimeSeries):
    r"""-"""

    loss: t.List[kW]


class POITimeSeries(BaseTimeSeries):
    r"""-"""

    power_pre_clip: t.List[kW]

    power_pre_adjustment: t.List[kW]

    power: t.List[kW]

    power_positive: t.List[kW]

    power_negative: t.List[kW]


class PVTimeSeries(BaseTimeSeries):
    r"""-"""

    ghi: t.List[Wm2]

    tracker_rotation_angle: t.Optional[t.List[deg]]

    front_poa_nominal: t.Optional[t.List[Wm2]]

    front_poa_shaded: t.Optional[t.List[Wm2]]

    front_poa_shaded_soiled: t.Optional[t.List[Wm2]]

    front_poa: t.List[Wm2]

    rear_poa: t.List[Wm2]

    poa_effective: t.List[Wm2]

    poa_effective_power: t.Optional[t.List[kW]]

    cell_temperature_quasi_steady: t.Optional[t.List[degC]]

    cell_temperature: t.Optional[t.List[degC]]

    module_efficiency: t.Optional[t.List[dec]]

    dc_shading_loss: t.Optional[t.List[kW]]

    dc_snow_loss: t.Optional[t.List[kW]]

    mppt_window_loss: t.Optional[t.List[kW]]

    gross_dc_power: t.List[kW]

    dc_power_undegraded: t.Optional[t.List[kW]]

    dc_power: t.Optional[t.List[kW]]

    dc_voltage: t.Optional[t.List[V]]


class Year1Waterfall(BaseModel):
    r""":meta private:"""

    dc_bus_energy: t.Optional[kWh]
    inverter_clipping: t.Optional[dec]
    inverter_consumption: t.Optional[dec]
    inverter_tare: t.Optional[dec]
    inverter_efficiency: t.Optional[dec]
    lv_bus_energy: t.Optional[kWh]
    mv_transformer: t.Optional[dec]
    mv_bus_energy: t.Optional[kWh]
    ac_wiring: t.Optional[dec]
    hv_transformer: t.Optional[dec]
    export_bus_energy: kWh
    transmission: dec
    poi_clipping: dec
    poi_adjustment: dec
    poi_energy: kWh


class GenerationYear1Waterfall(Year1Waterfall):
    r"""-"""

    ghi: t.Optional[Whm2]
    front_transposition: t.Optional[dec]
    front_shading: t.Optional[dec]
    front_soiling: t.Optional[dec]
    front_iam: t.Optional[dec]
    rear_poa: t.Optional[dec]
    rear_bifaciality: t.Optional[dec]
    poa_effective: t.Optional[Whm2]
    array_area: t.Optional[m2]
    poa_effective_energy: t.Optional[kWh]
    stc_pv_module_effeciency: t.Optional[dec]
    pv_dc_nominal_energy: t.Optional[kWh]
    non_stc_irradiance_temperature: t.Optional[dec]
    r"""this includes DC derate due to beam shading (electrical effect), will be broken out in the future"""
    mppt_clip: t.Optional[dec]
    snow: t.Optional[dec]
    pv_dc_gross_energy: t.Optional[kWh]
    nameplate: t.Optional[dec]
    lid: t.Optional[dec]
    mismatch: t.Optional[dec]
    diodes: t.Optional[dec]
    dc_optimizer: t.Optional[dec]
    tracking_error: t.Optional[dec]
    dc_wiring: t.Optional[dec]
    dc_adjustment: t.Optional[dec]


class GenerationPowerFlowTimeSeries(BaseModel):
    r"""-"""

    pv: t.Optional[PVTimeSeries]

    dc_bus: t.Optional[DCBusTimeSeries]

    inverter: t.Optional[InverterTimeSeries]

    lv_bus: t.Optional[BusTimeSeries]

    mv_xfmr: t.Optional[TransformerTimeSeries]

    mv_bus: t.Optional[BusTimeSeries]

    ac_wiring: t.Optional[ACWiringTimeSeries]

    hv_xfmr: t.Optional[TransformerTimeSeries]

    export_bus: BusTimeSeries

    transmission: TransmissionTimeSeries

    poi: POITimeSeries

    def default_include(self):
        r""":meta private:"""
        return {k: getattr(self, k).default_include() for k in self.dict(exclude_none=True).keys()}


class GenerationModelResults(BaseModel):
    r"""Results schema returned when a
    :class:`~generation_models.generation_models.generation_models.PVGenerationModel`,
    :class:`~generation_models.generation_models.generation_models.ACExternalGenerationModel` or
    :class:`~generation_models.generation_models.generation_models.DCExternalGenerationModel` simulation is run"""

    power_flow: GenerationPowerFlowTimeSeries

    waterfall: GenerationYear1Waterfall

    sam_raw: t.Optional[dict]

    solar_resource: t.Optional[SolarResource]

    warnings: t.Optional[t.List[str]]

    _defaults: t.ClassVar[t.List[str]] = ["power_flow", "waterfall", "warnings"]

    def default_dict(self):
        r""":meta private:"""
        inc = {k: True for k in self._defaults}
        inc["power_flow"] = self.power_flow.default_include()
        return self.dict(exclude_none=True, include=inc)


model_results_map = {"generation": GenerationModelResults}
