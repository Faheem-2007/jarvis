import subprocess
import ollama
import json
import os

# --- TOOL FUNCTIONS ---

def run_command(cmd: str) -> str:
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout or result.stderr

def read_file(path: str) -> str:
    try:
        with open(path, 'r') as f:
            return f.read()
    except Exception as e:
        return str(e)

def write_file(path: str, content: str) -> str:
    try:
        with open(path, 'w') as f:
            f.write(content)
        return f"Written to {path}"
    except Exception as e:
        return str(e)

# --- MEMORY ---
# saves and loads conversation history to disk
# so jarvis remembers across restarts

MEMORY_FILE = "memory.json"

def load_memory():
    # if memory file exists, load it — otherwise start fresh
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            print("[Memory loaded]\n")
            return json.load(f)
    return [{"role": "system", "content": SYSTEM_PROMPT}]

def save_memory(messages):
    # write full conversation history to disk after every turn
    with open(MEMORY_FILE, 'w') as f:
        json.dump(messages, f, indent=2)

# --- SYSTEM PROMPT ---

SYSTEM_PROMPT = """You are Jarvis, a personal AI assistant that controls a Mac.

You have access to these tools:
- run_command(cmd): runs a shell command on the Mac
- read_file(path): reads a file
- write_file(path, content): writes content to a file

When you need to use a tool, respond EXACTLY like this:
TOOL: tool_name
INPUT: the input to the tool

When you have a final answer, respond like this:
ANSWER: your response

Never mix formats. Only one action per response."""

# --- PARSE RESPONSE ---

def parse_response(text: str):
    lines = text.strip().split('\n')
    for i, line in enumerate(lines):
        if line.startswith("TOOL:"):
            tool_name = line.replace("TOOL:", "").strip()
            input_val = ""
            for j in range(i+1, len(lines)):
                if lines[j].startswith("INPUT:"):
                    input_val = lines[j].replace("INPUT:", "").strip()
                    break
            try:
                parsed = json.loads(input_val)
                if tool_name == "write_file" and "path" in parsed and "content" in parsed:
                    input_val = f"{parsed['path']}, {parsed['content']}"
                elif "path" in parsed:
                    input_val = parsed["path"]
                elif "cmd" in parsed:
                    input_val = parsed["cmd"]
            except (json.JSONDecodeError, TypeError):
                pass
            return ("tool", tool_name, input_val)

        if line.startswith("ANSWER:"):
            return ("answer", line.replace("ANSWER:", "").strip())

    return ("answer", text.strip())

# --- RUN TOOL ---

def run_tool(name: str, input_val: str) -> str:
    if name == "run_command":
        return run_command(input_val)
    elif name == "read_file":
        return read_file(input_val)
    elif name == "write_file":
        parts = input_val.split(',', 1)
        if len(parts) == 2:
            return write_file(parts[0].strip(), parts[1].strip())
        return "Error: write_file needs path and content"
    return f"Unknown tool: {name}"

# --- CHAT ---

def chat(messages):
    response = ollama.chat(
        model="qwen2.5-coder:7b",
        messages=messages
    )
    return response['message']['content']

# --- MAIN LOOP ---

print("Jarvis online. Type 'exit' to quit. Type '/clear' to wipe memory.\n")

messages = load_memory()

# make sure system prompt is always first
# handles case where memory.json exists but system prompt changed
if not messages or messages[0].get("role") != "system":
    messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})

while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        save_memory(messages)          # save before quitting
        print("Memory saved. Bye.\n")
        break

    if user_input.lower() == "/clear":
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        save_memory(messages)
        print("[Memory cleared]\n")
        continue

    messages.append({"role": "user", "content": user_input})

    for _ in range(5):
        response_text = chat(messages)
        print(f"\n[Jarvis thinking]: {response_text}\n")

        result = parse_response(response_text)

        if result[0] == "answer":
            print(f"Jarvis: {result[1]}\n")
            messages.append({"role": "assistant", "content": result[1]})
            save_memory(messages)      # save after every completed turn
            break

        elif result[0] == "tool":
            tool_output = run_tool(result[1], result[2])
            print(f"[Tool: {result[1]}] → {tool_output}\n")
            messages.append({"role": "assistant", "content": response_text})
            messages.append({"role": "user", "content": f"Tool result: {tool_output}"})