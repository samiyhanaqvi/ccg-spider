from attrs import define
import geopandas as gpd


@define
class Assumptions:
    duration: int = 20  # yrs
    interest_rate: float = 0.06  # as a fraction of 1
    fish_price: int = 6000  # USD/ton

    max_fish_output: int = 1000  # tons/yr
    labor_per_hh: float = 0.5

    max_lake_dist: int = 9  # max distance to lake victoria
    max_water_dist: int = 9  # max distance to another lake for pond water
    min_precip: int = 30  # min precip for pond if no water
    truck_econ_multi: float = 1  # additional road usage due to econ activity
    traffic_pp: float = 1 / 2000  # current vehicles/person/day

    mg_cost_pkw: int = 6000  # USD/kW

    elec_ice: float = 125  # kWh/ton of fish/yr
    ice_power: float = 0.1  # kW/ton capacity
    aeration_power: float = 1.25  # kW/ton capacity


@define
class Town:
    pop: int
    grid_dist: float
    road_dist: float
    urban_dist: float
    city_dist: float
    lake_dist: float
    water_dist: float
    precip: int
    road_type: str = "earth"
    hh_size: float = 5

    @property
    def hhs(self):
        return self.pop / self.hh_size

    @classmethod
    def from_row(cls, row: gpd.GeoSeries):
        return cls(
            pop=row["pop"],
            grid_dist=row["grid_dist"],
            road_dist=row["road_dist"],
            urban_dist=row["urban_dist"],
            city_dist=row["city_dist"],
            lake_dist=row["lake_dist"],
            water_dist=row["water_dist"],
            precip=row["precip"],
        )


def npv(yrs, r):
    """USD/yr"""
    tot = 0
    for i in range(yrs):
        tot += 1 / ((1 + r) ** i)
    return tot


def get_farm_type(town, ass):
    """type"""
    if town.lake_dist < ass.max_lake_dist:
        return "cage"
    elif town.water_dist < ass.max_water_dist:
        return "pond"
    elif town.precip > ass.min_precip:
        return "pond"
    else:
        return None


def get_road_type(town, ass, farm_type, fish_output):
    """type"""
    traffic = town.pop // ass.traffic_pp  # vehicles/day
    fish_vehicles = 7.7 if farm_type == "cage" else 10.2  # num/ton of fish/yr
    total_traffic = traffic + fish_vehicles * fish_output * ass.truck_econ_multi
    if total_traffic > 200 * 365:
        return "paved"
    elif total_traffic > 50 * 365:
        return "gravel"
    else:
        return "earth"


def get_road_cap_cost(town, needed):
    """USD/km"""
    cost = 0
    if town.road_type == "earth" and needed == "gravel":
        cost = 92_266
    elif town.road_type == "gravel" and needed == "paved":
        cost = 414_962
    elif town.road_type == "earth" and needed == "paved":
        cost = 507_228

    if town.road_dist < 10:
        cost *= 1.3
    return cost


def get_road_maintenance(needed):
    """USD/km/yr"""
    maintenance = 0
    if needed == "gravel":
        maintenance = 5_822
    elif needed == "paved":
        maintenance = 7_526
    return maintenance


def get_land_required(farm_type):
    """acres/ton"""
    if farm_type == "cage":
        return 0.01
    else:
        return 0.83


def get_land_rent(ass, farm_type):
    """USD/ton/yr"""
    land_required = get_land_required(farm_type)
    land_value = 4000  # USD/acre
    land_cost = land_required * land_value  # USD/ton
    land_rent = land_cost * ass.interest_rate  # USD/ton/yr
    return land_rent


def get_elec_capex(town, ass):
    """USD"""
    if town.grid_dist < 1:  # already grid-connected
        return 0

    elif town.grid_dist < 20:  # close enough to extend grid
        mv_cost_pkm = 15_000  # USD/km2
        conn_cost_phh = 4800  # USD/hh
        mv_cost = mv_cost_pkm * town.grid_dist  # USD
        conn_cost = conn_cost_phh * town.hhs  # USD
        return mv_cost + conn_cost

    else:
        kw_needed = town.hhs * 0.2  # kW
        conn_cost_phh = 500  # USD/hh
        mg_cost = ass.mg_cost_pkw * kw_needed  # USD
        conn_cost = conn_cost_phh * town.hhs  # USD
        return mg_cost + conn_cost


def get_elec_cost_for_farm(town, ass):
    """USD/ton/yr"""
    total_power_req = max(2, ass.ice_power + ass.aeration_power)  # kW/ton
    if town.grid_dist < 1:  # already grid-connected
        return 0
    elif town.grid_dist < 20:  # close enough to extend grid
        return 0
    else:
        mg_cap_cost = ass.mg_cost_pkw * total_power_req
        mg_repayment = mg_cap_cost / npv(ass.duration, ass.interest_rate)
        return mg_repayment


def get_farm_cap_cost_annual(ass, farm_type):
    """USD/ton/yr"""
    farm_cap_cost = 138.89 if farm_type == "cage" else 1950
    farm_annual = farm_cap_cost / npv(ass.duration, ass.interest_rate)  # USD/ton/yr
    return farm_annual


def get_fish_output(town, ass, farm_type):
    """ton/yr"""
    labor = town.hhs * ass.labor_per_hh  # number of laborers available
    labor_needed = 3 if farm_type == "cage" else 1  # worker/ton/yr
    max_fish_from_labor = labor // labor_needed  # ton/yr
    fish_output = min(max_fish_from_labor, ass.max_fish_output)  # ton/yr
    return fish_output


def get_transport_costs(town):
    """USD/ton/yr"""
    urban_to_city = town.city_dist - town.urban_dist
    short_dist_flat = 7.88  # USD/ton
    short_dist_spec = 1.214  # USD/ton/km
    long_dist_flat = 13.54  # USD/ton
    long_dist_spec = 0.086  # USD/ton/km
    transport_to_urban = short_dist_flat + short_dist_spec * town.urban_dist  # USD/ton
    transport_to_city = long_dist_flat + long_dist_spec * urban_to_city  # USD/ton
    short_dist_transport_multiplier = 1.5  # to account for ice and fish
    long_dist_transport_multiplier = 2  # ditto
    transport_cost_urban = (
        transport_to_urban * short_dist_transport_multiplier
    )  # USD/ton/yr
    transport_cost_city = (
        transport_to_city * long_dist_transport_multiplier
    )  # USD/ton/yr
    return transport_cost_urban + transport_cost_city  # USD/ton/yr


def get_revenue(ass, farm_type):
    """USD/ton/yr"""
    fish_price = ass.fish_price
    if farm_type == "pond":
        fish_price *= 0.75
    return fish_price


def get_equipment_costs(ass):
    """USD/ton/yr"""
    capex_ice = 1000  # USD/ton capacity
    capex_aeration = 200  # USD/ton capacity
    capex_equipment = capex_ice + capex_aeration  # USD/ton capacity
    equipment_annual = capex_equipment / npv(
        ass.duration, ass.interest_rate
    )  # USD/ton/yr
    return equipment_annual


def get_running_costs(ass, farm_type):
    """USD/ton"""
    aeration_use = 10  # hours
    elec_aeration = aeration_use * ass.aeration_power * 365  # kWh/ton/yr of fish

    elec_cost_to_farm = 0.25  # USD/kWh
    cost_feed = 1375  # USD/ton
    cost_labor = 150.7  # USD/ton
    cost_fingerlings = 500  # USD/ton
    cost_misc = 48.02 if farm_type == "cage" else 226.67  # USD/ton
    cost_ice = elec_cost_to_farm * ass.elec_ice  # USD/ton
    cost_aeration = elec_cost_to_farm * elec_aeration  # USD/ton
    total_running_costs = (
        cost_feed + cost_labor + cost_fingerlings + cost_misc + cost_ice + cost_aeration
    )  # USD/ton
    return total_running_costs


def get_gov_costs(town, ass, road_type_needed):
    """USD, USD/yr"""
    elec_capex = get_elec_capex(town, ass)
    road_cap_cost = get_road_cap_cost(town, road_type_needed)  # USD/km
    road_capex = road_cap_cost * town.road_dist  # USD
    road_maintenance_cost = get_road_maintenance(road_type_needed)  # USD/km/yr
    road_maintenance = road_maintenance_cost * town.road_dist  # USD/yr
    gov_costs = elec_capex + road_capex  # USD
    gov_annual = road_maintenance  # USD/yr
    return gov_costs, gov_annual


def get_social_benefit(town):
    """USD/yr"""
    energy_cooking = 1875  # kWh/yr
    energy_lights = 21.9  # kWh/yr
    energy_phh = energy_cooking + energy_lights  # kWh/yr
    energy_total = energy_phh * town.hhs  # kWh
    cooking_co2_saved = 1.47  # kgCO2/kWh
    social_carbon_cost = 0.15  # USD/kgCO2/yr
    health_benefits = 0.1  # USD/kgCO2/yr
    social_benefit = social_carbon_cost + health_benefits  # USD/kgCO2/yr
    total_social_benefit = social_benefit * cooking_co2_saved * energy_total  # USD/yr
    return total_social_benefit


def display(
    gov_costs,
    gov_annual,
    total_revenue,
    final_profit,
    town,
    hhs,
    total_social_benefit,
    farm_type,
):
    print(f"Farm type: {farm_type}")
    print()

    print(f"Gov capex:  {gov_costs:,.0f} USD")
    print(f"Gov annual: {gov_annual:,.0f} USD/yr")
    print()

    print(f"Revenue: {total_revenue:,.0f} USD/yr")
    print(f"Profit:  {final_profit:,.0f} USD/yr")
    print()

    print(f"Current grid dist:  {town.grid_dist:.0f} km")
    print(f"Houses electrified: {hhs:.0f}")
    print()

    print(f"Social benefit: {total_social_benefit:,.0f} USD/yr")


def run_model(town, ass, verbose=False):
    # Some decisions
    farm_type = get_farm_type(town, ass)

    if farm_type:
        fish_output = get_fish_output(town, ass, farm_type)  # ton/yr

        # Costs
        land_rent = get_land_rent(ass, farm_type)  # USD/ton/yr
        elec_cost_for_farm = get_elec_cost_for_farm(town, ass)  # USD/ton/yr
        farm_annual = get_farm_cap_cost_annual(ass, farm_type)  # USD/ton/yr
        equipment_annual = get_equipment_costs(ass)  # USD/ton/yr
        running_costs = get_running_costs(ass, farm_type)  # USD/ton/yr
        transport_costs = get_transport_costs(town)  # USD/ton/yr

        # Profit per ton
        costs_per_ton = (
            land_rent
            + elec_cost_for_farm
            + running_costs
            + farm_annual
            + equipment_annual
            + transport_costs
        )  # USD/ton/yr
        revenue_per_ton = get_revenue(ass, farm_type)  # USD/ton/yr
        profit_per_ton = revenue_per_ton - costs_per_ton  # USD/ton/yr

        # Absolute profit
        revenue = revenue_per_ton * fish_output
        profit = profit_per_ton * fish_output

        # Gov costs
        road_type_needed = get_road_type(town, ass, farm_type, fish_output)
        gov_costs, gov_annual = get_gov_costs(town, ass, road_type_needed)

        # Household elec
        total_social_benefit = get_social_benefit(town)

    if verbose:
        if farm_type:
            display(
                gov_costs,
                gov_annual,
                revenue,
                profit,
                town,
                town.hhs,
                total_social_benefit,
                farm_type,
            )
        else:
            print("No farm possible here")

    else:
        if farm_type:
            return max(0, profit)
        else:
            return 0
