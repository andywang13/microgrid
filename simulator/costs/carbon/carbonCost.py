# -*- coding: utf-8 -*-
"""
Created on Mon Apr  7 12:30:42 2020

@author: yun bin choh
"""
from dispatching.dispatchingLoop import dispatchingLoop
from costs.dollars.battery.batteryCost import batteryCost
from costs.dollars.dg.dgCost import dgCost
from costs.dollars.pv.pvCost import pvCost
import numpy as np

def carbonCost(gridComponents, timeStep, loadVector, projectDuration, discountRate, strategy):
    """
    INPUTS :
        - gridComponents : 
                            {
                                "battery" : {
                                                "maxStorage": float, the battery capacity storage (kWh),
                                                "initialStorage": float, the battery initial energy storage (kWh),
                                                "maxInputPow": float, the maximum charging power of the battery (kW),
                                                "maxOutputPow": float, the maximum discharging power of the battery (kW),
                                                "SOC_min": float, the minimum amount of energy that can be stored in the battery (kWh),
                                                "maxThroughput": float, the maximum amount of energy that can flow in and out of the battery during its lifetime (kWh),
                                                "lifetime": int, the nominal lifetime of the battery in hours. It's the time after which we must replace it if we did not exceed the maximum throughput,
                                                "capitalCost": float, the cost of a 1kWh battery in $,
                                                "replacementCost": float, the cost to replace 1kWh of batteries in $,
                                                "operationalCost": float, the cost PER HOUR, to operate and maintain the battery ($)
                                            },
                                "diesel" : {
                                                "maxPower": float, the generator nominal power (kW),
                                                "fuelCost": float, the cost of 1l of fuel ($),
                                                "fuelCostGrad": float, there is a fuel curve modeling the relationship between the functionning power of the dg and it's consumption of liters fuel per kW. This parameter is the slope of the model curve,
                                                "fuelCostIntercept": float, there is a fuel curve modeling the relationship between the functionning power of the dg and it's consumption of liters fuel per kW. This parameter is the intercept of the model curve,
                                                "lifetime": int, the nominal lifetime of the dg in hours,
                                                "capitalCost": float, the cost of the dg in $,
                                                "replacementCost": float, the cost to replace the dg in $,
                                                "operationalCost": float, the cost PER HOUR, to operate and maintain the dg,
                                            },
                                "photovoltaic" : {
                                                    "maxPower": float, the nominal power of a pannel (kWP),
                                                    "lifetime": int, the nominal lifetime of a pannel in hours,
                                                    "capitalCost": float, the cost of a pannel in $,
                                                    "replacementCost": float, the cost to replace a pannel in $,
                                                    "operationalCost": float, the cost PER HOUR, to operate and maintain the pannel ($),
                                                    "powerTimeVector": numpy array, the power output of the pannel at each time step (kW)
                                                }
                            }
       - timeStep : float, the time step of the simulation that generated the load in hours
       - loadVector : numpy array of floats, the power demand on the grid (kW)
       - projectDuration : int, the duration of the whole project in hours (e.g 25 * 365 * 24)
       - discountRate: float, the discount ratio
       - strategy : "LF" or "CC", respectively for "Load Following" or "Cycle Charging"
   OUTPUTS :
       - totalEmissionCO2hourly : float, the average emission of CO2 across the entire project lifespan by Diesel Generator + PV + Battery in (kgCO2eq/h)
    """
    # First, we need to compute the netLoadVetor from the loadVector and the power generated by renewables
    normalizingFactor = 52
    pvPowerVector = ((gridComponents["photovoltaic"]["powerTimeVector"])/normalizingFactor)*(gridComponents["photovoltaic"]["maxPower"])
    netLoadVector = loadVector - pvPowerVector

    # Now we need to run the dispatching loop
    specifications = [gridComponents["battery"]["maxStorage"], gridComponents["diesel"]["maxPower"], gridComponents["battery"]["maxInputPow"], gridComponents["battery"]["maxOutputPow"], gridComponents["battery"]["SOC_min"]]
    batteryInitialStorage = gridComponents["battery"]["initialStorage"]
    dispatchingResult = dispatchingLoop(timeStep, netLoadVector, batteryInitialStorage, specifications, strategy)

    # Now we extract the battery storage at each time step as well as the power of the dg at each time step
    batteryStorageVector, generatorPowerVector = dispatchingResult[0], dispatchingResult[1]
    batteryPowerVector = [energy/timeStep for energy in batteryStorageVector]

    # Emission (kg) per litre of diesel fuel consumed
    co2PerLitre = 2.65 #kg/L
    generatorPowerVector = np.tile(generatorPowerVector, projectDuration//(24 * 365))

    # Now we calculate the hourly emission of CO2 in kg by the Diesel Generator 
    N_years = projectDuration//8760
    for elem in range(1,N_years+1):
      fuelConsumptionResult = []  
      for i in range(8760*(elem-1) , 8760*elem):
          if generatorPowerVector[i] > 0.25*gridComponents["diesel"]["maxPower"]:
              fCon = gridComponents["diesel"]["fuelCostGrad"]*generatorPowerVector[i] + gridComponents["diesel"]["fuelCostIntercept"]
              fuelConsumptionResult.append(fCon)
    totalFuelConsumption = sum(fuelConsumptionResult)
    emiCO2Gen = co2PerLitre*totalFuelConsumption #kgCO2e

    # Now we multiply the emission by an upstream factor to take into account life-cycle CO2 production
    upstreamFactor = 1.2
    emiCO2Gen = emiCO2Gen * upstreamFactor #kgCO2e
    
    # Taking into account manufacturing emission for battery
    co2PerCapacity = 0.72 # kgCO₂/kWh 
    emiCO2Batt = co2PerCapacity*gridComponents["battery"]["maxStorage"]

    # Taking into account carbon footprint of PV (6gCO2e/kWh)
    co2PerkWhPV = 6e-3
    normalizingFactor = 52
    pvPowerVector = ((gridComponents["photovoltaic"]["powerTimeVector"])/normalizingFactor)*(gridComponents["photovoltaic"]["maxPower"])
    emiCO2Pv = sum(pvPowerVector)*8760*co2PerkWhPV

    # Total CO2 emission for project lifespan (kgCO2e)
    totalEmissionCO2 = emiCO2Gen + emiCO2Batt + emiCO2Pv

    # Average per hour C02 emission for entire project lifespan (kgCO2e/h)
    totalEmissionCO2hourly = totalEmissionCO2/projectDuration

    return totalEmissionCO2hourly