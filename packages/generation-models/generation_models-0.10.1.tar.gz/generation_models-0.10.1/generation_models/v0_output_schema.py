from __future__ import annotations
import typing as t
import pandas as pd
from pydantic import BaseModel
from .utils import reform_for_multiindex_df


class SolarTimeSeries(BaseModel):
    r"""-"""

    ideal_tracker_rotation: t.Optional[list]

    front_total_poa: t.Optional[list]

    rear_total_poa: t.Optional[list]

    effective_total_poa: t.Optional[list]

    array_dc_snow_loss: t.Optional[list]

    array_gross_dc_power: t.Optional[list]

    array_dc_power: t.Optional[list]

    array_dc_voltage: t.Optional[list]

    inverter_mppt_dc_voltage: t.Optional[list]

    inverter_mppt_loss: t.Optional[list]

    inverter_clipping_loss: t.Optional[list]

    inverter_night_tare_loss: t.Optional[list]

    inverter_power_consumption_loss: t.Optional[list]

    inverter_efficiency: t.Optional[list]

    ambient_temp: t.Optional[list]

    gross_ac_power: list

    mv_transformer_loss: t.Optional[list]

    mv_transformer_load_loss: t.Optional[list]

    mv_transformer_no_load_loss: t.Optional[list]

    mv_ac_power: list

    ac_wiring_loss: list

    hv_transformer_loss: t.Optional[list]

    hv_transformer_load_loss: t.Optional[list]

    hv_transformer_no_load_loss: t.Optional[list]

    transformer_load_loss: list

    transformer_no_load_loss: list

    hv_ac_power: list

    ac_transmission_loss: list

    gen: list

    poi_unadjusted: list

    system_power: list

    positive_system_power: list

    negative_system_power: list

    sam_design_parameters: dict


class SolarWaterfall(BaseModel):
    r"""-"""

    gh_ann: t.Optional[float]

    nominal_poa_ann: t.Optional[float]

    shading_lp: t.Optional[float]

    soiling_lp: t.Optional[float]

    reflection_lp: t.Optional[float]

    bifacial_lp: t.Optional[float]

    dc_nominal_ann: t.Optional[float]

    snow_lp: t.Optional[float]

    module_temp_lp: t.Optional[float]

    mppt_lp: t.Optional[float]

    mismatch_lp: t.Optional[float]

    diodes_lp: t.Optional[float]

    dc_wiring_lp: t.Optional[float]

    tracking_error_lp: t.Optional[float]

    mppt_error_lp: t.Optional[float]

    nameplate_lp: t.Optional[float]

    dc_optimizer_lp: t.Optional[float]

    dc_avail_lp: t.Optional[float]

    dc_net_ann: t.Optional[float]

    inverter_clipping_lp: t.Optional[float]

    inverter_consumption_lp: t.Optional[float]

    inverter_nightcons_lp: t.Optional[float]

    inverter_efficiency_lp: t.Optional[float]

    ac_gross_ann: t.Optional[float]

    mv_transformer_lp: t.Optional[float]

    ac_wiring_lp: t.Optional[float]

    hv_transformer_lp: t.Optional[float]

    transformer_lp: float

    transmission_lp: float

    poi_clipping_lp: float

    ac_availcurtail_lp: float

    annual_energy: float


class SolarStorageTimeSeries(BaseModel):
    r"""-"""

    battery_internal_energy: list

    battery_internal_energy_max: list

    battery_limit: t.Union[float, list]

    battery_output: list

    excess_power_at_coupling: list

    captured_excess_at_coupling: list

    solar_storage_dc_voltage: t.Optional[list]

    solar_storage_dc_power: t.Optional[list]

    solar_storage_power_at_coupling: t.Optional[list]

    inverter_clipping_loss: t.Optional[list]

    inverter_tare_loss: t.Optional[list]

    inverter_parasitic_loss: t.Optional[list]

    inverter_consumption_loss: t.Optional[list]

    inverter_efficiency: t.Optional[list]

    solar_storage_gross_ac_power: t.Optional[list]

    mv_xfmr_loss: t.Optional[list]

    mv_xfmr_load_loss: t.Optional[list]

    mv_xfmr_no_load_loss: t.Optional[list]

    solar_storage_ac_power: list

    solar_storage_mv_ac_power: t.Optional[list]

    hvac_loss: t.Optional[list]

    ac_wiring_loss: t.Optional[list]

    hv_xfmr_loss: t.Optional[list]

    hv_xfmr_load_loss: t.Optional[list]

    hv_xfmr_no_load_loss: t.Optional[list]

    transformer_loss: t.Optional[list]

    solar_storage_hv_ac_power: list

    transmission_loss: list

    solar_storage_gen: list

    solar_storage_poi_unadjusted: list

    solar_storage_poi: list

    positive_solar_storage_poi: list

    negative_solar_storage_poi: list


class SolarStorageWaterfall(SolarWaterfall):
    r"""-"""

    battery_operation_lp: float

    excess_power_at_coupling_lp: float

    captured_excess_at_coupling_lp: float

    bess_hvac_lp: t.Optional[float]


class OptimizerTimeSeries(BaseModel):
    r"""-"""

    # note here we allow extras because of reserve markets and adversarial utilization
    class Config:
        extra = "allow"

    # note this might not be present because there were no hvac inputs, but also because for standalone+downstream and
    #  hybrid this signal is moved into system/solar_storage
    hvac_loss: t.Optional[list]

    import_limit_at_coupling: t.Optional[list]

    export_limit_at_coupling: t.Optional[list]

    target_load: t.Optional[list]

    charge_actual: list

    discharge_actual: list

    charge: list

    discharge: list

    charge_hi: list

    discharge_hi: list

    charge_lo: list

    discharge_lo: list

    battery_output: list

    output: list

    total_output: list

    internal_energy: list

    soe_actual: list

    soe_lo: list

    soe_hi: list

    soe_hb_actual: list

    soe_hb_lo: list

    soe_hb_hi: list

    soe_mean_actual: list

    soe_mean_lo: list

    soe_mean_hi: list

    dam_charge: t.Optional[list]

    dam_discharge: t.Optional[list]

    dam_base_point: t.Optional[list]

    negative_dam_base_point: t.Optional[list]

    dam_solar: t.Optional[list]

    rtm_charge: t.Optional[list]

    rtm_discharge: t.Optional[list]

    rtm_base_point: t.Optional[list]

    negative_rtm_base_point: t.Optional[list]

    rtm_solar: t.Optional[list]

    rtm_price: t.Optional[list]

    dam_price: t.Optional[list]

    imbalance: t.Optional[list]

    theoretical_dam_soe: t.Optional[list]

    solar_actual: t.Optional[list]

    solar_hi: t.Optional[list]

    solar_lo: t.Optional[list]

    net_load: t.Optional[list]


class MarketAwardsTimeSeries(BaseModel):
    r"""-"""

    # note here we allow extras because of reserve markets
    class Config:
        extra = "allow"

    charge: list

    discharge: list

    total_output: list

    rt_tare: list

    dam_charge: list

    dam_discharge: list

    dam_base_point: list

    negative_dam_base_point: list

    rtm_charge: list

    rtm_discharge: list

    rtm_base_point: list

    solar_actual: t.Optional[list]

    dam_solar: t.Optional[list]

    rtm_solar: t.Optional[list]


class StandaloneStorageSystemTimeSeries(BaseModel):
    r"""-"""

    dc_power: t.Optional[list]

    dc_voltage: t.Optional[list]

    inverter_clipping_loss: t.Optional[list]

    inverter_tare_loss: t.Optional[list]

    inverter_parasitic_loss: t.Optional[list]

    inverter_consumption_loss: t.Optional[list]

    inverter_efficiency: t.Optional[list]

    gross_ac_power: t.Optional[list]

    hvac_loss: t.Optional[list]

    ac_power: list

    mv_xfmr_loss: t.Optional[list]

    mv_xfmr_load_loss: t.Optional[list]

    mv_xfmr_no_load_loss: t.Optional[list]

    ac_wiring_loss: t.Optional[list]

    hv_xfmr_loss: t.Optional[list]

    hv_xfmr_load_loss: t.Optional[list]

    hv_xfmr_no_load_loss: t.Optional[list]

    transformer_loss: t.Optional[list]

    hv_ac_power: list

    transmission_loss: list

    gen: list

    poi_unadjusted: list

    poi: list

    positive_poi: list

    negative_poi: list


class GenerationModelResults(SolarTimeSeries):
    r"""Results schema returned when a
    :class:`~generation_models.generation_models.generation_models.PVGenerationModel`,
    :class:`~generation_models.generation_models.generation_models.ACExternalGenerationModel` or
    :class:`~generation_models.generation_models.generation_models.DCExternalGenerationModel` simulation is run"""

    tyba_api_loss_waterfall: SolarWaterfall

    warnings: t.List[str]

    coupling: None

    def time_series_df(self):
        return pd.DataFrame(
            self.dict(
                exclude={
                    "tyba_api_loss_waterfall",
                    "warnings",
                    "coupling",
                    "sam_design_parameters",
                },
                exclude_none=True,
            )
        )


class PVStorageModelResults(BaseModel):
    r"""Results schema returned when a :class:`~generation_models.generation_models.generation_models.PVStorageModel`
    simulation is run
    """

    solar_only: SolarTimeSeries

    solar_storage: SolarStorageTimeSeries

    waterfall: SolarStorageWaterfall

    optimizer: OptimizerTimeSeries

    market_awards: t.Optional[MarketAwardsTimeSeries]

    warnings: t.List[str]

    coupling: str

    def time_series_df(self):
        model_dict = self.dict(
            exclude={
                "solar_only": {"sam_design_parameters"},
                "waterfall": True,
                "warnings": True,
                "coupling": True,
            },
            exclude_none=True,
        )
        if isinstance(model_dict["solar_storage"]["battery_limit"], float):
            model_dict["solar_storage"]["battery_limit"] = [model_dict["solar_storage"]["battery_limit"]] * len(
                model_dict["solar_storage"]["battery_internal_energy_max"]
            )
        return pd.DataFrame(reform_for_multiindex_df(model_dict))


class StandaloneStorageModelWithDownstreamResults(BaseModel):
    r"""Results schema returned when a
    :class:`~generation_models.generation_models.generation_models.StandaloneStorageModel` simulation is run with a
    :attr:`~generation_models.generation_models.generation_models.StandaloneStorageModel.downstream_system` specified"""

    system: StandaloneStorageSystemTimeSeries

    optimizer_outputs: OptimizerTimeSeries

    market_awards: t.Optional[MarketAwardsTimeSeries]

    def time_series_df(self):
        model_dict = self.dict(exclude_none=True)
        return pd.DataFrame(reform_for_multiindex_df(model_dict))


class StandaloneStorageModelSimpleResults(OptimizerTimeSeries):
    r"""Results schema returned when a
    :class:`~generation_models.generation_models.generation_models.StandaloneStorageModel` simulation is run without a
    :attr:`~generation_models.generation_models.generation_models.StandaloneStorageModel.downstream_system` specified"""

    # note we allow extras because we inherit from OptimizerTimeSeries
    class Config:
        extra = "allow"

    def time_series_df(self):
        return pd.DataFrame(self.dict(exclude_none=True))
