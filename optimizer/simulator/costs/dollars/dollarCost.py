# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 12:33:58 2020

@author: bastien velitchkine

Edited on Tues Apr 7 07:19:43 2020

@author: yun bin choh
"""
import numpy as np

from simulator.costs.dollars.battery.batteryCost import batteryCost
from simulator.costs.dollars.dg.dgCost import dgCost
from simulator.costs.dollars.pv.pvCost import pvCost
from simulator.dispatching.dispatchingLoop import dispatchingLoop


def dollarCost(gridComponents, timeStep, loadVector, projectDuration, discountRate, strategy):
    """
    INPUTS :
        - gridComponents : 
                            {
                                "battery" : {
                                                "maxStorage": float, the battery capacity storage (kWh),
                                                "initialStorage": float between 0 and 1, the battery initial energy storage as a percentage of its maximum storage capacity,
                                                "maxInputPow": float, the maximum charging power of the battery in kW for a 1kWh battery. The real value will be obtained by multiplying by the maximum storage capacity,
                                                "maxOutputPow": float, the maximum discharging power of the battery in kW for a 1kWh battery. The real value will be obtained by multiplying by the maximum storage capacity,
                                                "SOC_min": float, the minimum amount of energy that can be stored in the battery as a percentage of the maximum storage capacity,
                                                "maxThroughput": float, the number by which we multiply the max storage to get the maximum amount of energy that can flow in and out of the battery during its lifetime (kWh),
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
       - totalCost : float, the total cost of the project in $
    """
    # First, we need to compute the netLoadVetor from the loadVector and the power generated by renewables
    normalizingFactor = 52
    pvPowerVector = ((gridComponents["photovoltaic"]["powerTimeVector"])/normalizingFactor)*(gridComponents["photovoltaic"]["maxPower"])
    netLoadVector = loadVector - pvPowerVector
    
    # Now we need to run the dispatching loop
    battMaxInputPow = gridComponents["battery"]["maxInputPow"] * gridComponents["battery"]["maxStorage"]
    battMaxOutputPow = gridComponents["battery"]["maxOutputPow"] * gridComponents["battery"]["maxStorage"]
    SOC_min = gridComponents["battery"]["SOC_min"] * gridComponents["battery"]["maxStorage"]
    
    specifications = [gridComponents["battery"]["maxStorage"], gridComponents["diesel"]["maxPower"], battMaxInputPow, battMaxOutputPow, SOC_min]
    batteryInitialStorage = gridComponents["battery"]["initialStorage"] * gridComponents["battery"]["maxStorage"]
    dispatchingResult = dispatchingLoop(timeStep, netLoadVector, batteryInitialStorage, specifications, strategy)
    
    # Now we extract the battery storage at each time step as well as the power of the dg at each time step
    batteryStorageVector, generatorPowerVector = dispatchingResult[0], dispatchingResult[1]
    batteryPowerVector = [energy/timeStep for energy in batteryStorageVector]
    
    # Now we have everything we need to compute each specific cost
    
    # BATTERY COST
    timeVariables = [timeStep, projectDuration]
    costVariables = [gridComponents["battery"]["replacementCost"], gridComponents["battery"]["operationalCost"], gridComponents["battery"]["capitalCost"]]
    batteryVariables = [gridComponents["battery"]["maxThroughput"] * gridComponents["battery"]["maxStorage"], gridComponents["battery"]["lifetime"]]
    battery = batteryCost(batteryPowerVector, discountRate, timeVariables, costVariables, batteryVariables)
    
    # DIESEL GENERATOR COST
    generatorPowerVector = np.tile(generatorPowerVector, projectDuration//(24 * 365))
    dg = dgCost(generatorPowerVector,
                 projectDuration//(24 * 365),
                 gridComponents["diesel"]["maxPower"],
                 gridComponents["diesel"]["fuelCost"],
                 gridComponents["diesel"]["capitalCost"],
                 gridComponents["diesel"]["replacementCost"],
                 gridComponents["diesel"]["operationalCost"],
                 gridComponents["diesel"]["lifetime"],
                 discountRate*100,
                 gridComponents["diesel"]["fuelCostGrad"],
                 gridComponents["diesel"]["fuelCostIntercept"])

    # PV COST
    pvPowerVector = np.tile(pvPowerVector,projectDuration//(24 * 365))
    pv = pvCost(pvPowerVector,
                 projectDuration//(24 * 365),
                 gridComponents["photovoltaic"]["maxPower"],
                 gridComponents["photovoltaic"]["capitalCost"],
                 gridComponents["photovoltaic"]["replacementCost"],
                 gridComponents["photovoltaic"]["operationalCost"],
                 gridComponents["photovoltaic"]["lifetime"],
                 discountRate*100)
    
    totalCost = battery + dg + pv
#    print("The total cost is : {}$\n".format(totalCost))
    return totalCost