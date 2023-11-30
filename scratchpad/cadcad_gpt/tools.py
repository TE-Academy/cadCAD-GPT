from radcad import Model, Simulation, Experiment, Engine
import pandas as pd
from pydantic import create_model
import inspect
from inspect import Parameter
import plotly.express as px
from typing import List, Callable, Dict, Union, Any
#analysis agent imports
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain.chat_models import ChatOpenAI
from langchain.agents.agent_types import AgentType
#vector database documentation agent imports
from langchain.prompts import ChatPromptTemplate
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
import openai


class Toolkit:
    """
    A class representing a toolkit for working with a cadCAD Python model.

    Attributes:
        model (radcad.Model): The cadCAD model.
        simulation (radcad.Simulation): The cadCAD simulation.
        experiment (radcad.Experiment): The cadCAD experiment.
        df (pandas.DataFrame): The dataframe to use for function execution.

    """
    def __init__(self, model: Model, simulation: Simulation, experiment: Experiment, df: pd.DataFrame, docs: str):
        self.model = model
        self.simulation = simulation
        self.experiment = experiment
        self.df = df
        self.function_schemas = self.get_function_schemas()
        self.params = self.model.params
        self.docs = docs

    
    def get_function_schemas(self) -> List[Dict[str, Union[str, Any]]]:
        """
        Generates a schema for each function in the toolkit.

        The schema includes the function name, description, and parameters.

        Returns:
            list: A list of dictionaries representing the function schemas.

        """
        function_schemas = []
        for name, obj in inspect.getmembers(self):
            if inspect.ismethod(obj) and obj.__name__ != '__init__' and obj.__name__ != 'get_function_schemas':
                kw = {n: (o.annotation, ... if o.default == inspect.Parameter.empty else o.default)
                    for n, o in inspect.signature(obj).parameters.items()}
                s = create_model(f'Input for `{obj.__name__}`', **kw).schema()
                function_schemas.append(dict(name=obj.__name__, description=obj.__doc__, parameters=s))
        return function_schemas

    def change_param(self, param: str, value: float) -> str:
        """
        Changes the parameter of the cadCAD simulation and runs the simulation to update dataframe.

        Args:
            param (str): The name of the parameter to change. Must be a parameter of the model.
            value (float): The new value for the parameter.

        Returns:
            str: A message indicating the new parameter value and that the simulation dataframe has been updated.

        """
        if param not in self.model.params:
            return f'{param} is not a parameter of the model try choosing from {self.model.params.keys()}'
        value = float(value)
        self.simulation.model.params.update({
            param: [value]
        })
        self.experiment = Experiment(self.simulation)
        self.experiment.engine = Engine()
        result = self.experiment.run()
        # Convert the results to a pandas DataFrame
        self.df = pd.DataFrame(result)
        return f'new {param} value is {value} and the simulation dataframe is updated'

    
    def model_info(self, param: str) -> Union[Dict[str, float], str]:
        """
        Returns quantitative values of current state of the simulation parameters.

        Args:
            param (str): The name of the parameter to retrieve. If 'all', returns all parameters. Must be a parameter of the model.

        Returns:
            Union[Dict[str, float], str]: A dictionary of parameter names and values, or a message indicating that the parameter is not part of the model.

        Raises:
            ValueError: If the parameter name is not part of the model.

        """
        if param == 'all':
            output=''
            for param in self.simulation.model.params:
                output= output +f'\n{param} is {self.simulation.model.params[param]}'
            return output
        elif param in self.simulation.model.params:
            return f'{param} value is {self.simulation.model.params[param][0]}'
        else:
            return f'{param} is not a parameter of the model try choosing from {self.model.params.keys()}'

    # pandas agent as a tool

    def analysis_agent(self, question: str) -> str:
        """
        Analyzes the dataframe and returns the answer to the question.

        Args:
            question (str): The question to ask the dataframe.

        Returns:
            str: The answer to the question.

        """
        pandas_agent = create_pandas_dataframe_agent(ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613"),
                                                    self.df,
                                                    verbose=True,
                                                    agent_type=AgentType.OPENAI_FUNCTIONS)
        answer = pandas_agent.run(question)
        return answer

    def model_documentation(self, question: str) -> str:
        """
        Returns the documentation of the model.

        Args:
            question (str): The question to ask about the model documentation.

        Returns:
            str: The answer to the question based on the model documentation.

        """
        vectorstore = FAISS.from_texts([self.docs], embedding=OpenAIEmbeddings())
        retriever = vectorstore.as_retriever()

        template = """Answer the question based only on the following context:
        {context}

        Question: {question}
        """
        prompt = ChatPromptTemplate.from_template(template)
        model = ChatOpenAI()
        chain = (
            {"context": retriever, "question": RunnablePassthrough()} 
            | prompt 
            | model 
            | StrOutputParser()
        )
        info = chain.invoke(question)

        return info
    

    def plotter(self, natural_language_request: str) -> None:
        """
        Plots any visualizations using plotly express when given a natural language request.

        Args:
            natural_language_request (str): A natural language request for a plot with details about pkot congifurations. 

        Returns:
            None: The plot is displayed using the `fig.show()` function.

        """
        df = self.df
        systemprompt = f'''You are a plotly express data visualization expert. You will take a request from user and write back the python code to generate the plotly express visualization. The dataframe user is working with is df. and it has the following columns: {self.model.state.keys()}. Only output the python output enclosed in ``` backticks.'''
        completion = openai.ChatCompletion.create(
                model="gpt-4-1106-preview",
                max_tokens=500,
                messages=[
                    {
                    "role": "system",
                    "content": f"{systemprompt}"
                    },
                    {
                    "role": "user",
                    "content": f"{natural_language_request}"
                    }
                ],
                temperature=0,
                top_p=0.5,
            )
        answer = completion.choices[0].message.content
        code_to_run = answer.split('```')[1].replace('python', '')
        if 'plotly' in code_to_run:
            exec(code_to_run)

        return 'plotly visualization created'


            

    # def A_B_test(self, par1, val1, par2, val2, natural_language_request):
    #     """
    #     Perform an A/B test by updating the parameters par1 and par2 with values val1 and val2 respectively. Runs the experiment and returns the result of the A/B test.

    #     Args:
    #         par1 (str): The name of the first parameter to update.
    #         val1 (float): The value to set for the first parameter.
    #         par2 (str): The name of the second parameter to update.
    #         val2 (float): The value to set for the second parameter.
    #         natural_language_request (str): The natural language request that tests a metric on the dataframe generated by the A/B test. eg: which subset has the max value of prey_population?

    #     Returns:
    #         str: The answer to the question based on the A/B test.
    #     """
    #     initial_par1_value = self.simulation.model.params[par1][0]
    #     initial_par2_value = self.simulation.model.params[par2][0]
        
    #     self.simulation.model.params.update({
    #         par1: [val1, initial_par1_value],
    #         par2: [initial_par2_value, val2]
    #         })
        
    #     experiment = Experiment(self.simulation)
    #     experiment.engine = Engine()
    #     result = experiment.run()
    #     # Convert the results to a pandas DataFrame
    #     df = pd.DataFrame(result)

    #     systemprompt = f'''You are a python pandas helper. You are working with a dataframe called df and it has the following columns: {self.model.state.keys()}. The subset column 0 and 1 are to be compared on the metric that is given by the user. The code must print a string at the end explaining the comparision. Only output the python output enclosed in ``` backticks.'''
    #     completion = openai.ChatCompletion.create(
    #             model="gpt-4-1106-preview",
    #             max_tokens=500,
    #             messages=[
    #                 {
    #                 "role": "system",
    #                 "content": f"{systemprompt}"
    #                 },
    #                 {
    #                 "role": "user",
    #                 "content": f"{natural_language_request}"
    #                 }
    #             ],
    #             temperature=0,
    #             top_p=0.5,
    #         )
    #     answer = completion.choices[0].message.content
    #     code_to_run = answer.split('```')[1].replace('python', '')
    #     print(code_to_run)
    #     if 'df' in code_to_run:
    #         exec(code_to_run)

    #     return 'answer must be printed above'