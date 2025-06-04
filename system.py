from openai import OpenAI
import subprocess
import os
import json
from dotenv import load_dotenv
from cmd_executor import AutomatedCommandExecutor
from server_manager import ServerManager

load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

import subprocess
import sys

def run_commands(cmd_input):
    try:
       automatedCommandExecutor = AutomatedCommandExecutor()
       return automatedCommandExecutor.run_commands(cmd_input)
    except Exception as e:
        print(f"Error executing command: {e}")
        return f"Error: {str(e)}"
    

serverManager = ServerManager()
available_tools = {
    "run_commands": run_commands,
    "start_server": serverManager.start_server,
    "stop_server": serverManager.stop_server,
    "server_status": serverManager.server_status
}
SYSTEM_PROMPT = """
    You are a helpful assistant that solves user query and chat with the user.
    Your primary task is to assist user in creating applications by runing commands on the system.
    In order to solve any user's query, you have to break it down into steps and execute one step at a time.
    For the user's input, you have to analyse,think, action, observe , validate and then have to provide the result.
    You will be provided with a set of available tools that you can use to solve the user's query. You have to use them based on the user's query.
    The output should be a valid json object.

    IMPORTATNT: Before installing any dependencies, you have to check if the dependencies are already installed or not.

    Rules:
    1.You have break down the user's query into steps and execute one step at a time.
    2. You can use the available tools to solve the user's query.
    3. You have to provide the output in a valid json format.
    4. You have to assume that the user's system is nascent and it does not have any dependencies installed. So if nodejs or python is required, you have to install it first.
    5. Before installing any dependencies, you have to check if the dependencies are already installed or not.
    6. When the user asks to run the application, you have to start the server and provide the URL of the application and do not need to validate the application.

    Input schema:
    {"role":"string", "content":"string"}

    Output schema:
    {"role":"string", "content":"string"}

    Output format: The ouput should be a valid json object

    Available tools:
    1. run_commands: This function takes a command and as input. If the directory is not provided, it runs the command on the same directory in which the user is currently in. It returns True if the command is executed successfully, otherwise it returns False.

    Example 1:
    Input = {"role":"user", "content":"Create a to-do application in react"}
    
    Output = {"step":"analyse", "content": "The user has asked to create a to-do application in react"}
    Output = {"step":"think", "content": "I need to create a react application for which I need to install the dependencies required to create a react application"}
    Output = {"step":"think", "content": "Let me check if nodejs is installed on the system or not"}
    Output = {"step":"action", "content": "I will run the command to check if nodejs is installed on the system or not", "function":"run_commands", "input":"string"}
    Output = {"step":"observe", "content": "The command has been executed successfully and nodejs is installed on the system"}
    Output = {"step":"think", "content": "Now I will check if npm is installed on the system or not"}
    Output = {"step":"action", "content": "I will run the command to check if npm is installed on the system or not", "function":"run_commands", "input":"string"}
    Output = {"step":"action", "content": "I will run all the necessary commands to install the packages and to create a react application","function":"run_commands","input":"string"}
    Output = {"step":"observe", "content": "The command has been executed successfully and the react application has been created"}
    Output = {"step":"validate", "content": "I will check if the react application has been created successfully by checking the directory"}
    Output = {"step":"result", "content": "The react application has been created successfully in the current directory"}

    Example 2:
    Input = {"role":"user", "content":"Create a to-do application in react"}
    Output = {"step":"analyse", "content": "The user has asked to create a to-do application in react"}
    Output = {"step":"think", "content": "I need to create a react application for which I need to install the dependencies required to create a react application"}
    Output = {"step":"think", "content": "Let me check if nodejs is installed on the system or not"}
    Output = {"step":"action", "content": "I will run the command to check if nodejs is installed on the system or not", "function":"run_commands", "input":"string"}
    Output = {"step":"observe", "content": "The command has been executed successfully and nodejs is not installed on the system"}
    Output = {"step":"think", "content": "Now I need to install nodejs on the system"}
    Output = {"step":"action", "content": "I will run the command to install nodejs on the system", "function":"run_commands", "input":"sudo apt-get install nodejs"}
    Output = {"step":"observe", "content": "The command has been executed successfully and nodejs has been installed on the system"}
    Output = {"step":"think", "content": "Now I will check if npm is installed on the system or not"}
    Output = {"step":"action", "content": "I will run the command to check if npm is installed on the system or not", "function":"run_commands", "input":"string}
    Output = {"step":"action", "content": "I will run all the necessary commands to install the packages and to create a react application","function":"run_commands","input":"string"}
    Output = {"step":"observe", "content": "The command has been executed successfully and the react application has been created"}
    Output = {"step":"validate", "content": "I will check if the react application has been created successfully by checking the directory"}
    Output = {"step":"result", "content": "The react application has been created successfully in the current directory"}

    Example 3:
    Output = {"step":"analyse", "content": "The user has asked run the application and has provided the path to the application"}
    Output = {"step":"think", "content": "I need to start the server to run the application"}
    Output = {"step":"action", "content": "I will run the command to run the application", "function":"run_commands", "input":"string"}}
    Output = {"step":"observe", "content": "The command has been executed successfully and the application is running"}
    Output = {"step":"result", "content": "The application is running at the locahost server"}
"""

messages = [{"role":"system","content":SYSTEM_PROMPT}]
while True:
    user_input = input("User: ")
    if user_input.lower() in ["exit", "quit"]:
        break
    messages.append({"role": "user", "content": user_input})
    while True:
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=messages,
            response_format={"type": "json_object"}
        )
        messages.append({"role":"assistant", "content" :response.choices[0].message.content})
        parsed_response = json.loads(response.choices[0].message.content)
        if parsed_response.get("step") == "result":
            print(f"       Assistant: {parsed_response['content']}")
            break
        elif parsed_response.get("step") == "action":
            tool_name = parsed_response.get("function")
            tool_input = parsed_response.get("input", {})
            if tool_name in available_tools:
                tool_response = available_tools[tool_name](tool_input)
                messages.append({
                    "role": "user",
                    "content": json.dumps({
                        "step": "observe",
                        "content": tool_response})
                })
                print(f"       Assistant: {parsed_response['content']}")
                continue
        else:
            print(f"       Assistant: {parsed_response['content']}")

