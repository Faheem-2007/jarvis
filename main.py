import subprocess
import ollama
import json
import os
import datetime

# ============================================================
# TOOL FUNCTIONS
# ============================================================

# --- SYSTEM INFO ---

def get_time() -> str:
    return datetime.datetime.now().strftime("%A, %d %B %Y — %I:%M %p")

def get_battery() -> str:
    result = subprocess.run("pmset -g batt", shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def get_wifi() -> str:
    ssid = subprocess.run(
        "networksetup -getairportnetwork en0",
        shell=True, capture_output=True, text=True
    ).stdout.strip()
    ip = subprocess.run(
        "ipconfig getifaddr en0",
        shell=True, capture_output=True, text=True
    ).stdout.strip()
    return f"{ssid} | IP: {ip}"

def get_disk_space() -> str:
    result = subprocess.run("df -h /", shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def get_ram_usage() -> str:
    result = subprocess.run(
        "memory_pressure | head -1",
        shell=True, capture_output=True, text=True
    )
    return result.stdout.strip()

def get_cpu_usage() -> str:
    result = subprocess.run(
        "top -l 1 | grep 'CPU usage'",
        shell=True, capture_output=True, text=True
    )
    return result.stdout.strip()

def get_uptime() -> str:
    result = subprocess.run("uptime", shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def get_active_app() -> str:
    script = 'tell application "System Events" to get name of first application process whose frontmost is true'
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    return result.stdout.strip()

def get_volume() -> str:
    script = "output volume of (get volume settings)"
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    return f"Volume: {result.stdout.strip()}%"

def set_volume(level: str) -> str:
    script = f"set volume output volume {level}"
    subprocess.run(["osascript", "-e", script])
    return f"Volume set to {level}%"

def get_brightness() -> str:
    result = subprocess.run(
        "brightness -l 2>/dev/null || echo 'install: brew install brightness'",
        shell=True, capture_output=True, text=True
    )
    return result.stdout.strip()

def set_brightness(level: str) -> str:
    result = subprocess.run(f"brightness {level}", shell=True, capture_output=True, text=True)
    return result.stdout.strip() or f"Brightness set to {level}"

# --- CONTROL ---

def open_app(app_name: str) -> str:
    result = subprocess.run(f"open -a '{app_name}'", shell=True, capture_output=True, text=True)
    return result.stderr.strip() or f"Opened {app_name}"

def quit_app(app_name: str) -> str:
    script = f'tell application "{app_name}" to quit'
    subprocess.run(["osascript", "-e", script])
    return f"Quit {app_name}"

def take_screenshot(path: str = "~/Desktop/screenshot.png") -> str:
    subprocess.run(f"screencapture {os.path.expanduser(path)}", shell=True)
    return f"Screenshot saved to {path}"

def lock_screen() -> str:
    subprocess.run(
        'osascript -e \'tell application "System Events" to keystroke "q" using {command down, control down}\'',
        shell=True
    )
    return "Screen locked"

def sleep_mac() -> str:
    subprocess.run("pmset sleepnow", shell=True)
    return "Going to sleep"

def empty_trash() -> str:
    script = 'tell application "Finder" to empty trash'
    subprocess.run(["osascript", "-e", script])
    return "Trash emptied"

def type_text(text: str) -> str:
    script = f'tell application "System Events" to keystroke "{text}"'
    subprocess.run(["osascript", "-e", script])
    return f"Typed: {text}"

def mute() -> str:
    subprocess.run(["osascript", "-e", "set volume with output muted"])
    return "Muted"

def unmute() -> str:
    subprocess.run(["osascript", "-e", "set volume without output muted"])
    return "Unmuted"

# --- CLIPBOARD ---

def read_clipboard() -> str:
    result = subprocess.run("pbpaste", shell=True, capture_output=True, text=True)
    return result.stdout.strip() or "Clipboard is empty"

def write_clipboard(text: str) -> str:
    subprocess.run(f"echo '{text}' | pbcopy", shell=True)
    return f"Copied to clipboard"

# --- FILES ---

def run_command(cmd: str) -> str:
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout or result.stderr

def read_file(path: str) -> str:
    try:
        with open(os.path.expanduser(path), 'r') as f:
            return f.read()
    except Exception as e:
        return str(e)

def write_file(path: str, content: str) -> str:
    try:
        with open(os.path.expanduser(path), 'w') as f:
            f.write(content)
        return f"Written to {path}"
    except Exception as e:
        return str(e)

def list_directory(path: str = ".") -> str:
    result = subprocess.run(f"ls -la {os.path.expanduser(path)}", shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def create_folder(path: str) -> str:
    result = subprocess.run(f"mkdir -p {os.path.expanduser(path)}", shell=True, capture_output=True, text=True)
    return result.stderr or f"Folder created: {path}"

def move_file(src: str, dst: str) -> str:
    result = subprocess.run(
        f"mv {os.path.expanduser(src)} {os.path.expanduser(dst)}",
        shell=True, capture_output=True, text=True
    )
    return result.stderr or f"Moved {src} to {dst}"

def delete_file(path: str) -> str:
    result = subprocess.run(f"rm -rf {os.path.expanduser(path)}", shell=True, capture_output=True, text=True)
    return result.stderr or f"Deleted {path}"

def get_file_info(path: str) -> str:
    result = subprocess.run(f"stat {os.path.expanduser(path)}", shell=True, capture_output=True, text=True)
    return result.stdout.strip()

# --- BROWSER ---

def open_url(url: str) -> str:
    subprocess.run(f"open '{url}'", shell=True)
    return f"Opened {url}"

def get_current_tab() -> str:
    script = '''
    tell application "Google Chrome"
        get URL of active tab of front window
    end tell
    '''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    return result.stdout.strip() or "Could not get tab (is Chrome open?)"

# --- NOTIFICATIONS ---

def send_notification(title: str, message: str) -> str:
    script = f'display notification "{message}" with title "{title}"'
    subprocess.run(["osascript", "-e", script])
    return f"Notification sent"

# --- CALENDAR ---

def get_calendar_events() -> str:
    script = '''
    tell application "Calendar"
        set today to current date
        set tomorrow to today + 1 * days
        set eventList to ""
        repeat with c in calendars
            repeat with e in (every event of c whose start date >= today and start date < tomorrow)
                set eventList to eventList & summary of e & " at " & (start date of e as string) & "\n"
            end repeat
        end repeat
        return eventList
    end tell
    '''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    return result.stdout.strip() or "No events today"

# --- REMINDERS ---

def add_reminder(text: str) -> str:
    script = f'''
    tell application "Reminders"
        make new reminder with properties {{name:"{text}"}}
    end tell
    '''
    subprocess.run(["osascript", "-e", script])
    return f"Reminder added: {text}"

# --- MUSIC ---

def music_play_pause() -> str:
    script = 'tell application "Spotify" to playpause'
    subprocess.run(["osascript", "-e", script])
    return "Play/pause toggled"

def music_next() -> str:
    script = 'tell application "Spotify" to next track'
    subprocess.run(["osascript", "-e", script])
    return "Next track"

def music_previous() -> str:
    script = 'tell application "Spotify" to previous track'
    subprocess.run(["osascript", "-e", script])
    return "Previous track"

def get_current_song() -> str:
    script = '''
    tell application "Spotify"
        set trackName to name of current track
        set artistName to artist of current track
        return trackName & " by " & artistName
    end tell
    '''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    return result.stdout.strip() or "Spotify not running"

# --- MESSAGES ---

def send_imessage(phone: str, message: str) -> str:
    script = f'''
    tell application "Messages"
        set targetBuddy to "{phone}"
        set targetService to id of 1st account whose service type = iMessage
        send "{message}" to buddy targetBuddy of account id targetService
    end tell
    '''
    subprocess.run(["osascript", "-e", script])
    return f"iMessage sent to {phone}"

# --- WEATHER ---

def get_weather(city: str = "Chennai") -> str:
    result = subprocess.run(
        f"curl -s 'wttr.in/{city}?format=3'",
        shell=True, capture_output=True, text=True
    )
    return result.stdout.strip()

# ============================================================
# TOOL REGISTRY
# ============================================================

TOOLS = {
    "get_time":            lambda _: get_time(),
    "get_battery":         lambda _: get_battery(),
    "get_wifi":            lambda _: get_wifi(),
    "get_disk_space":      lambda _: get_disk_space(),
    "get_ram_usage":       lambda _: get_ram_usage(),
    "get_cpu_usage":       lambda _: get_cpu_usage(),
    "get_uptime":          lambda _: get_uptime(),
    "get_active_app":      lambda _: get_active_app(),
    "get_volume":          lambda _: get_volume(),
    "set_volume":          set_volume,
    "get_brightness":      lambda _: get_brightness(),
    "set_brightness":      set_brightness,
    "open_app":            open_app,
    "quit_app":            quit_app,
    "take_screenshot":     lambda p: take_screenshot(p if p else "~/Desktop/screenshot.png"),
    "lock_screen":         lambda _: lock_screen(),
    "sleep_mac":           lambda _: sleep_mac(),
    "empty_trash":         lambda _: empty_trash(),
    "type_text":           type_text,
    "mute":                lambda _: mute(),
    "unmute":              lambda _: unmute(),
    "read_clipboard":      lambda _: read_clipboard(),
    "write_clipboard":     write_clipboard,
    "run_command":         run_command,
    "read_file":           read_file,
    "write_file":          None,   # two args
    "list_directory":      lambda p: list_directory(p if p else "."),
    "create_folder":       create_folder,
    "move_file":           None,   # two args
    "delete_file":         delete_file,
    "get_file_info":       get_file_info,
    "open_url":            open_url,
    "get_current_tab":     lambda _: get_current_tab(),
    "send_notification":   None,   # two args
    "get_calendar_events": lambda _: get_calendar_events(),
    "add_reminder":        add_reminder,
    "music_play_pause":    lambda _: music_play_pause(),
    "music_next":          lambda _: music_next(),
    "music_previous":      lambda _: music_previous(),
    "get_current_song":    lambda _: get_current_song(),
    "send_imessage":       None,   # two args
    "get_weather":         lambda c: get_weather(c if c else "Chennai"),
}

TOOLS_LIST = "\n".join([f"- {name}" for name in TOOLS.keys()])

# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = f"""You are Jarvis, a personal AI assistant that controls a Mac.

You have access to these tools:
{TOOLS_LIST}

When you need to use a tool, respond EXACTLY like this:
TOOL: tool_name
INPUT: the input to the tool

For tools that need two inputs (write_file, move_file, send_notification, send_imessage), separate with a comma:
TOOL: write_file
INPUT: ~/Desktop/note.txt, hello world

TOOL: send_notification
INPUT: Reminder, Time to study

TOOL: send_imessage
INPUT: +91XXXXXXXXXX, hey whats up

TOOL: move_file
INPUT: ~/Downloads/file.txt, ~/Documents/file.txt

When you have a final answer, respond like this:
ANSWER: your response

Never mix formats. Only one action per response."""

# ============================================================
# MEMORY
# ============================================================

MEMORY_FILE = "memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            print("[Memory loaded]\n")
            return json.load(f)
    return [{"role": "system", "content": SYSTEM_PROMPT}]

def save_memory(messages):
    with open(MEMORY_FILE, 'w') as f:
        json.dump(messages, f, indent=2)

# ============================================================
# PARSE RESPONSE
# ============================================================

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
                if isinstance(parsed, dict):
                    for key in ["cmd", "text", "app", "city", "level", "path"]:
                        if key in parsed:
                            input_val = parsed[key]
                            break
                    if "path" in parsed and "content" in parsed:
                        input_val = f"{parsed['path']}, {parsed['content']}"
            except (json.JSONDecodeError, TypeError):
                pass
            return ("tool", tool_name, input_val)

        if line.startswith("ANSWER:"):
            return ("answer", line.replace("ANSWER:", "").strip())

    return ("answer", text.strip())

# ============================================================
# RUN TOOL
# ============================================================

def run_tool(name: str, input_val: str) -> str:
    # two-argument tools
    two_arg = {
        "write_file": write_file,
        "move_file": move_file,
        "send_notification": send_notification,
        "send_imessage": send_imessage,
    }
    if name in two_arg:
        parts = input_val.split(',', 1)
        if len(parts) == 2:
            return two_arg[name](parts[0].strip(), parts[1].strip())
        return f"Error: {name} needs two inputs separated by comma"

    if name in TOOLS and TOOLS[name] is not None:
        try:
            return TOOLS[name](input_val)
        except Exception as e:
            return f"Error running {name}: {str(e)}"

    return f"Unknown tool: {name}"

# ============================================================
# CHAT
# ============================================================

def chat(messages):
    response = ollama.chat(
        model="qwen2.5-coder:7b",
        messages=messages
    )
    return response['message']['content']

# ============================================================
# MAIN LOOP
# ============================================================

print("Jarvis online.")
print("'/clear' wipe memory | '/tools' list tools | '/memory' memory size | 'exit' quit\n")

messages = load_memory()

if not messages or messages[0].get("role") != "system":
    messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})
else:
    messages[0]["content"] = SYSTEM_PROMPT

while True:
    user_input = input("You: ").strip()

    if not user_input:
        continue

    if user_input.lower() == "exit":
        save_memory(messages)
        print("Memory saved. Bye.")
        break

    if user_input.lower() == "/clear":
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        save_memory(messages)
        print("[Memory cleared]\n")
        continue

    if user_input.lower() == "/tools":
        print(f"\nAvailable tools:\n{TOOLS_LIST}\n")
        continue

    if user_input.lower() == "/memory":
        print(f"\n[{len(messages) - 1} messages in memory]\n")
        continue

    messages.append({"role": "user", "content": user_input})

    for _ in range(5):
        response_text = chat(messages)
        print(f"\n[Jarvis thinking]: {response_text}\n")

        result = parse_response(response_text)

        if result[0] == "answer":
            print(f"Jarvis: {result[1]}\n")
            messages.append({"role": "assistant", "content": result[1]})
            save_memory(messages)
            break

        elif result[0] == "tool":
            tool_output = run_tool(result[1], result[2])
            print(f"[Tool: {result[1]}] → {tool_output}\n")
            messages.append({"role": "assistant", "content": response_text})
            messages.append({"role": "user", "content": f"Tool result: {tool_output}"})