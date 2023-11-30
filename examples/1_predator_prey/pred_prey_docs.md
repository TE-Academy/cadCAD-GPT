# Predator-Prey Simulation Documentation

(Chatgpt Generated docs based on Danilo's (@danlessa) Radcad example model. Here's the link for the same: https://github.com/CADLabs/radCAD/tree/master/examples)

Welcome to the documentation for our Predator-Prey Simulation. This simulation models the interactions between a population of prey and a population of predators over time. The simulation parameters, initial states, and logic are described below.

## Parameters

The simulation is configured with the following parameters:

- **Prey Reproduction Rate** (`prey_reproduction_rate`): This parameter represents the rate at which prey reproduce. It's a value that influences the growth of the prey population.

- **Predator Interaction Factor** (`predator_interaction_factor`): The predator interaction factor determines how predators interact with prey. A higher value indicates a stronger interaction.

- **Prey Interaction Factor** (`prey_interaction_factor`): This factor signifies the interaction strength of prey with predators. It influences how prey population is affected by the presence of predators.

- **Prey Death Rate** (`prey_death_rate`): The prey death rate determines the natural mortality rate of the prey population.

- **Predator Death Rate** (`predator_death_rate`): This parameter sets the predator death rate, which represents the natural death rate of predators.

- **Time Step** (`dt`): The time step (`dt`) defines the duration of each time step in the simulation, influencing the granularity of the simulation.

## Initial States

At the beginning of the simulation, the following initial states are set:

- **Prey Population** (`prey_population`): The initial population of prey is 100 individuals.

- **Predator Population** (`predator_population`): The initial population of predators is 50 individuals.

## Simulation Logic

The simulation progresses through time by following a set of ecological principles and mathematical equations:

### Prey Population Dynamics

The prey population evolves as follows:

- **Birth of Prey Population**: New prey are born based on the previous state's prey population, the prey reproduction rate, and the time step. This is represented as:


- **Predator-Induced Elimination of Prey**: Predators influence the prey population by causing eliminations based on their interaction factor, the previous prey population, and the time step. This is represented as:


- **Natural Elimination of Prey**: Prey experience natural mortality based on the prey death rate and the current population:

- **Interaction-Induced Elimination of Prey**: Prey can be eliminated due to the interaction with predators. The elimination rate depends on the current prey population, the predator population, the prey interaction factor, and the time step. This is represented as:


- **Overall Elimination of Prey Population**: The total eliminated population of prey is the sum of natural and interaction-induced elimination, scaled by the time step.

### Predator Population Dynamics

The predator population evolves as follows:

- **Predator-Induced Elimination**: Predators can eliminate prey, resulting in the predator-induced elimination based on the predator death rate and the time step:


This simulation logic captures the dynamics of the predator-prey relationship and allows you to explore the population changes of both prey and predators over time.

For detailed instructions on running and customizing the simulation, please refer to the [How to Use the Simulation](#how-to-use-the-simulation) section.



## Assumptions and Limitations

To effectively use and interpret the results of this simulation, it's essential to understand the assumptions made during its design and the inherent limitations:

### Assumptions

1. **Homogeneous Environment**: The simulation assumes a homogeneous environment where there are no spatial variations or variations in resource availability. In reality, ecosystems can be complex with varying landscapes and resource distribution.

2. **Constant Parameters**: The simulation assumes constant parameter values throughout the simulation. For example, prey and predator interaction factors are considered to be unchanging. In real ecosystems, these factors can vary due to environmental conditions.

3. **Instantaneous Interactions**: The model represents predation and reproduction as instantaneous events, simplifying the complexities of real-world predator-prey interactions. In reality, these events can occur over time with varying dynamics.

### Limitations

1. **Simplified Model**: The simulation is a simplified representation of a predator-prey relationship. It does not consider additional ecological factors, such as competition among prey species, predator interference, or spatial heterogeneity.

2. **Deterministic Nature**: The simulation's deterministic nature means that each run with the same initial conditions and parameters will yield identical results. In real ecosystems, stochasticity plays a significant role.

3. **Parameter Sensitivity**: Small changes in parameters can result in significant variations in outcomes. Users should be cautious when interpreting results, especially when applying them to real ecosystems.

4. **Predator-Prey Dynamics**: While the simulation captures predator-prey dynamics, it simplifies these interactions. In reality, predator-prey dynamics can be influenced by numerous factors, including food availability, predator learning, and more.

5. **Environmental Factors**: Environmental factors such as habitat destruction, disease, and human intervention are not considered in the simulation. These factors can have a substantial impact on real ecosystems.

Understanding these assumptions and limitations is crucial for using the simulation responsibly and interpreting the results within the context of a simplified model. Users are encouraged to use the simulation as a learning tool and as a way to explore basic predator-prey dynamics while recognizing its inherent simplifications.