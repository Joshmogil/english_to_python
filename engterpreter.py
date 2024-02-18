
import os
from dotenv import load_dotenv, find_dotenv
from typing import Any, Sequence

from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool

from langchain.agents import AgentExecutor, create_openai_tools_agent

from langchain_openai import ChatOpenAI

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


from langchain_core.messages import BaseMessage, AIMessage, HumanMessage

from prompts import ENGTERPRETER_SYSTEM_PROMPT, ENGTERPRETER_CODER_PROMPT, PROMPT_FACTORY





"""
The engterperter is a tool that allows you to write code in English and have it translated into Python code.
It is designed to be used in an interactive environment, such as a Jupyter notebook or a Python shell.
It works in the following way:
1. You write a sentence in English that describes your application
2. The engterpreter translates the sentence into a business logic model
3. The engterpreter generates functions, classes and methods based on the business logic model
4. The engterpreter generates a semantic model of the business logic using the generated code
5. The engterpreter generates code for the business logic model

"""


class Function(BaseModel):
    name :str = Field(description="The name of the function, use snake case")
    arguments : str = Field(description="The arguments of the function and their types", example={"name": "str", "age": "int"})
    returns : str = Field(description="The return value(s) of the function and their types")
    description: str = Field(description="A description of the function, describing what it does and how it works")
    #code: str = Field(description="The code for the function")



class Structure(BaseModel):
    name : str = Field(description="The name of the structure, use snake case")
    attributes: str = Field(description="The attributes of the structure and their types", example={"name": "str", "age": "int"})
    description: str = Field(description="A description of the structure, describing what it does and how it works")
    #code: str = ""


class Relationship(BaseModel):
    """A relationship between two structures, methods or functions"""

    name: str = Field(description="The name of the relationship")
    rationale: str = Field(description="The rationale for the relationship")
    actor: str = Field(description="The name of the actor structure or function")
    reciever: str = Field(description="The name of the reciever structure or function")
    relation: str = Field(description="One single verb descriging the relationship between the actor and the reciever", example="uses")


class Handoff(BaseModel):
    """A handoff of work from one agent to another"""
    handoff: str = Field(description="The name of the agent to handoff work to", example="CODER")

class CodeSegment(BaseModel):
    """A segment of code"""
    name: str = Field(description="The name of the code segment, must be a function or structure from the application model")
    code: str = Field(description="A block of code that is either a function or a structure's full implementation")


class Application(BaseModel):
    app_name: str =""
    functions: dict[str, Function] = {}
    structures: dict[str, Structure] = {}
    relationships: dict[str, Relationship] = {}
    application_logic: str = ""

class CodeBase(BaseModel):
    code_segments: dict[str,CodeSegment] = {}


### Global state
application_model: Application = Application()
code_base: CodeBase = CodeBase()

application_code: str = ""

current_agent= "ARCHITECT" # or "CODER"




@tool(args_schema=Handoff)
def handoff_work_to_coder(**kwargs) -> str:
    """handoff the work of writing the code to the coder."""
    print("Beginning code generation")
    global current_agent
    current_agent = "CODER"

    return "The work has been handed off to the coder."

@tool(args_schema=Handoff)
def handoff_work_to_architect(**kwargs) -> str:
    """handoff the work of designing the application model to the architect."""
    print("Beginning code generation")
    global current_agent
    current_agent = "ARCHITECT"
    return "Going back to design phase."

@tool
def create_or_update_application_logic(application_logic: str) -> str:
    """Create or update the current application logic based on initial user input OR iterative feedback."""
    application_model.application_logic = application_logic
    return "The application's logic flow has been updated."

@tool
def create_or_update_application_name(application_name: str) -> str:
    """Create or update the applications name."""
    application_model.application_logic = application_name
    return "The application's name has been updated."

@tool(args_schema=Structure)
def add_or_update_structure_to_application_model(**kwargs) -> str:
    """Add or update structure to the application model."""
    application_model.structures[kwargs['name']] = Structure(**kwargs)
    return f"The structure {kwargs['name']} has been modified in the application model."

@tool(args_schema=Structure)
def remove_structure_from_application_model(name: str) -> str:
    """Remove structure from the application model."""
    if name in application_model.structures:
        del application_model.structures[name]
        return f"The structure {name} has been removed from the application model."
    else:
        return f"The structure {name} does not exist in the application model."

@tool(args_schema=Function)
def add_or_update_function_to_application_model(**kwargs) -> str:
    """Add or update function to the application model."""
    #print(kwargs)
    application_model.functions[kwargs['name']] = Function(**kwargs)
    return f"The function {kwargs['name']} has been modified in the application model."

@tool(args_schema=Function)
def remove_function_from_application_model(name: str) -> str:
    """Remove function from the application model."""
    if name in application_model.functions:
        del application_model.functions[name]
        return f"The function {name} has been removed from the application model."
    else:
        return f"The function {name} does not exist in the application model."

@tool(args_schema=Relationship)
def add_or_update_relationship_to_application_model(**kwargs) -> str:
    """Add or update a relationship between structures/functions to the application model."""
    #print(kwargs)
    try:
        application_model.relationships[kwargs['name']] = Relationship(**kwargs)
        return f"The relationship {kwargs['name']} has been modified in the application model."
    except Exception as e:
        print(e)
        return f"An error occured while adding the relationship to the application model: {e}"

@tool(args_schema=Relationship)
def remove_relationship_from_application_model(name: str) -> str:
    """Remove relationship from the application model."""
    if name in application_model.relationships:
        del application_model.relationships[name]
        return f"The relationship {name} has been removed from the application model."
    else:
        return f"The relationship {name} does not exist in the application model."

@tool(args_schema=CodeSegment)
def add_or_update_code_segment_to_code_base(**kwargs) -> str:
    """Add or update code segment to the code base."""
    code_base.code_segments[kwargs['name']] = CodeSegment(**kwargs)
    return f"The code for {kwargs['name']} has been updated in the code base."

@tool(args_schema=CodeSegment)
def remove_code_segment_from_code_base(**kwargs) -> str:
    """Add or update code segment to the code base."""
    code_base.code_segments[kwargs['name']] = CodeSegment(**kwargs)
    return f"The code for {kwargs['name']} has been updated in the code base."

architect_tools: Sequence[Any] = [
    create_or_update_application_logic,
    create_or_update_application_name,
    add_or_update_structure_to_application_model,
    add_or_update_function_to_application_model,
    add_or_update_relationship_to_application_model,
    remove_function_from_application_model,
    remove_relationship_from_application_model,
    remove_structure_from_application_model,
    handoff_work_to_coder
    ]   

coder_tools: Sequence[Any] = [
    add_or_update_code_segment_to_code_base,
    remove_code_segment_from_code_base,
    handoff_work_to_architect
    ]   


class Engterpreter():

    def __init__(self, arch_model: str = "gpt-3.5-turbo-1106", coder_model: str = "gpt-3.5-turbo-1106"):
        self.program_context: str = "No program context yet. Make sure to ask the user for context of the program."

        arch_prompt= ChatPromptTemplate.from_messages(
            [
                ("system", ENGTERPRETER_SYSTEM_PROMPT),
                MessagesPlaceholder("chat_history", optional=True),
                ("human", "{input}"),
                MessagesPlaceholder("agent_scratchpad"),
            ]
        )

        coder_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", ENGTERPRETER_CODER_PROMPT),
                MessagesPlaceholder("chat_history", optional=True),
                ("human", "{input}"),
                MessagesPlaceholder("agent_scratchpad"),
            ]
        ) 

        arch_llm = ChatOpenAI(model=arch_model, temperature=0)
        coder_llm = ChatOpenAI(model=coder_model, temperature=0)
        self.architect_agent = create_openai_tools_agent(arch_llm, architect_tools, arch_prompt)
        self.coder_agent = create_openai_tools_agent(coder_llm, coder_tools,coder_prompt)
        self.architect_chat_history: list[BaseMessage] = [
            HumanMessage(content="I'm working on building a program, can you help me?"),
            AIMessage(content="Sure, let's first figure out what some of the requirements are for the program then we can start building a semantic model of the business logic."),]
        self.coder_chat_history: list[BaseMessage] = [
            HumanMessage(content="I'm working on building a program, can you help me?"),
            AIMessage(content="Sure, let's first figure out what some of the requirements are for the program then we can start building a semantic model of the business logic."),]

    def render_code_base(self) -> str:
        code_base_str = ""
        for segment_name in code_base.code_segments:
            code_base_str += f"{code_base.code_segments[segment_name].code}\n"
        return code_base_str

    def refresh_program_context(self) -> str:
        
        program_context = "BEGIN - APPLICATION MODEL\n"
        program_context += f"\nHow this application should work: {application_model.application_logic}\n"
        structure_header = "\nData Structures for this program: \n"
        functions_header = "\nFunctions for this program: \n"
        relationships_header = "\nRelationships between data structures and functions for this program. These are more metadata about interactions between Structures and Functions: \n"
        code_base_header = "\nBEGIN - CODE\n"

        program_context += structure_header
        for structure_name in application_model.structures:
            structure: Structure = application_model.structures[structure_name]
            program_context += f"A Structure: {structure.json()}\n"


        program_context += functions_header
        for function_name in application_model.functions:
            function: Function = application_model.functions[function_name]
            program_context += f"A Function: {function.json()}\n"

        program_context += relationships_header
        for relationship_name in application_model.relationships:
            relationship: Relationship = application_model.relationships[relationship_name]
            program_context += f"A Relationship: {relationship.json()}\n"
        
        program_context += "END - APPLICATION MODEL\n"

        program_context += code_base_header
        program_context += self.render_code_base()
        program_context += "\nEND - CODE\n"


        self.program_context = program_context


        print("Program context refreshed.")

        return program_context

    def read_in(self, english_sentence: str):
        self.refresh_program_context()
        global current_agent

        if current_agent == "ARCHITECT":

            agent_executor = AgentExecutor(agent=self.architect_agent, tools=architect_tools, verbose=True)

            output = agent_executor.invoke(
                    {
                    "input": PROMPT_FACTORY(ENGTERPRETER_SYSTEM_PROMPT, self.program_context, english_sentence),
                    "chat_history": self.architect_chat_history
                }
            )
            self.refresh_program_context()
            #print(output["output"])

        if current_agent == "CODER":
            agent_executor = AgentExecutor(agent=self.coder_agent, tools=coder_tools, verbose=True)

            output = agent_executor.invoke(
                    {
                    "input": PROMPT_FACTORY(ENGTERPRETER_CODER_PROMPT, self.program_context, english_sentence),
                    "chat_history": self.coder_chat_history
                }
            )
            self.refresh_program_context()
            #print(output["output"])

    def interpret(self):
        print("Engterpreter is running. Enter a program idea in English!")
        try:
            while True:

                with open("interpreter_context.txt", "w") as f:
                    # Writing data to a file
                    f.writelines(engterpreter.program_context)

                json_object = application_model.json()
            
                # Writing to sample.json
                with open("application_model.json", "w") as f:
                    f.write(json_object)

                if self.render_code_base() != "":
                    file_name = application_model.app_name + ".py"
                    print(f"Writing program to {file_name}.")
                    with open(file_name, "w") as f:
                        f.write(self.render_code_base())

                user_response = input("User input:")
                print(user_response)
                engterpreter.read_in(user_response)
        except KeyboardInterrupt:
            print("Exiting Engterpreter.")
            exit(0)


def create_env_file():
    # Check if .env file exists
    if not os.path.isfile('.env'):
        # If not, create it
        with open('.env', 'w') as f:
            pass

        with open('.env', 'a') as f:
            f.write(f'OPENAI_API_KEY=')
        print('Please enter your OpenAI API token in the created .env file')
        exit(0)
    else:
        print('Using existing .env file')

create_env_file()
load_dotenv(find_dotenv())




engterpreter = Engterpreter(arch_model="gpt-3.5-turbo-1106",coder_model="gpt-3.5-turbo-1106")
engterpreter.interpret()

