const constrain_output = (town, ass) => {
  // ton/yr, farm type

  let farm_type = "none";
  if (town.lake_dist < ass.max_lake_dist) {
    farm_type = "cage";
  } else if (
    town.water_dist < ass.max_water_dist ||
    town.river_dist < ass.max_water_dist ||
    town.precip > ass.min_precip // ||
    // town.adm1.lower() in ass.always_towns
  ) {
    farm_type = "pond";
  }
  let fish_output = 0;
  if (
    town.precip > ass.min_precip &&
    town.pop > ass.min_pop &&
    town.pop < ass.max_pop
  ) {
    let max_from_farm = 0;
    if (farm_type == "cage") {
      max_from_farm = ass.max_fish_output;
    } else if (farm_type == "pond") {
      max_from_farm = town.precip * 20;
    }

    let labor = town.hhs * ass.labor_per_hh; // number of laborers available
    let labor_needed = farm_type == "cage" ? 3 : 1; // worker/ton/yr
    let max_fish_from_labor = labor / labor_needed; // ton/yr

    fish_output = Math.min(
      ass.max_fish_output,
      max_fish_from_labor,
      max_from_farm
    ); // ton/yr
  }

  if (fish_output === 0) {
    farm_type = "none";
  }
  if (farm_type === "none") {
    fish_output = 0;
  }

  return [fish_output, farm_type];
};

const npv = (yrs, r) => {
  // USD/yr
  let tot = 0;
  for (let i = 0; i < yrs; i++) {
    tot += 1 / (1 + r) ** i;
  }
  return tot;
};

const get_road_type = (town, ass, farm_type, fish_output) => {
  // type
  let traffic = town.pop / ass.traffic_pp; // vehicles/day
  let fish_vehicles = farm_type == "cage" ? 7.7 : 10.2; // num/ton of fish/yr
  let total_traffic =
    traffic + fish_vehicles * fish_output * ass.truck_econ_multi;
  if (total_traffic > 200 * 365) {
    return "paved";
  } else if (total_traffic > 50 * 365) {
    return "gravel";
  } else {
    return "earth";
  }
};

const get_road_cap_cost = (town, needed) => {
  // USD/km
  let cost = 0;
  if (town.road_type == "earth" && needed == "gravel") {
    cost = 92_266;
  } else if (town.road_type == "gravel" && needed == "paved") {
    cost = 414_962;
  } else if (town.road_type == "earth" && needed == "paved") {
    cost = 507_228;
  }

  if (town.road_dist < 10) cost *= 1.3;
  return cost;
};

const get_road_maintenance = (needed) => {
  // USD/km/yr
  let maintenance = 0;
  if (needed == "gravel") {
    maintenance = 5_822;
  } else if (needed == "paved") {
    maintenance = 7_526;
  }
  return maintenance;
};

const get_land_required = (farm_type) => {
  // acres/ton
  if (farm_type == "cage") {
    return 0.01;
  } else {
    return 0.83;
  }
};

const get_land_rent = (ass, farm_type) => {
  // USD/ton/yr
  let land_required = get_land_required(farm_type);
  let land_value = 4000; // USD/acre
  let land_cost = land_required * land_value; // USD/ton
  let land_rent = land_cost * ass.interest_rate; // USD/ton/yr
  return land_rent;
};

const get_elec_capex = (town, ass) => {
  // USD
  if (town.grid_dist < 1) {
    // already grid-connected
    return 0;
  } else if (town.grid_dist < 20) {
    // close enough to extend grid
    let mv_cost_pkm = 15_000; // USD/km2
    let conn_cost_phh = 4800; // USD/hh
    let mv_cost = mv_cost_pkm * town.grid_dist; // USD
    let conn_cost = conn_cost_phh * town.hhs; // USD
    return mv_cost + conn_cost;
  } else {
    let kw_needed = town.hhs * 0.2; // kW
    let conn_cost_phh = 500; // USD/hh
    let mg_cost = ass.mg_cost_pkw * kw_needed; // USD
    let conn_cost = conn_cost_phh * town.hhs; // USD
    return mg_cost + conn_cost;
  }
};

const get_elec_cost_for_farm = (town, ass) => {
  // USD/ton/yr
  let total_power_req = Math.max(2, ass.ice_power + ass.aeration_power); // kW/ton
  if (town.grid_dist < 1) {
    // already grid-connected
    return 0;
  } else if (town.grid_dist < 20) {
    // close enough to extend grid
    return 0;
  } else {
    let mg_cap_cost = ass.mg_cost_pkw * total_power_req;
    let mg_repayment = mg_cap_cost / npv(ass.duration, ass.interest_rate);
    return mg_repayment;
  }
};

const get_farm_cap_cost_annual = (ass, farm_type) => {
  // USD/ton/yr
  let farm_cap_cost = farm_type == "cage" ? 138.89 : 1950;
  let farm_annual = farm_cap_cost / npv(ass.duration, ass.interest_rate); // USD/ton/yr
  return farm_annual;
};

const get_transport_costs = (town) => {
  // USD/ton/yr
  let urban_to_city = town.city_dist - town.urban_dist;
  let short_dist_flat = 7.88; // USD/ton
  let short_dist_spec = 1.214; // USD/ton/km
  let long_dist_flat = 13.54; // USD/ton
  let long_dist_spec = 0.086; // USD/ton/km
  let transport_to_urban = short_dist_flat + short_dist_spec * town.urban_dist; // USD/ton
  let transport_to_city = long_dist_flat + long_dist_spec * urban_to_city; // USD/ton
  let short_dist_transport_multiplier = 1.5; // to account for ice and fish
  let long_dist_transport_multiplier = 2; // ditto
  let transport_cost_urban =
    transport_to_urban * short_dist_transport_multiplier; // USD/ton/yr
  let transport_cost_city = transport_to_city * long_dist_transport_multiplier; // USD/ton/yr
  return transport_cost_urban + transport_cost_city; // USD/ton/yr
};

const get_revenue = (ass, farm_type) => {
  // USD/ton/yr
  let fish_price = ass.fish_price;
  if (farm_type == "pond") {
    fish_price *= 0.75;
  }
  return fish_price;
};

const get_equipment_costs = (ass) => {
  // USD/ton/yr
  let capex_ice = 1000; // USD/ton capacity
  let capex_aeration = 200; // USD/ton capacity
  let capex_equipment = capex_ice + capex_aeration; // USD/ton capacity
  let equipment_annual = capex_equipment / npv(ass.duration, ass.interest_rate); // USD/ton/yr
  return equipment_annual;
};

const get_running_costs = (ass, farm_type) => {
  // USD/ton
  const aeration_use = 10; // hours
  const elec_aeration = aeration_use * ass.aeration_power * 365; // kWh/ton/yr of fish

  const elec_cost_to_farm = 0.25; // USD/kWh
  const cost_feed = 1375; // USD/ton
  const cost_labor = 150.7; // USD/ton
  const cost_fingerlings = 500; // USD/ton
  const cost_misc = farm_type == "cage" ? 48.02 : 226.67; // USD/ton
  const cost_ice = elec_cost_to_farm * ass.elec_ice; // USD/ton
  const cost_aeration = elec_cost_to_farm * elec_aeration; // USD/ton
  const total_running_costs =
    cost_feed +
    cost_labor +
    cost_fingerlings +
    cost_misc +
    cost_ice +
    cost_aeration; // USD/ton
  return total_running_costs;
};

const get_gov_costs = (town, ass, road_type_needed) => {
  // USD, USD/yr
  const elec_capex = get_elec_capex(town, ass);
  const road_cap_cost = get_road_cap_cost(town, road_type_needed); // USD/km
  const road_capex = road_cap_cost * town.road_dist; // USD
  const road_maintenance_cost = get_road_maintenance(road_type_needed); // USD/km/yr
  const road_maintenance = road_maintenance_cost * town.road_dist; // USD/yr
  const gov_costs = elec_capex + road_capex; // USD
  const gov_annual = road_maintenance; // USD/yr
  return [gov_costs, gov_annual];
};

const get_social_benefit = (town) => {
  // USD/yr
  const energy_cooking = 1875; // kWh/yr
  const energy_lights = 21.9; // kWh/yr
  const energy_phh = energy_cooking + energy_lights; // kWh/yr
  const energy_total = energy_phh * town.hhs; // kWh
  const cooking_co2_saved = 1.47; // kgCO2/kWh
  const social_carbon_cost = 0.15; // USD/kgCO2/yr
  const health_benefits = 0.1; // USD/kgCO2/yr
  const social_benefit = social_carbon_cost + health_benefits; // USD/kgCO2/yr
  const total_social_benefit =
    social_benefit * cooking_co2_saved * energy_total; // USD/yr
  return total_social_benefit;
};

export const run_model = (town, ass) => {
  town.hhs = town.pop / 5;
  // Some decisions
  const [fish_output, farm_type] = constrain_output(town, ass); // ton/yr

  if (farm_type != "none") {
    // Costs
    const land_rent = get_land_rent(ass, farm_type); // USD/ton/yr
    const elec_cost_for_farm = get_elec_cost_for_farm(town, ass); // USD/ton/yr
    const farm_annual = get_farm_cap_cost_annual(ass, farm_type); // USD/ton/yr
    const equipment_annual = get_equipment_costs(ass); // USD/ton/yr
    const running_costs = get_running_costs(ass, farm_type); // USD/ton/yr
    const transport_costs = get_transport_costs(town); // USD/ton/yr

    // Profit per ton
    const costs_per_ton =
      land_rent +
      elec_cost_for_farm +
      running_costs +
      farm_annual +
      equipment_annual +
      transport_costs; // USD/ton/yr
    const revenue_per_ton = get_revenue(ass, farm_type); // USD/ton/yr
    const profit_per_ton = revenue_per_ton - costs_per_ton; // USD/ton/yr

    // Absolute profit
    const revenue = revenue_per_ton * fish_output;
    const profit = profit_per_ton * fish_output;

    // Gov costs
    const road_type_needed = get_road_type(town, ass, farm_type, fish_output);
    const [gov_costs, gov_annual] = get_gov_costs(town, ass, road_type_needed);

    // Household elec
    const total_social_benefit = get_social_benefit(town);
    return {
      farm_type: farm_type,
      fish_output: Math.max(0, fish_output),
      profit: Math.max(0, profit),
      gov_costs: Math.max(0, gov_costs),
      social: Math.max(0, total_social_benefit),
    };
  } else {
    return {
      farm_type: "none",
      fish_output: 0,
      profit: 0,
      gov_costs: 0,
      social: 0,
    };
  }
};
