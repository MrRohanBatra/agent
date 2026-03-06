
from pprint import pprint
from langchain.tools import tool
from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from tools import *
from music_tool import play_music
import json
import os

MEMORY_FILE = "memory_new.json"
MAX_CONVERSATION_HISTORY = 50
loggedInUser:str=None
memory:dict=None
conversation_history:list = []
def load_memory(username: str) -> dict:
    default_memory = {
        "user_profile": {"name": None, "github_username": None},
        "preferences": {},
        "other": {}
    }

    if not os.path.exists(MEMORY_FILE):
        return default_memory

    try:
        with open(MEMORY_FILE, "r") as f:
            data = json.load(f)
            return data.get("users", {}).get(username, default_memory)
    except json.JSONDecodeError:
        # print(f"Error: {MEMORY_FILE} is corrupted. Returning blank memory.")
        return default_memory

def save_memory(username: str, user_memory_data: dict):
    """Safely updates a specific user's memory without destroying the file structure."""
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                full_data = json.load(f)
        except json.JSONDecodeError:
            full_data = {"users": {}}
    else:
        full_data = {"users": {}}

    if "users" not in full_data or not isinstance(full_data["users"], dict):
        full_data["users"] = {}
    full_data["users"][username] = user_memory_data

    with open(MEMORY_FILE, "w") as f:
        json.dump(full_data, f, indent=2)

@tool
def update_memory(section: str, key: str, value: str) -> dict:
    """
    Store structured long-term memory.

    Sections:
    - user_profile
    - preferences
    - other

    Examples:
    - name -> user_profile.name
    - github_username -> user_profile.github_username

    Inputs:
        section (str): Memory section
        key (str): Key name
        value (str): Value to store

    Returns:
        dict: {"status": "stored", "section": section, "key": key}
    """
    global memory
    global loggedInUser
    
    if not loggedInUser:
        return {"error": "No user is currently logged in."}

    if section not in memory:
        return {"error": f"Invalid memory section: {section}"}
        
    # Update the global memory dictionary in RAM
    memory[section][key] = value
    
    # Save the updated memory to the JSON file safely
    save_memory(loggedInUser, memory)
    
    return {"status": "stored", "section": section, "key": key}

def format_memory():
    return json.dumps(memory, indent=2)

tools = [
    get_time_for_timezone,
    get_user_location,
    get_weather_from_coordinates,
    web_search,
    get_wikipedia_summary,
    convert_currency,
    calculate_expression,
    scrape_website_text,
    get_github_repo_info,
    get_github_file_content,
    search_code_in_repo,
    list_repo_issues,
    get_repo_file_structure,
    read_file,
    write_to_file,
    list_directory,
    update_memory,
    play_music
]

SystemPrompt = """[CRITICAL SYSTEM DIRECTIVE: MEMORY FIRST]
You are Qwen. Your PRIMARY and most important function is to remember user information using the `update_memory` tool. You must evaluate EVERY user message for new information before doing anything else.

## MANDATORY MEMORY PROTOCOL
You must call `update_memory` IMMEDIATELY if the user states ANY of the following:
- A fact about themselves (traits, ownership, background).
- A preference or dislike.
- An environmental detail (setup, hardware, current state).
- A goal or current task.

Do NOT wait for specific keywords. If it describes the user or their world, SAVE IT.

## CATEGORIZATION RULES
When saving, use these broad categories:
1. "user_profile": Any factual data about who the user is or what they do.
2. "preferences": Any subjective choices, likes, dislikes, or working styles.
3. "other": Temporary states, current tasks, or hardware/software environment.

## TOOL USAGE PROTOCOL
Available tools: {tools}

You must operate using this exact step-by-step internal logic for EVERY response:

STEP 1: [MEMORY CHECK] Read the user's prompt. Does it contain ANY new fact, preference, or context about the user? 
-> If YES: Call `update_memory` silently.
-> If NO: Proceed to Step 2.

STEP 2: [EXTERNAL CHECK] Does the user need information outside your internal knowledge (time, weather, search)?
-> If YES: Call the relevant tool.
-> If NO: Proceed to Step 3.

STEP 3: [RESPOND] Formulate your answer concisely based on tool outputs or memory. NEVER announce that you are saving information.

## CORE RULES
- NEVER ask the user for information you already have in memory. Check memory first.
- NEVER guess information. If a tool exists to find the answer, use it.
- NEVER explain your tool usage. Just output the response.

## EXAMPLES OF PERFECT BEHAVIOR

User: "I am trying to learn Rust today."
Model: [Calls `update_memory(section="context", key="current_goal", value="Learning Rust")`]
"Rust is a great choice! What specific concept are you starting with?"

User: "What's the weather like here?"
Model: [Checks memory for location -> Calls `get_weather_from_coordinates`]
"It is currently 22°C and clear."

User: "I hate using dark mode."
Model: [Calls `update_memory(section="preferences", key="ui_theme", value="Dislikes dark mode, prefers light mode")`]
"Noted! I'll keep things bright. What's next on your agenda?"

[FINAL CRITICAL DIRECTIVE]
Did the user just tell you something about themselves? If yes, you MUST call `update_memory` right now before replying.
"""
SYSTEM_MESSAGES = [
    SystemMessage(content=SystemPrompt),
    SystemMessage(content=f"Persistent Memory:\n{format_memory()}")
]


model = ChatOllama(
    model="qwen3.5:2b",
    temperature=0.1
).bind_tools(tools)


def get_messages_for_model():
    global conversation_history

    messages = [
        SystemMessage(content=SystemPrompt),
        SystemMessage(content=f"Persistent Memory:\n{json.dumps(memory)}")
    ]

    if len(conversation_history) > MAX_CONVERSATION_HISTORY:
        filtered_history = conversation_history[-MAX_CONVERSATION_HISTORY:]
    else:
        filtered_history = conversation_history

    messages.extend(filtered_history)
    return messages
def runAgent(userMessage: str):
    global conversation_history
    conversation_history.append(HumanMessage(content=userMessage))
    
    while True:
        # Get filtered messages for model
        messages_for_model = get_messages_for_model()
        
        # Invoke model
        response = model.invoke(messages_for_model)
        
        # If no tool calls → final answer
        if not response.tool_calls:
            print(response.content)
            # Add assistant response to history
            conversation_history.append(AIMessage(content=response.content))
            return response.content
        
        # Add assistant message with tool calls to history
        conversation_history.append(response)
        
        # Process tool calls
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_call_id = tool_call["id"]
            selected_tool = next(t for t in tools if t.name == tool_name)
            tool_result = selected_tool.invoke(tool_args)
            
            # Add tool result to history
            conversation_history.append(
                ToolMessage(
                    content=str(tool_result),
                    tool_call_id=tool_call_id
                )
            )

if __name__ == "__main__":
    print("🤖 Agent initialized. Type 'exit' to quit.")
    print(f"📊 Keeping last {MAX_CONVERSATION_HISTORY} messages in history")
    print("-" * 50)
    
    while True:
        if(loggedInUser is not None):
            user_input = input("You-> ")
            if user_input.lower() == "exit":
                print("bye 👋")
                break
            runAgent(user_input)
        else:
            loggedInUser=input("Enter Username ")
            memory=load_memory(loggedInUser)