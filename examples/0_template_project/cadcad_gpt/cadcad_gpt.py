from typing import List, Dict
from radcad import Experiment, Model, Simulation
from .utils import plan_parser, print_color
from .agents import PlannerAgent, ExecutorAgent
from .tools import Toolkit
import json
import pandas as pd

class CadCAD_GPT:
    def __init__(self, api_key: str, model: Model, simulation: Simulation, experiment: Experiment, docs:str = ''):
        """
        Class initialization function.

        Parameters:
        model (Model): RadCAD model object
        simulation (Simulation): RadCAD simulation object
        experiment (Experiment): RadCAD experiment object
        docs (str): Documentation for the model, as a string
        api_key (str): OpenAI API key
        """
        self.model = model
        self.simulation = simulation
        self.experiment = experiment
        self.docs = docs
        self.api_key = api_key
        self.df = pd.DataFrame(self.experiment.run())

        # Create a Toolkit object
        self.toolkit = Toolkit(self.model, self.simulation, self.experiment, self.df, self.docs)

        # Extract function schema list from toolkit for subsequent agent usage
        self.function_schemas = self.toolkit.function_schemas
        self.function_name_descriptions = [(function['name'],function['description'].split('\n')[1]) for function in self.function_schemas]

        # Create Planner and Executor agent
        self.planner_agent = PlannerAgent(self.function_name_descriptions, self.api_key)
        self.executor_agent = ExecutorAgent(self.df, self.function_schemas,  self.model.params.keys() ,self.api_key)

    def __call__(self, user_input: str):
        """
        Function to process user input, create plans and execute them
        using planner and executor agents.

        Parameters:
        user_input (str): command or input from the user

        Returns:
        str: reply from the agent, after processing user input and executing tasks
        """

        # Pass user input to planner agent
        reply = self.planner_agent(user_input)
        # Parse agent's reply into a plan
        plan_list = plan_parser(reply)
        # If there's no plan, return the agent's reply
        if plan_list == []:
            return reply

        # If there are plans, they are printed and executed one by one
        print_color("Planner Agent:", "35")
        print('I have made a plan to follow:')
        # print plan one by one along with its index
        for i, plan in enumerate(plan_list):
            print(f'Step {i+1} {plan}')
        print('\n')

        # Clear old chat history of executor agent
        self.executor_agent.delete_all_messages()

        # Execute plans one by one
        for plan in plan_list:
            self.executor_agent.add_message({"role": "user", "content": plan})

            print_color("Executor Agent:", "36")
            thought = f'Thought: My task is to {plan}'
            print(thought)
            
            #Send plan to executor agent
            message = self.executor_agent(plan)

            # If message.content is None, executor agent has made a function call and we need to execute it
            if (message.content==None):
                function_name = message.function_call.name
                function_args = json.loads(message.function_call.arguments)
                action = 'Action: I should call ' + str(function_name) + ' function with these ' + str(function_args) + ' arguments.'
                print(action)
                observation1 = 'Observation: ' 
                observation2 = str(eval(f'self.toolkit.{function_name}')(**function_args))
                observation = observation1 + observation2

                print(observation1)
                if plan == plan_list[-1]:
                    print_color(observation2, "33")
                else: 
                    print_color(observation2, "32")
                
                # Reflect the changes made by the toolkit to the model, simulation, experiment and df.
                self.df = self.toolkit.df
                self.model = self.toolkit.model
                self.simulation = self.toolkit.simulation
                self.experiment = self.toolkit.experiment
                # update executor agent's chat history with the observation
                self.executor_agent.add_message({"role": "assistant", "content":observation})
    
            # If message.content is not None, executor agent has responded with a chat reply
            else:
                print('Response: ', message.content)
                return message.content

