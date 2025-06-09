from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import json
import os,subprocess
import webbrowser
import requests
load_dotenv()

client = OpenAI()

def open_in_browser(file_path: str):
    try:
        abs_path = os.path.abspath(file_path)
        if not os.path.exists(abs_path):
            return f"File '{file_path}' does not exist."
        webbrowser.open(f"file://{abs_path}")
        return f"Opened '{file_path}' in your default browser."
    except Exception as e:
        return f"Failed to open browser: {str(e)}"


def get_weather(city :str):
    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)
    if response.status_code == 200:
        return f"The weather in {city} is {response.text}."
    
    return "Something went wrong"

current_dir = os.getcwd()  # Default to current directory

def run_command(cmd: str, cwd: str = None):
    try:
        result = subprocess.check_output(
            cmd, shell=True, stderr=subprocess.STDOUT, text=True, cwd=cwd
        )
        return result.strip()
    except subprocess.CalledProcessError as e:
        return f"Command failed: {e.output.strip()}"
    
def write_file(file_path: str, content: str):
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"File '{file_path}' written successfully."
    except Exception as e:
        return f"Failed to write to file '{file_path}': {str(e)}"
    
def make_directory(path: str):
    try:
        os.makedirs(path, exist_ok=True)
        return f"Directory '{path}' created or already exists."
    except Exception as e:
        return f"Failed to create directory '{path}': {str(e)}"


def read_file(file_path: str):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Failed to read file '{file_path}': {str(e)}"


SYSTEM_PROMPT ="""
    You are a AI agent helping in solving user query
    you work on start,plan,action,observe mode,
    
    based on the user query and avaiabale tools, plan the step by step execution based on planning,select the relevant tools from available tools and based on the tool selected you perform an action on the tool
    
    wait for the observation and based on observation from tool resolve the query
    
    do not write code in terminal at any cost do it in the file instead
    
    Rules:
    -Follow the Output JSON format
    NEVER return code inside the 'content' field. All code must be written to a file using the write_file tool only. 
    Look at available tools before each step
    Never include HTML, CSS, or JS code directly in messages. Only describe the action, then perform it via tools.
    always perform one step at a time and wait for it complete 
    carefully analyse the user query
    
   Available tools:
    "get_weather": "Takes a city name and returns the current weather."
    "run_command": "Takes a shell command string, executes it, and returns the result."
    "write_file": "Takes 'file_path' and 'content', writes content to the file."
    "read_file": "Takes a file path and returns the content of the file."
    "make_directory": "Takes a directory path and creates it if it doesn't exist."
    
    Example:
    User: What is weather in newyork
    output:{{"step":"plan","content":"the user is interseted in weather of newyork}}
    output:{{"step":"plan","content":"from available tools i should call get weather"}}
    output:{{"step":"action","function":"get_weather","input":"New york"}}
    output:{{"step":"observer","output":"42 c"}}
    output:{{"step":"output","content":"weather in newyork is 42 c}}
    
    {"step": "plan", "content": "The user wants to open index.html in browser."}
    {"step": "action", "function": "open_in_browser", "input": "index.html"}
    
    Example:
    {"step": "plan", "content": "We will create 3 files: index.html, style.css, script.js"}
    {"step": "action", "function": "write_file", "input": {"file_path": "index.html", "content": "<!DOCTYPE html>..."}}
    {"step": "observe", "output": "File 'index.html' written successfully."}
    {"step": "action", "function": "write_file", "input": {"file_path": "style.css", "content": "body { ... }"}}
    {"step": "observe", "output": "File 'style.css' written successfully."}
    {"step": "action", "function": "write_file", "input": {"file_path": "script.js", "content": "document.addEventListener(..."}}
    {"step": "observe", "output": "File 'script.js' written successfully."}
    {"step": "action", "function": "open_in_browser", "input": "index.html"}
    {"step": "observe", "output": "Opened 'index.html' in your default browser."}
    {"step": "output", "content": "Your landing page is ready. Preview opened in browser."}

    
    
    
    """
        
    
available_tools = {
    "get_weather": get_weather,
    "run_command": run_command,
    "write_file": write_file,
    "read_file": read_file,
    "open_in_browser": open_in_browser,
    "make_directory": make_directory
}

    
messages=[]
messages.append(
        {"role":"system","content":SYSTEM_PROMPT},
    )


while True:
    query = input("> ")
    messages.append({"role": "user", "content": query})

    while True:
        response = client.chat.completions.create(
            model="chatgpt-4o-latest",
            response_format={"type": "json_object"},
            messages=messages
        )

        assistant_message = response.choices[0].message.content
        messages.append({"role": "assistant", "content": assistant_message})

        parsed_response = json.loads(assistant_message)
        step = parsed_response.get("step")
        content = parsed_response.get("content")

        if step == "plan":
            print(f"🧠 Plan: {content}")
            continue

        if step == "action":
            tool_name = parsed_response.get("function")
            tool_input = parsed_response.get("input")

            if tool_name not in available_tools:
                print(f"⚠️ Unknown tool: {tool_name}")
                break

            tool = available_tools[tool_name]

            try:
                if isinstance(tool_input, dict):
                    result = tool(**tool_input)
                else:
                    result = tool(tool_input)
            except Exception as e:
                result = f"Tool execution error: {e}"

            messages.append({
                "role": "user",
                "content": json.dumps({
                    "step": "observe",
                    "output": result
                })
            })

            # Log tool usage cleanly
            if isinstance(tool_input, dict):
                input_summary = ", ".join(
                    f"{k}: {('[content omitted]' if k == 'content' else str(v))}"
                    for k, v in tool_input.items()
                )
                print(f"🔧 Tool '{tool_name}' called with: {input_summary}")
            elif isinstance(tool_input, str):
                short_input = tool_input if len(tool_input) <= 50 else "[input too long, omitted]"
                print(f"🔧 Tool '{tool_name}' called with input: {short_input}")
            else:
                print(f"🔧 Tool '{tool_name}' called.")

            continue

        if step == "output":
            print(f"🤖: {content}")
            break
