def getProductionMultiplier(pars):
    if pars["Tech_type"] == "pump":
        return 2.5
    elif pars["Tech_type"] == "bore":
        return 1.9
    else:
        return 0.7


def model(town, pars):
    h3size = 0.7373276
    km2ha = 100
    CropWaterNeeds = 50  # m3 per t per year
    pump_eff = 0.8
    kWh_cost = 0.8

    productionMulti = getProductionMultiplier(pars)
    crop_production = (
        ((town["crop_extentmajority"] * 0.5) / 100)
        * h3size
        * km2ha
        * town["cropyield"]
        * productionMulti
    )

    transp_cost = (
        ((town["MarketDist"] * 833) / 1000)
        * town["crop_extentmajority"]
        * pars["tcostperton_km"]
    )

    irrig_cost = (
        (
            (crop_production * CropWaterNeeds * town["WTDmean"] * pars["pumpenergyint"])
            / pump_eff
        )
        * kWh_cost
        * town["GridDist"]
    )

    revenue = crop_production * pars["crop_price"]
    profit = revenue - transp_cost - irrig_cost

    tech = "agri" if crop_production > 0.5 else "none"

    return dict(
        crop_production=max(0, crop_production),
        transp_cost=max(0, transp_cost),
        irrig_cost=max(0, irrig_cost),
        revenue=max(0, revenue),
        profit=max(0, profit),
        tech=tech,
    )
