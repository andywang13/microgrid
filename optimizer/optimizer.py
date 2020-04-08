# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 12:58:54 2020

@author: bastien velitchkine
"""

from costFunctionBuilder import costFunctionBuilder 
from platypus import NSGAII, Problem, Real

def optimizer(fixedParameters, costFunctions, constraints):
    """
            - fixedParameters: {gridComponents : {
                                                        "battery" : {
                                                                        "initialStorage": float between 0 and 1, the battery initial energy storage as a percentage of its maximum capacity,
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
                                                                        "fuelCost": float, the cost of 1l of fuel ($),
                                                                        "fuelCostGrad": float, there is a fuel curve modeling the relationship between the functionning power of the dg and it's consumption of liters fuel per kW. This parameter is the slope of the model curve,
                                                                        "fuelCostIntercept": float, there is a fuel curve modeling the relationship between the functionning power of the dg and it's consumption of liters fuel per kW. This parameter is the intercept of the model curve,
                                                                        "lifetime": int, the nominal lifetime of the dg in hours,
                                                                        "capitalCost": float, the cost of the dg in $,
                                                                        "replacementCost": float, the cost to replace the dg in $,
                                                                        "operationalCost": float, the cost PER HOUR, to operate and maintain the dg,
                                                                    },
                                                        "photovoltaic" : {
                                                                            "lifetime": int, the nominal lifetime of a pannel in hours,
                                                                            "capitalCost": float, the cost of a pannel in $,
                                                                            "replacementCost": float, the cost to replace a pannel in $,
                                                                            "operationalCost": float, the cost PER HOUR, to operate and maintain the pannel ($),
                                                                            "powerTimeVector": numpy array, the power output of the pannel at each time step (kW)
                                                                        }
                                                    },
                                    
                               timeStep : float, the time step of the simulation that generated the load in hours,
                               loadVector : numpy array of floats, the power demand on the grid (kW),
                               projectDuration : int, the duration of the whole project in hours (e.g 25 * 365 * 24),
                               discountRate: float, the discount ratio,
                               strategy : "LF" or "CC", respectively for "Load Following" or "Cycle Charging"
                               }
                - costFunctions : list of 
                    - lambda functions whose inputs are the arguments to optimize and outputs are the the floats corresponding to the costs we aim at minimizing
                - constraints : {
                                    "diesel":
                                                {
                                                        "upperBound": float, the upper Bound for the value of the generatorMaximumPower (kW),
                                                        "lowerBound": float, the lower Bound for the value of the generatorMaximumPower (kW),
                                                },
                                     "battery":
                                                {
                                                        "upperBound": float, the upper Bound for the value of the battery maximum storage capacity (kWh),
                                                        "lowerBound": float, the lower Bound for the value of the battery maximum storage capacity (kWh),
                                                },
                                     "photovoltaic":
                                                    {
                                                            "upperBound": float, the upper Bound for the value of the pvMaximumPower (kW),
                                                            "lowerBound": float, the upperlower Bound for the value of the pvMaximumPower (kW),
                                                    },           
                                }
                                                    
    OUTPUT:
        {
                "parameters":
                            {
                                    "battery": float, the battery storage capacity (kWh),
                                    "diesel": float, the generator maximum power (kW),
                                    "photovoltaic": float, the pv maximum power (kW)                                                
                            },
                "costs":
                        {
                                "dollars": float, the cost of the project in dollars,
                                "carbon": float, the carbon emissions generated by the project (kg)
                        }
                            
        }                                                    
    """        
    
    problem = Problem(3, 2)
    problem.types[:] = [Real(constraints["battery"]["lowerBound"], constraints["battery"]["upperBound"]), Real(constraints["diesel"]["lowerBound"], constraints["diesel"]["upperBound"]), Real(constraints["photovoltaic"]["lowerBound"], constraints["photovoltaic"]["upperBound"])]
    problem.function = costFunctionBuilder(fixedParameters["gridComponents"], fixedParameters["timeStep"], fixedParameters["loadVector"], fixedParameters["projectDuration"], fixedParameters["discountRate"], fixedParameters["strategy"])(vars[0], vars[1], vars[2])
    
    algorithm = NSGAII(problem)
    algorithm.run(10)
    
    # display the results
    for solution in algorithm.result:
        print(solution.objectives)
        
def optimizerTest():
    """
    A simple function to test the function `optimizer`
    """
    
    fixedParameters = {"gridComponents": {
                                                        "battery" : {
                                                                        "initialStorage": 1.,
                                                                        "maxInputPow": 6 * 157,
                                                                        "maxOutputPow": 6 * 500,
                                                                        "SOC_min": 0.,
                                                                        "maxThroughput": float, the maximum amount of energy that can flow in and out of the battery during its lifetime (kWh),
                                                                        "lifetime": int, the nominal lifetime of the battery in hours. It's the time after which we must replace it if we did not exceed the maximum throughput,
                                                                        "capitalCost": float, the cost of a 1kWh battery in $,
                                                                        "replacementCost": float, the cost to replace 1kWh of batteries in $,
                                                                        "operationalCost": float, the cost PER HOUR, to operate and maintain the battery ($)
                                                                    },
                                                        "diesel" : {
                                                                        "fuelCost": float, the cost of 1l of fuel ($),
                                                                        "fuelCostGrad": float, there is a fuel curve modeling the relationship between the functionning power of the dg and it's consumption of liters fuel per kW. This parameter is the slope of the model curve,
                                                                        "fuelCostIntercept": float, there is a fuel curve modeling the relationship between the functionning power of the dg and it's consumption of liters fuel per kW. This parameter is the intercept of the model curve,
                                                                        "lifetime": int, the nominal lifetime of the dg in hours,
                                                                        "capitalCost": float, the cost of the dg in $,
                                                                        "replacementCost": float, the cost to replace the dg in $,
                                                                        "operationalCost": float, the cost PER HOUR, to operate and maintain the dg,
                                                                    },
                                                        "photovoltaic" : {
                                                                            "lifetime": int, the nominal lifetime of a pannel in hours,
                                                                            "capitalCost": float, the cost of a pannel in $,
                                                                            "replacementCost": float, the cost to replace a pannel in $,
                                                                            "operationalCost": float, the cost PER HOUR, to operate and maintain the pannel ($),
                                                                            "powerTimeVector": numpy array, the power output of the pannel at each time step (kW)
                                                                        }
                                                    },
                                    
                               timeStep : float, the time step of the simulation that generated the load in hours,
                               loadVector : numpy array of floats, the power demand on the grid (kW),
                               projectDuration : int, the duration of the whole project in hours (e.g 25 * 365 * 24),
                               discountRate: float, the discount ratio,
                               strategy : "LF" or "CC", respectively for "Load Following" or "Cycle Charging"
                               }
                - costFunctions : list of 
                    - lambda functions whose inputs are the arguments to optimize and outputs are the the floats corresponding to the costs we aim at minimizing
                - constraints : {
                                    "diesel":
                                                {
                                                        "upperBound": float, the upper Bound for the value of the generatorMaximumPower (kW),
                                                        "lowerBound": float, the lower Bound for the value of the generatorMaximumPower (kW),
                                                },
                                     "battery":
                                                {
                                                        "upperBound": float, the upper Bound for the value of the battery maximum storage capacity (kWh),
                                                        "lowerBound": float, the lower Bound for the value of the battery maximum storage capacity (kWh),
                                                },
                                     "photovoltaic":
                                                    {
                                                            "upperBound": float, the upper Bound for the value of the pvMaximumPower (kW),
                                                            "lowerBound": float, the upperlower Bound for the value of the pvMaximumPower (kW),
                                                    },           
                                }