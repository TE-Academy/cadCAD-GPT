import pandas as pd
import numpy as np
from radcad import Model, Simulation, Experiment
from radcad.engine import Engine, Backend

system_params = {
    'param1': [2],
}

state_variables = {
    'state_var1': 1,
    'state_var2': 2
}

def p_policy1(params, substep, state_history, prev_state, **kwargs):
    addition_to_state_var1 = prev_state['state_var1'] * params['param1']
    return {'addition_to_state_var1': addition_to_state_var1}


def s_update1(params, substep, state_history, prev_state, policy_input, **kwargs):
    updated_var1 = np.ceil(prev_state['state_var1'] + policy_input['addition_to_state_var1'])
    return ('state_var1', max(updated_var1, 0))



state_update_blocks = [
    {
        'policies': {
            'policy_1': p_policy1,
        },
        'variables': {
            'state_var1': s_update1,           
        }
    }

]




TIMESTEPS = 40
RUNS = 1


model = Model(initial_state=state_variables, state_update_blocks=state_update_blocks, params=system_params)
simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
experiment = Experiment(simulation)
# Select the Pathos backend to avoid issues with multiprocessing and Jupyter Notebooks
experiment.engine = Engine(backend=Backend.PATHOS)

# result = experiment.run()