const getTech = (profit) => {
  if (profit > 30) {
    return "solar";
  } else if (profit > 10) {
    return "wind";
  } else {
    return "none";
  }
};

export default (town, pars) => {
  const revenue = town.city_dist * 2;
  const profit = revenue / 10;
  const gov_costs = 100 * pars.duration;
  const gov_annual = 20;
  const social = 15;

  const tech = getTech(profit);

  return {
    tech: tech,
    revenue: Math.max(0, revenue),
    profit: Math.max(0, profit),
    gov_costs: Math.max(0, gov_costs),
    gov_annual: Math.max(0, gov_annual),
    social: Math.max(0, social),
  };
};
