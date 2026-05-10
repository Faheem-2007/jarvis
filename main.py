import subprocess
import ollama
import json
import os
import re
import sys
import datetime
import speech_recognition as sr

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

# --- CONTROLLED BROWSER ---

BROWSER_PROFILE_DIR = os.path.expanduser("~/jarvis/browser_profile")
browser_playwright = None
browser_context = None
browser_page = None

def _ensure_browser():
    """Start or return Jarvis's controlled Playwright browser page."""
    global browser_playwright, browser_context, browser_page

    if browser_page is not None and not browser_page.is_closed():
        return browser_page, ""

    try:
        from playwright.sync_api import sync_playwright
    except Exception as e:
        return None, f"Playwright is not installed in this Python env: {e}"

    try:
        os.makedirs(BROWSER_PROFILE_DIR, exist_ok=True)
        browser_playwright = sync_playwright().start()
        launch_options = {
            "headless": False,
            "accept_downloads": True,
        }
        channel = os.getenv("JARVIS_BROWSER_CHANNEL", "").strip()
        if channel:
            launch_options["channel"] = channel
        try:
            browser_context = browser_playwright.chromium.launch_persistent_context(
                BROWSER_PROFILE_DIR,
                **launch_options,
            )
        except Exception:
            launch_options.pop("channel", None)
            browser_context = browser_playwright.chromium.launch_persistent_context(
                BROWSER_PROFILE_DIR,
                **launch_options,
            )
        browser_page = browser_context.pages[0] if browser_context.pages else browser_context.new_page()
        return browser_page, ""
    except Exception as e:
        return None, f"Could not start controlled browser: {e}"

def _normalize_url(url: str) -> str:
    url = (url or "").strip()
    if not url:
        return "https://www.google.com"
    shortcuts = {
        "google": "https://www.google.com",
        "youtube": "https://www.youtube.com",
        "leetcode": "https://leetcode.com",
        "gmail": "https://mail.google.com",
    }
    lowered = url.lower()
    if lowered in shortcuts:
        return shortcuts[lowered]
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url):
        return f"https://{url}"
    return url

def browser_open(url: str) -> str:
    page, error = _ensure_browser()
    if error:
        return error
    target = _normalize_url(url)
    try:
        page.goto(target, wait_until="domcontentloaded", timeout=30000)
        page.bring_to_front()
        return f"Browser opened: {page.title()} | {page.url}"
    except Exception as e:
        return f"Browser open error: {e}"

def browser_read_page(_: str = "") -> str:
    page, error = _ensure_browser()
    if error:
        return error
    try:
        title = page.title()
        url = page.url
        text = page.locator("body").inner_text(timeout=8000)
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        if len(text) > 6000:
            text = text[:6000] + "\n...[truncated]"
        return f"Title: {title}\nURL: {url}\n\n{text}"
    except Exception as e:
        return f"Browser read error: {e}"

def browser_click(target: str) -> str:
    page, error = _ensure_browser()
    if error:
        return error
    target = (target or "").strip()
    if not target:
        return "Browser click error: provide visible text or a CSS selector"

    try:
        if target.startswith(("css=", "xpath=", "//", "#", ".", "[", "button", "input", "a[")):
            selector = target.replace("css=", "", 1)
            page.locator(selector).first.click(timeout=10000)
        elif target.lower() in {"first", "first result", "first video", "top result"}:
            if "youtube.com" in page.url:
                page.locator("ytd-video-renderer a#video-title, ytd-rich-item-renderer a#video-title-link").first.click(timeout=10000)
            else:
                page.locator("a:visible").first.click(timeout=10000)
        else:
            page.get_by_text(target, exact=False).first.click(timeout=10000)
    except Exception:
        try:
            page.locator(target).first.click(timeout=10000)
        except Exception as e:
            return f"Browser click error: {e}"

    try:
        page.wait_for_load_state("domcontentloaded", timeout=10000)
    except Exception:
        pass
    return f"Clicked: {target}"

def browser_type(selector: str, text: str) -> str:
    page, error = _ensure_browser()
    if error:
        return error
    selector = (selector or "").strip()
    text = text or ""

    try:
        if selector.lower() in {"", "active", "focused"}:
            page.keyboard.insert_text(text)
        elif selector.lower() in {"search", "search box", "youtube search"}:
            search = page.locator("input[name='search_query'], textarea[name='search_query'], input[type='search'], textarea, input[type='text']").first
            search.click(timeout=10000)
            search.fill(text)
        else:
            field = page.locator(selector).first
            field.click(timeout=10000)
            field.fill(text)
    except Exception as e:
        return f"Browser type error: {e}"
    return f"Typed into {selector or 'active element'}"

def browser_press(key: str) -> str:
    page, error = _ensure_browser()
    if error:
        return error
    key = (key or "Enter").strip()
    try:
        page.keyboard.press(key)
    except Exception as e:
        return f"Browser key error: {e}"

    try:
        page.wait_for_load_state("domcontentloaded", timeout=10000)
    except Exception:
        pass
    return f"Pressed: {key}"

def browser_screenshot(path: str = "~/Desktop/jarvis-browser.png") -> str:
    page, error = _ensure_browser()
    if error:
        return error
    output = os.path.expanduser(path or "~/Desktop/jarvis-browser.png")
    try:
        page.screenshot(path=output, full_page=True)
    except Exception as e:
        return f"Browser screenshot error: {e}"
    return f"Browser screenshot saved to {output}"

def browser_close(_: str = "") -> str:
    global browser_playwright, browser_context, browser_page
    try:
        if browser_context is not None:
            browser_context.close()
        if browser_playwright is not None:
            browser_playwright.stop()
    except Exception as e:
        return f"Browser close error: {e}"
    finally:
        browser_playwright = None
        browser_context = None
        browser_page = None
    return "Controlled browser closed"

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
    "browser_open":        browser_open,
    "browser_read_page":   lambda _: browser_read_page(),
    "browser_click":       browser_click,
    "browser_type":        None,   # two args
    "browser_press":       browser_press,
    "browser_screenshot":  lambda p: browser_screenshot(p if p else "~/Desktop/jarvis-browser.png"),
    "browser_close":       lambda _: browser_close(),
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

SYSTEM_PROMPT = f"""You are Jarvis, a personal AI assistant that controls a Mac and a real browser.

You have access to these tools:
{TOOLS_LIST}

Important behavior:
- You can control the Mac and the browser with tools. Do not say you cannot control Chrome, websites, or pages if a browser tool can help.
- For normal URL opening, prefer browser_open over open_url because browser_open creates a page you can read and interact with.
- To understand what is on a web page, use browser_read_page.
- To interact with a web page, use browser_click, browser_type, and browser_press.
- If the user asks you to search YouTube, open YouTube, type the search into the search box, press Enter, then read or click results.
- If the user asks you to solve a coding problem on a website, first open/read the page and inspect the problem. Do not claim you are blind to the page.
- If a browser action fails because the page needs login, say that the user needs to log in once in the controlled browser, then you can continue.

When you need to use a tool, respond EXACTLY like this:
TOOL: tool_name
INPUT: the input to the tool

For tools that need two inputs (write_file, move_file, send_notification, send_imessage, browser_type), separate with a comma:
TOOL: write_file
INPUT: ~/Desktop/note.txt, hello world

TOOL: send_notification
INPUT: Reminder, Time to study

TOOL: send_imessage
INPUT: +91XXXXXXXXXX, hey whats up

TOOL: move_file
INPUT: ~/Downloads/file.txt, ~/Documents/file.txt

TOOL: browser_type
INPUT: search, lofi beats

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
# VOICE — INPUT & OUTPUT
# ============================================================

recognizer = sr.Recognizer()
voice_microphone_index = None

def get_microphones():
    """Return available input microphones as (index, name) pairs."""
    try:
        import pyaudio
    except Exception as e:
        return [], f"PyAudio is not working: {e}"

    try:
        audio = pyaudio.PyAudio()
        microphones = []
        for index in range(audio.get_device_count()):
            info = audio.get_device_info_by_index(index)
            if int(info.get("maxInputChannels", 0)) > 0:
                microphones.append((index, info.get("name", f"Microphone {index}")))
        audio.terminate()
        return microphones, ""
    except Exception as e:
        return [], f"Could not read audio devices: {e}"

def get_microphone_index(refresh: bool = False):
    """Pick the configured mic, or the first input mic PyAudio can see."""
    global voice_microphone_index
    if voice_microphone_index is not None and not refresh:
        return voice_microphone_index

    configured = os.getenv("JARVIS_MIC_INDEX")
    if configured is not None:
        try:
            voice_microphone_index = int(configured)
            return voice_microphone_index
        except ValueError:
            print(f"[Voice warning] JARVIS_MIC_INDEX must be a number, got: {configured}")

    microphones, error = get_microphones()
    if error:
        print(f"[Voice error] {error}")
        return None
    if not microphones:
        print("[Voice error] No input microphones found.")
        print("[Voice hint] Run Jarvis from Terminal/iTerm/VS Code with microphone permission enabled.")
        return None

    preferred_words = ("macbook", "built-in", "internal")
    avoided_words = ("iphone", "teams")
    for index, name in microphones:
        lowered = name.lower()
        if any(word in lowered for word in preferred_words):
            voice_microphone_index = index
            return voice_microphone_index
    for index, name in microphones:
        lowered = name.lower()
        if not any(word in lowered for word in avoided_words):
            voice_microphone_index = index
            return voice_microphone_index
    voice_microphone_index = microphones[0][0]
    return voice_microphone_index

def print_voice_status():
    microphones, error = get_microphones()
    print(f"[Python] {sys.executable}")
    print(f"[SpeechRecognition] {sr.__version__}")
    if error:
        print(f"[Voice error] {error}")
        print("[Fix] Activate the env with: conda activate jarvis")
        return False
    if not microphones:
        print("[Microphones] none found")
        print("[Fix] Give your terminal microphone access in System Settings > Privacy & Security > Microphone.")
        return False
    print("[Microphones]")
    for index, name in microphones:
        print(f"  {index}: {name}")
    return True

def listen(microphone_index=None) -> str:
    """Record from mic and return transcribed text. Returns empty string on failure."""
    if microphone_index is None:
        microphone_index = get_microphone_index()
    if microphone_index is None:
        return ""

    try:
        with sr.Microphone(device_index=microphone_index) as source:
            print(f"[Listening on mic {microphone_index}... speak now]")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = recognizer.listen(source, timeout=6, phrase_time_limit=12)
            except sr.WaitTimeoutError:
                print("[No speech detected]")
                return ""
    except Exception as e:
        print(f"[Microphone error: {e}]")
        print("[Voice hint] Try /voice-test, or set a mic manually: export JARVIS_MIC_INDEX=1")
        return ""

    try:
        text = recognizer.recognize_google(audio)
        print(f"[You said]: {text}")
        return text
    except sr.UnknownValueError:
        print("[Could not understand audio]")
        return ""
    except sr.RequestError as e:
        print(f"[Speech recognition error: {e}]")
        print("[Voice hint] Google transcription needs internet. The local AI can stay offline, but this voice input path cannot.")
        return ""

def speak(text: str):
    """Speak text using Mac's built-in say command."""
    # Strip markdown-style formatting so it sounds natural
    clean = text.replace("*", "").replace("_", "").replace("`", "")
    try:
        subprocess.run(["say", clean])
    except Exception as e:
        print(f"[Speech output error: {e}]")

def normalized_command(text: str) -> str:
    """Map spoken command phrases to Jarvis slash commands."""
    cleaned = text.lower().strip()
    cleaned = cleaned.replace("\\", " slash ")
    cleaned = re.sub(r"[^a-z0-9/ ]+", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    command_map = {
        "slash memory": "/memory",
        "slash memories": "/memory",
        "slash messages": "/memory",
        "slash message": "/memory",
        "backslash memory": "/memory",
        "backslash messages": "/memory",
        "memory": "/memory",
        "messages": "/memory",
        "how many messages": "/memory",
        "how many messages are stored": "/memory",
        "memory size": "/memory",
        "list tools": "/tools",
        "show tools": "/tools",
        "what tools do you have": "/tools",
        "clear memory": "/clear",
        "wipe memory": "/clear",
        "turn on voice": "/voice",
        "turn off voice": "/voice",
        "stop voice": "/voice",
        "stop listening": "/voice",
        "voice off": "/voice",
        "voice on": "/voice",
        "exit": "exit",
        "quit": "exit",
        "bye": "exit",
    }
    return command_map.get(cleaned, text)

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
                    if "selector" in parsed and "text" in parsed:
                        input_val = f"{parsed['selector']}, {parsed['text']}"
                        return ("tool", tool_name, input_val)
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
    two_arg = {
        "write_file": write_file,
        "move_file": move_file,
        "send_notification": send_notification,
        "send_imessage": send_imessage,
        "browser_type": browser_type,
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

def main():
    print("Jarvis online.")
    print("'/clear' wipe memory | '/tools' list tools | '/memory' memory size | '/voice' toggle voice | '/voice-test' test mic | 'exit' quit\n")

    messages = load_memory()

    if not messages or messages[0].get("role") != "system":
        messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})
    else:
        messages[0]["content"] = SYSTEM_PROMPT

    voice_mode = False  # toggle with /voice

    while True:
        if voice_mode:
            user_input = listen(voice_microphone_index).strip()
            if not user_input:
                continue  # nothing heard, keep listening
        else:
            try:
                user_input = input("You: ").strip()
            except EOFError:
                save_memory(messages)
                print("\nMemory saved. Bye.")
                break

        if not user_input:
            continue

        user_input = normalized_command(user_input)

        if user_input.lower() in {"exit", "/exit", "/quit", "/bye"}:
            save_memory(messages)
            browser_close()
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

        if user_input.lower() in {"/memory", "/messages", "/message"}:
            memory_text = f"[{len(messages) - 1} messages in memory]"
            print(f"\n{memory_text}\n")
            if voice_mode:
                speak(memory_text)
            continue

        if user_input.lower() == "/voice-test":
            print_voice_status()
            microphone_index = get_microphone_index(refresh=True)
            heard = listen(microphone_index).strip()
            if heard:
                print(f"[Voice test passed] Heard: {heard}\n")
                speak(f"I heard: {heard}")
            else:
                print("[Voice test did not capture speech]\n")
            continue

        if user_input.lower() == "/voice":
            if not voice_mode and not print_voice_status():
                print("[Voice mode stayed OFF]\n")
                continue
            if not voice_mode and get_microphone_index(refresh=True) is None:
                print("[Voice mode stayed OFF]\n")
                continue
            voice_mode = not voice_mode
            status = "ON" if voice_mode else "OFF"
            print(f"[Voice mode {status}]\n")
            if voice_mode:
                print(f"[Using mic {voice_microphone_index}]\n")
            if voice_mode:
                speak(f"Voice mode on. I'm listening.")
            else:
                speak("Voice mode off.")
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
                if voice_mode:
                    speak(result[1])
                break

            elif result[0] == "tool":
                tool_output = run_tool(result[1], result[2])
                print(f"[Tool: {result[1]}] → {tool_output}\n")
                messages.append({"role": "assistant", "content": response_text})
                messages.append({"role": "user", "content": f"Tool result: {tool_output}"})

if __name__ == "__main__":
    main()
