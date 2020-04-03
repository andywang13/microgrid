Compiling of functions together, and running them under the simulator. Feed inputs and simulator function into the optimization function

The aim is to 1) Minimize the cost function (Total cost of PV+Battery+Generator)
              2) 2nd Objective Here
              
# Architecture
  - 📁 simulator
      - 📁 dispatching
          - 📑 dispatchingStrategyFunction.py
      - 📁 costs
          - 📁 dollars
              - 📁 battery
                  - 📑 auxilliaryCostFunctions.py
                  - 📑 batteryCost.py
              - 📁 pv
                  - 📑
                  - 📑
              - 📁 diesel
                  - 📑
                  - 📑
              - 📁 windmill
                  - 📑
                  - 📑
          - 📁 carbon (afterwards)
  - 📁 optimizer
  - 📁 communication (the functions that ensure the communication between the optimizer and the simulator)
  - 📑 README.md
