from langchain.tools import tool
from langchain_ollama import ChatOllama
from langchain_huggingface import ChatHuggingFace
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, BitsAndBytesConfig
from tools import *
from langchain_community.llms import HuggingFacePipeline
import torch
import json
import os

MEMORY_FILE = "memory.json"
MAX_CONVERSATION_HISTORY = 10  

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

tools = [get_weather_from_coordinates, get_user_location, get_time_for_timezone, 
         get_github_repo_info, update_memory, web_search]
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4"
)
model_name = "Qwen/Qwen2.5-7B-Instruct"  # or "microsoft/Phi-3.5-mini-instruct" for smaller

tokenizer = AutoTokenizer.from_pretrained(model_name)
model_llm = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=quantization_config,
    device_map="auto",
    torch_dtype=torch.float16
)
pipe = pipeline(
    "text-generation",
    model=model_llm,
    tokenizer=tokenizer,
    max_new_tokens=512,
    temperature=0.1,
    do_sample=False,
    return_full_text=False
)
hf_llm = HuggingFacePipeline(pipeline=pipe)

# Create Chat Model
chat_model = ChatHuggingFace(llm=hf_llm)

# Bind tools
model = chat_model.bind_tools(tools)
def format_memory():
    return json.dumps(memory, indent=2)

SystemPrompt = """You are Qwen, a highly capable AI assistant with access to tools.

## IDENTITY
You are precise, helpful, and honest. You never invent information when tools are available.

## CORE RULES
1. NEVER guess information that tools can provide
2. ALWAYS use tools for real-time/ external data
3. If unsure, use tools or ask the user
4. Be concise but complete in responses

## TOOL USAGE PROTOCOL
When you need information:
- STEP 1: Check if a tool exists for it
- STEP 2: If yes, CALL IT IMMEDIATELY
- STEP 3: Use the tool result verbatim
- STEP 4: Never paraphrase tool data if it changes meaning

Available tools:
- Weather: Use coordinates from location tool
- Location: Get user's current location
- Time: Get time for any timezone
- GitHub: Get repository information
- Memory: Store user information permanently
- Web Search: Get current/online information

## MEMORY SYSTEM
You HAVE TO store important information using update_memory:

STORE when user shares:
- Their name → "user_profile" section, "name" key
- Their GitHub username → "user_profile" section, "github_username" key
- Preferences → "preferences" section, descriptive key
- Reusable facts → "other" section, descriptive key

RULES:
- Store immediately when information is revealed
- Use exact section names: "user_profile", "preferences", "other"
- Create meaningful keys (e.g., "favorite_cuisine" not "pref1")
- NEVER mention that you're storing something

## RESPONSE FORMAT
1. For questions requiring tools:
   - Identify needed tool
   - Call it with correct parameters
   - Use the exact result in response

2. For factual questions:
   - Use web_search if current info needed
   - Use memory if personal info needed

3. For unclear requests:
   - Ask ONE clarifying question
   - Suggest what tool might help

## CONVERSATION FLOW
- Keep responses focused
- Don't repeat information
- Don't explain your reasoning unless asked
- Don't mention tool calls in response

## LOCATION HANDLING
When user mentions:
- "my location" → Call get_user_location
- "near me" → Call get_user_location
- "here" → Call get_user_location
- Then use coordinates for weather/time

## ERROR HANDLING
If tool fails:
- Report the issue clearly
- Suggest alternatives if possible
- Never make up data to compensate

## SAFETY
- Refuse harmful requests politely
- Explain why you can't comply
- Offer alternatives when possible

## EXAMPLES OF GOOD BEHAVIOR

User: "What's the weather like here?"
Good: [Calls get_user_location → gets coordinates → calls get_weather → returns actual weather]
Bad: "I need your location first" (without using tool)

User: "My name is John"
Good: [Silently stores in memory] "Nice to meet you, John! How can I help?"
Bad: "I'll remember that your name is John" (mentions memory)

User: "What's new with GPT-5?"
Good: [Calls web_search] "Based on recent information: [factual summary]"
Bad: "GPT-5 hasn't been released yet" (without checking)

## REMEMBER
- Tools exist for a reason → USE THEM
- Your knowledge cutoff is your training data
- Anything current needs web_search
- Personal info needs memory storage
- Never apologize for using tools
- Never explain your process unless asked
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