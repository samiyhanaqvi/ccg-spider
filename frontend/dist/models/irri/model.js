export default (town, pars) => {
  const revenue = pars.crop_price * town.cropyield;
  const cost = pars.duration * town.GridDist;
  const profit = revenue - cost;

  const gov_costs = profit * 10;
  const gov_annual = gov_costs / 12;
  const total_social_benefit = cost * 0.5;

  const tech = profit > 0 ? "pump" : "none";

  return {
    tech: tech,
    revenue: Math.max(0, revenue),
    profit: Math.max(0, profit),
    gov_costs: Math.max(0, gov_costs),
    gov_annual: Math.max(0, gov_annual),
    social: Math.max(0, total_social_benefit),
  };
};
