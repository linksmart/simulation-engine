# DSF Simulation Engine API
DSF Simulation Engine (DSF-SE) API is a web-based API to that enables online interaction with power simulator, i.e., OpenDSS.

## Getting Started
These instructions will get you a copy of the project up and running for development and testing purposes.
###Getting the Source from the Repository
$git clone https://sisay.chala@code.linksmart.eu/scm/se/dsf_se.git

### Modifying the code
modify swagger definition on swager editor,
generate code from swagger
download the generated model and replace the existing model
replace the existing swagger file with the new one
modify the simulation_controller.py, controller.py, and opendss.py according to the new model

NB: To save time, you may also do these steps manually, i.e., modify swagger file, modify corresponing code in model, simulation_controller.py, controller.py and opendss.py files

### Pre-requisite 
Using this API, requires availability of docker environment. All the required dependencies are specified and contained in the package.

### Building and Running the Simulation Engine
$docker-compose build && docker-compose up # after every change

Once the simulation engine starts running, you can send simulation requests via clients such as PostMan 

### Using the Simulation Engine API
BaseURL: http://<<ip>>:port/se

#### Create Simulation
- Method: post
- End Point: /simulation
- Input: JSON file of GRID definition
- Output: Simulation id


#### Run Simulation
once simulation is successfully created, you can run the simulation
- Method: post 
- End Point: /commands/run/<<simulation id>>
- Input: simulation id
- Output: Simulation result (at the moment): array of Node Names, and Voltage MagPus


Simulation id returned after creating simulation is used as a parameter to run the simulation

#### Get Simulation Result
once simulation is successfully run, you can obtain the simulation results
- Method: get
- End Point: /simulationResult/<<simulation id>>
- Input: Simulation id
- Output: Result of simulation, i.e., Returns result of “Run Simulation” to client


#### Abort Simulation 
- Method: post
- End Point: /commands/abort/<<simulation id>> 
Note: you can abort a running simulation


#### update Simulation
- Method: put
- End Point: simulation/<<simulation id>> 
Note: Simulation id is the id returned by the successfull creation of simulation in the above step


#### Delete Simulation
- Method: delete
- End Point: /simulation/<<simulation id>> 
Note: simulation id is the id returned by the successfull creation of simulation in the above step