import pandas as pd
import numpy as np
from radcad import Model, Simulation, Experiment
from radcad.engine import Engine, Backend

system_params = {
    'prey_reproduction_rate': [0.6],
    'predator_interaction_factor': [0.0002],
    'prey_interaction_factor': [0.002],
    'prey_death_rate': [0.02],
    'predator_death_rate': [1.0],
    'dt': [0.1]
}

initial_state = {
    'prey_population': 100,
    'predator_population': 50
}


def p_reproduce_prey(params, substep, state_history, prev_state, **kwargs):
    born_population = prev_state['prey_population'] * params['prey_reproduction_rate'] * params['dt']
    return {'add_prey': born_population}


def p_reproduce_predators(params, substep, state_history, prev_state, **kwargs):
    born_population = prev_state['predator_population'] * prev_state['prey_population'] * params['predator_interaction_factor'] * params['dt']
    return {'add_predators': born_population}


def p_eliminate_prey(params, substep, state_history, prev_state, **kwargs):
    population = prev_state['prey_population']
    natural_elimination = population * params['prey_death_rate']
    
    interaction_elimination = population * prev_state['predator_population'] * params['prey_interaction_factor']
    
    eliminated_population = natural_elimination + interaction_elimination * params['dt']
    return {'add_prey': -1.0 * eliminated_population}


def p_eliminate_predators(params, substep, state_history, prev_state, **kwargs):
    population = prev_state['predator_population']
    eliminated_population = population * params['predator_death_rate'] * params['dt']
    return {'add_predators': -1.0 * eliminated_population}


def s_prey_population(params, substep, state_history, prev_state, policy_input, **kwargs):
    updated_prey_population = np.ceil(prev_state['prey_population'] + policy_input['add_prey'])
    return ('prey_population', max(updated_prey_population, 0))


def s_predator_population(params, substep, state_history, prev_state, policy_input, **kwargs):
    updated_predator_population = np.ceil(prev_state['predator_population'] + policy_input['add_predators'])
    return ('predator_population', max(updated_predator_population, 0))


state_update_blocks = [
    {
        'policies': {
            'reproduce_prey': p_reproduce_prey,
            'reproduce_predators': p_reproduce_predators,
            'eliminate_prey': p_eliminate_prey,
            'eliminate_predators': p_eliminate_predators
        },
        'variables': {
            'prey_population': s_prey_population,
            'predator_population': s_predator_population            
        }
    }

]


TIMESTEPS = 1000
RUNS = 1


model = Model(initial_state=initial_state, state_update_blocks=state_update_blocks, params=system_params)
simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
experiment = Experiment(simulation)
# Select the Pathos backend to avoid issues with multiprocessing and Jupyter Notebooks
experiment.engine = Engine(backend=Backend.PATHOS)

# result = experiment.run()