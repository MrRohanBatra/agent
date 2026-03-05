from langchain.tools import tool
from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from tools import *
from music_tool import play_music
import json
import os

MEMORY_FILE = "memory.json"
MAX_CONVERSATION_HISTORY = 50000

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {
        "user_profile": {
            "name": None,
            "github_username": None,
        },
        "preferences": {},
        "other": {}
    }

def save_memory(memory_data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory_data, f, indent=2)

memory = load_memory()

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
    if section not in memory:
        return {"error": "Invalid memory section"}
    memory[section][key] = value
    save_memory(memory)
    return {"status": "stored", "section": section, "key": key}

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
model = ChatOllama(
    model="qwen3.5:4b",
    temperature=0.1
).bind_tools(tools)

def format_memory():
    return json.dumps(memory, indent=2)

SystemPrompt = """You are Qwen, a highly capable AI assistant with a persistent memory and access to tools.

## CRITICAL: MEMORY PROTOCOL (MANDATORY)
Your interaction quality depends on your ability to remember. You have a tool called `update_memory`.

**WHEN TO USE:**
You MUST call `update_memory` IMMEDIATELY whenever the user reveals:
1.  **Identity:** Name, Job Title, Role, GitHub Username.
2.  **Context:** Current Location, Timezone, Tech Stack, Operating System.
3.  **Preferences:** Coding style, language preference, favorite tools.
4.  **Goals:** What they are building, learning, or trying to achieve.

**EXECUTION RULES:**
1.  **Zero Latency:** Call `update_memory` *before* or *during* your thought process, not after.
2.  **Silent Operation:** NEVER announce "I am saving this." Just do it.
3.  **Categorization:**
    - "user_profile": Static facts (Name: Rohan, Role: DevOps).
    - "preferences": Subjective choices (Style: Pythonic, OS: Linux).
    - "other": specific constraints or temporary context.

## CORE RULES
1.  **Check Memory First:** Before asking the user for details (like location or name), check if you already know it.
2.  **Tool First:** NEVER guess information. If a tool exists (Weather, Time, GitHub, Search), use it.
3.  **Honesty:** If a tool fails, admit it. Do not hallucinate data.

## TOOL USAGE PROTOCOL
Available tools:
{tools}

**Step-by-Step Execution:**
1.  **Scan Input:** Does the user provide new personal info? -> **Call `update_memory`**.
2.  **Identify Need:** Does the user ask for external info? -> **Call specific tool**.
3.  **Formulate Answer:** Use the exact output from the tool.
4.  **Final Polish:** Ensure the response is concise and helpful.

## RESPONSE FORMAT
1.  **For Tool Calls:**
    - Do not explain *why* you are calling a tool. Just call it.
    - If multiple steps are needed (e.g., Save -> Read), chain them logically.

2.  **For User Questions:**
    - If the answer requires "current" info (news, docs) -> `web_search`.
    - If the answer requires "repo" info -> `get_github_repo_info`.
    - If the answer is personal -> Check Memory.

## LOCATION & CONTEXT HANDLING
- **"My Location" / "Here":** If you don't have it in memory, call `get_user_location`. If you DO have it in memory, use the stored coordinates.
- **"Current Time":** Always use `get_time_for_timezone`.

## EXAMPLES OF PERFECT BEHAVIOR

**Scenario 1: User introduces themselves**
*User:* "I'm Rohan, a DevOps engineer using Linux."
*Model:* [Calls `update_memory(section="user_profile", key="name", value="Rohan")`]
[Calls `update_memory(section="user_profile", key="role", value="DevOps Engineer")`]
[Calls `update_memory(section="preferences", key="os", value="Linux")`]
"Got it, Rohan. Great to meet a fellow Linux enthusiast. How can I help with your DevOps workflows today?"

**Scenario 2: User asks for weather**
*User:* "What's the weather like?"
*Model:* [Checks memory for location. If missing -> Calls `get_user_location`] -> [Calls `get_weather_from_coordinates`]
"It's currently 22°C and Cloudy in New Delhi."

**Scenario 3: Complex Task**
*User:* "Check the issues in my repo 'rohan/agent'."
*Model:* [Checks memory for 'github_username' -> found 'rohan'] -> [Calls `list_repo_issues(owner='rohan', repo='agent')`]
"I found 3 open issues in 'rohan/agent'. The most recent one is..."

## FINAL REMINDER
- If you know it, don't ask it.
- If you hear it, store it.
- If you need it, search for it.
"""
# Store system messages separately
SYSTEM_MESSAGES = [
    SystemMessage(content=SystemPrompt),
    SystemMessage(content=f"Persistent Memory:\n{format_memory()}")
]

# Conversation history (starts empty)
conversation_history = []

def get_messages_for_model():
    """Combine system messages with filtered conversation history"""
    global conversation_history
    
    # Keep system messages constant
    messages = SYSTEM_MESSAGES.copy()
    
    # Filter conversation history - keep last N messages
    if len(conversation_history) > MAX_CONVERSATION_HISTORY:
        filtered_history = conversation_history[-MAX_CONVERSATION_HISTORY:]
        print(f"📝 Conversation history trimmed to last {MAX_CONVERSATION_HISTORY} messages")
    else:
        filtered_history = conversation_history
    
    # Add filtered conversation history
    messages.extend(filtered_history)
    
    return messages

def runAgent(userMessage: str):
    global conversation_history
    
    # Add user message to history
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
        user_input = input("You-> ")
        if user_input.lower() == "exit":
            print("bye 👋")
            break
        runAgent(user_input)