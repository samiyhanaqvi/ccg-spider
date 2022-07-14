from typing import TypedDict


class Town(TypedDict):
    crop_extentmajority: float
    cropyield: float
    MarketDist: float
    WTDmean: float
    GridDist: float


class Pars(TypedDict):
    Tech_type: float
    tcostperton_km: float
    pumpenergyint: float
    crop_price: float


class C:
    h3size: float = 0.7373276
    km2ha: float = 100
    CropWaterNeeds: float = 50  # m3 per t per year
    pump_eff: float = 0.8
    kWh_cost: float = 0.8


class Result(TypedDict):
    tech: str
    crop_production: float
    transp_cost: float
    irrig_cost: float
    revenue: float
    profit: float


def getProductionMultiplier(pars: Pars) -> float:
    if pars["Tech_type"] == "pump":
        return 2.5
    elif pars["Tech_type"] == "bore":
        return 1.9
    else:
        return 0.7


def model(town: Town, pars: Pars) -> Result:
    productionMulti = getProductionMultiplier(pars)
    crop_production = (
        ((town["crop_extentmajority"] * 0.5) / 100)
        * C.h3size
        * C.km2ha
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
            (
                crop_production
                * C.CropWaterNeeds
                * town["WTDmean"]
                * pars["pumpenergyint"]
            )
            / C.pump_eff
        )
        * C.kWh_cost
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
