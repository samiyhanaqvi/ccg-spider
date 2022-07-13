from typing import TypedDict, NamedTuple


class Town(NamedTuple):
    pv: float
    wind: float
    ocean_dist: float
    water_dist: float
    mombasa_dist: float
    rest_area: float
    avail_area: float


class Pars(NamedTuple):
    pv_capex: float
    min_area: float
    water_tran_cost: float
    elec_ocean_water_treatment: float
    interest_rate: float
    h2_state: str
    elec_water_treatment: float
    wind_capex: float
    water_resource: str
    h2_trans_cost: float
    wind_dist: float
    pv_size: float


class Const(NamedTuple):
    pv_lifetime: float = 20
    pv_opex: float = 9.3  # €/kWp*a

    wind_lifetime: float = 20
    wind_opex: float = 40  # €/kWp*a
    cp: float = 0.45  # Coefficient of performance wind turbine
    den_air: float = 1.14  # Air density in kg/m3
    d_rot: float = 100  # Diameter of rotor in kg/m3

    ely_capex: float = 1280  # €/kW
    ely_opex: float = 0.02  # % CAPEX/a
    ely_lt: float = 10  # a
    ely_eff: float = 0.6
    ely_cap: float = 0.6
    ely_water: float = 10  # liter/kg

    water_spec_cost: float = 1.2  # €/m3
    h2_en_den: float = 33.33  # kWh/kgh2
    energy_liquid: float = 9  # kWh/kgh2
    ely_output_pressure: float = 30  # bar


C = Const()


class Result(TypedDict):
    tech: str
    elec_technology: str
    cost_elec_pv: float
    cost_elec_wind: float
    cost_elec: float
    cost_h2: float
    cost_h2_ocean: float
    turbine_output: float
    pv_radiation: float
    wind_speed: float
    h2_cost_to_demand: float
    pv_kWh: float
    wind_kWh: float


def pvf(interestrate: float, lifetime: float) -> float:
    """
    Function present value facto
    """
    return float(
        (((1 + interestrate) ** lifetime) - 1)
        / (((1 + interestrate) ** lifetime) * interestrate)
    )


def elec_tech(option1: float, option2: float) -> str:
    if option1 > option2:
        return "wind"
    else:
        return "pv"


def handling_costs(pars: Pars, cost_elec: float) -> float:
    """
    Function handling costs (compression or liquification)
    """
    if "Liquid" in pars.h2_state:
        return C.energy_liquid * (cost_elec / 1000)
    else:
        return float(
            (0.003944 * 298.15 * (((500 / C.ely_output_pressure) ** (0.4 / 1.4)) - 1))
            / 0.8
        ) * (cost_elec / 1000)


def water_costs(town: Town, pars: Pars, cost_elec: float) -> float:
    """
    Water costs
    """
    if "Domestic" in pars.water_resource:
        return (
            (
                C.water_spec_cost
                + (pars.water_tran_cost / 100) * town.water_dist
                + pars.elec_water_treatment * cost_elec
            )
            * C.ely_water
            / 1000
        )
    elif "Ocean" in pars.water_resource:
        return (
            (
                C.water_spec_cost
                + (pars.water_tran_cost / 100) * town.ocean_dist
                + pars.elec_ocean_water_treatment * cost_elec
            )
            * C.ely_water
            / 1000
        )
    elif "Cheapest option" in pars.water_resource:
        water_costs_h2_water_bodies = (
            (
                C.water_spec_cost
                + (pars.water_tran_cost / 100) * town.water_dist
                + pars.elec_water_treatment * cost_elec
            )
            * C.ely_water
            / 1000
        )
        water_costs_h2_ocean = (
            (
                C.water_spec_cost
                + (pars.water_tran_cost / 100) * town.ocean_dist
                + pars.elec_ocean_water_treatment * cost_elec
            )
            * C.ely_water
            / 1000
        )
        if water_costs_h2_ocean > water_costs_h2_water_bodies:
            return water_costs_h2_water_bodies
    return water_costs_h2_ocean


def pv_kwp(pars: Pars, available_area: float) -> float:
    """
    Adding PV GWh possible
    """
    if available_area > pars.min_area:
        return ((available_area) * 1000000) / pars.pv_size
    else:
        return 0


def wind_pc(pars: Pars, available_area: float) -> float:
    """
    Adding Wind GWh possible
    """
    if available_area > pars.min_area:
        return ((available_area) * 1000000) / (
            (3.14 * ((pars.wind_dist * C.d_rot) ** 2)) / 4
        )
    else:
        return 0


def model(town: Town, pars: Pars) -> Result:

    # Electricity cost calculation
    cost_elec_pv = (
        (pars.pv_capex / pvf((pars.interest_rate / 100), C.pv_lifetime) + C.pv_opex)
        / town.pv
        / 365
    ) * 1000
    pv_radiation = town.pv * 365
    wind_speed = town.wind
    turbine_output = (
        0.5
        * C.cp
        * C.den_air
        * ((C.d_rot**2) * 3.14 / 4)
        * (town.wind**3)
        * 8760
        / 1000
        / 3000
    )  # yearly power output per turbine
    cost_elec_wind = (
        (
            (
                pars.wind_capex / pvf(pars.interest_rate / 100, C.wind_lifetime)
                + C.wind_opex
            )
        )
        / turbine_output
    ) * 1000
    cost_elec = min(cost_elec_pv, cost_elec_wind)
    cost_ely = (
        ((C.ely_capex / pvf(pars.interest_rate / 100, C.ely_lt)) / (C.ely_cap * 8760))
        * (C.h2_en_den / C.ely_eff)
    ) * (1 + C.ely_opex)
    elec_technology = elec_tech(cost_elec_pv, cost_elec_wind)

    # LCOH cost calculation
    cost_elec_h2 = (cost_elec / 1000) * (C.h2_en_den / C.ely_eff)
    cost_h2_ocean = (
        cost_elec_h2
        + cost_ely
        + handling_costs(pars, cost_elec)
        + (
            (
                C.water_spec_cost
                + (pars.water_tran_cost / 100) * town.ocean_dist
                + pars.elec_ocean_water_treatment * cost_elec
            )
            * C.ely_water
            / 1000
        )
    )
    cost_h2 = (
        cost_elec_h2
        + cost_ely
        + handling_costs(pars, cost_elec)
        + water_costs(town, pars, cost_elec)
    )

    # Distance to port in mombasa --> demand center due to export
    port_dist = town.mombasa_dist

    # H2 costs including transport
    h2_cost_to_demand = cost_h2 + (pars.h2_trans_cost * port_dist / 100)

    # Including restricted surface area: Currently forest, agri and water
    tech = "something" if (town.avail_area - town.rest_area) > pars.min_area else "none"
    available_area = town.avail_area - town.rest_area

    pv_kWp = pv_kwp(pars, available_area)
    pv_kWh = pv_kWp * town.pv / 1000000  # in GWh

    wind_pcs = wind_pc(pars, available_area)
    wind_kWh = turbine_output * wind_pcs / 1000000  # in GWh

    return Result(
        elec_technology=elec_technology,
        tech=tech,
        cost_elec_pv=cost_elec_pv,
        cost_elec_wind=cost_elec_wind,
        cost_elec=cost_elec,
        cost_h2=cost_h2,
        cost_h2_ocean=cost_h2_ocean,
        turbine_output=turbine_output,
        pv_radiation=pv_radiation,
        wind_speed=wind_speed,
        h2_cost_to_demand=h2_cost_to_demand,
        pv_kWh=pv_kWh,
        wind_kWh=wind_kWh,
    )


def entry(town: dict, pars: dict) -> Result:
    t = Town(**{k: v for k, v in town.items() if k in Town._fields})
    p = Pars(**{k: v for k, v in pars.items() if k in Pars._fields})
    return model(t, p)
