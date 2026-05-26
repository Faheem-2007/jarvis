# Jarvis v2.0 — Personal AI Assistant for Mac
# Fast-path keyword routing: common commands never touch Ollama.
# Ollama is only called for conversation and complex tasks.

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
    return "Copied to clipboard"

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
    global browser_playwright, browser_context, browser_page
    if browser_page is not None and not browser_page.is_closed():
        return browser_page, ""
    try:
        from playwright.sync_api import sync_playwright
    except Exception as e:
        return None, f"Playwright not installed: {e}"
    try:
        os.makedirs(BROWSER_PROFILE_DIR, exist_ok=True)
        browser_playwright = sync_playwright().start()
        launch_options = {"headless": False, "accept_downloads": True}
        channel = os.getenv("JARVIS_BROWSER_CHANNEL", "").strip()
        if channel:
            launch_options["channel"] = channel
        try:
            browser_context = browser_playwright.chromium.launch_persistent_context(
                BROWSER_PROFILE_DIR, **launch_options)
        except Exception:
            launch_options.pop("channel", None)
            browser_context = browser_playwright.chromium.launch_persistent_context(
                BROWSER_PROFILE_DIR, **launch_options)
        browser_page = browser_context.pages[0] if browser_context.pages else browser_context.new_page()
        return browser_page, ""
    except Exception as e:
        return None, f"Could not start browser: {e}"

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
    if url.lower() in shortcuts:
        return shortcuts[url.lower()]
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
        return "Browser click error: provide visible text or CSS selector"
    try:
        if target.startswith(("css=", "xpath=", "//", "#", ".", "[", "button", "input", "a[")):
            page.locator(target.replace("css=", "", 1)).first.click(timeout=10000)
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
    return "Notification sent"

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
# FAST ROUTER
# Every entry: (pattern, tool_fn, arg_extractor)
# arg_extractor receives the full input string and returns
# the argument(s) needed, or None to use the default.
# ============================================================

def _extract_number(text: str) -> str | None:
    m = re.search(r'\b(\d+)\b', text)
    return m.group(1) if m else None

def _extract_app(text: str) -> str | None:
    # "open X" or "launch X" or "start X"
    m = re.search(r'(?:open|launch|start)\s+(.+)', text, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return None


def _extract_quit_app(text: str) -> str | None:
    m = re.search(r'(?:quit|close|kill)\s+(.+)', text, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return None

def _extract_url(text: str) -> str | None:
    m = re.search(r'(?:open|go to|navigate to|browse to)\s+(.+)', text, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return None

def _extract_city(text: str) -> str:
    m = re.search(r'weather\s+(?:in\s+|for\s+)?(.+)', text, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return "Chennai"

def _extract_reminder(text: str) -> str | None:
    m = re.search(r'(?:remind(?:er)?|add reminder)\s+(?:me\s+)?(?:to\s+)?(.+)', text, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return text

def _extract_path(text: str) -> str | None:
    m = re.search(r'(?:list|ls|show)\s+(.+)', text, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return "."

# Each rule: (compiled_regex, handler_fn)
# handler_fn(match, original_text) -> str result
FAST_ROUTES: list[tuple] = []

def _route(pattern: str):
    """Decorator to register a fast route."""
    def decorator(fn):
        FAST_ROUTES.append((re.compile(pattern, re.IGNORECASE), fn))
        return fn
    return decorator

@_route(r'\b(notify|notification|alert|remind me)\b')
def _r_notify(m, text):
    m2 = re.search(r'(?:notify|notification|alert|remind me)\s*[:\-]?\s*(.+)', text, re.IGNORECASE)
    if not m2:
        return "Usage: notify Title, Your message"
    parts = m2.group(1).split(',', 1)
    if len(parts) == 2:
        return send_notification(parts[0].strip(), parts[1].strip())
    return send_notification("Jarvis", parts[0].strip())

@_route(r'\b(what(?:\'s| is) the time|current time|time now|what time)\b')
def _r_time(m, text): return get_time()

@_route(r'\bbattery\b')
def _r_battery(m, text): return get_battery()

@_route(r'\b(wifi|wi-fi|network|ip address)\b')
def _r_wifi(m, text): return get_wifi()

@_route(r'\b(disk|storage|space)\b')
def _r_disk(m, text): return get_disk_space()

@_route(r'\b(ram|memory usage|memory pressure)\b')
def _r_ram(m, text): return get_ram_usage()

@_route(r'\b(cpu|processor)\b')
def _r_cpu(m, text): return get_cpu_usage()

@_route(r'\b(uptime|how long.*running)\b')
def _r_uptime(m, text): return get_uptime()

@_route(r'\b(active app|front app|what.*open|current app)\b')
def _r_active(m, text): return get_active_app()

@_route(r'\b(what.*volume|volume level|current volume)\b')
def _r_get_vol(m, text): return get_volume()

@_route(r'\bset volume\b')
def _r_set_vol(m, text):
    n = _extract_number(text)
    return set_volume(n) if n else "Couldn't find a volume level in your request"

@_route(r'\b(brightness level|what.*brightness)\b')
def _r_get_bright(m, text): return get_brightness()

@_route(r'\bset brightness\b')
def _r_set_bright(m, text):
    n = _extract_number(text)
    return set_brightness(n) if n else "Couldn't find a brightness level"

@_route(r'\b(screenshot|screen capture|capture screen)\b')
def _r_screenshot(m, text): return take_screenshot()

@_route(r'\b(lock|lock screen|lock the screen)\b')
def _r_lock(m, text): return lock_screen()

@_route(r'\b(sleep|sleep mac|put.*sleep)\b')
def _r_sleep(m, text): return sleep_mac()

@_route(r'\b(empty trash|clear trash)\b')
def _r_trash(m, text): return empty_trash()

@_route(r'\b(mute|silence)\b')
def _r_mute(m, text): return mute()

@_route(r'\bunmute\b')
def _r_unmute(m, text): return unmute()

@_route(r'\b(clipboard|paste|what.*clipboard)\b')
def _r_clipboard(m, text): return read_clipboard()

@_route(r'\b(open|launch|start)\s+\w')
def _r_open_app(m, text):
    app = _extract_app(text)
    return open_app(app) if app else "Couldn't find app name"

@_route(r'\b(quit|close|kill)\s+\w')
def _r_quit_app(m, text):
    app = _extract_quit_app(text)
    return quit_app(app) if app else "Couldn't find app name"

@_route(r'\b(go to|navigate to|browse to|open url|open site)\s+\S')
def _r_url(m, text):
    url = _extract_url(text)
    return browser_open(url) if url else "Couldn't find a URL"

@_route(r'\bweather\b')
def _r_weather(m, text):
    city = _extract_city(text)
    return get_weather(city)

@_route(r'\b(play|pause|play pause|toggle music)\b')
def _r_playpause(m, text): return music_play_pause()

@_route(r'\b(next (track|song)|skip)\b')
def _r_next(m, text): return music_next()

@_route(r'\b(previous (track|song)|prev|back)\b')
def _r_prev(m, text): return music_previous()

@_route(r'\b(current song|what.*playing|now playing|whats on)\b')
def _r_song(m, text): return get_current_song()

@_route(r'\b(calendar|events today|my schedule|what.*today)\b')
def _r_calendar(m, text): return get_calendar_events()

@_route(r'\b(remind|reminder)\b')
def _r_reminder(m, text):
    reminder = _extract_reminder(text)
    return add_reminder(reminder) if reminder else "Couldn't parse reminder"

@_route(r'\b(list|ls|show files|show directory)\b')
def _r_ls(m, text):
    path = _extract_path(text)
    return list_directory(path)

@_route(r'\b(current tab|what tab|active tab)\b')
def _r_tab(m, text): return get_current_tab()

@_route(r'\b(read page|what.*page say|page content)\b')
def _r_read(m, text): return browser_read_page()

@_route(r'\bclose browser\b')
def _r_close_browser(m, text): return browser_close()

def quick_route(text: str):
    """
    Try each fast route in order.
    Returns the tool result string if matched, or None if no match.
    """
    for pattern, handler in FAST_ROUTES:
        m = pattern.search(text)
        if m:
            try:
                return handler(m, text)
            except Exception as e:
                return f"Error: {e}"
    return None

# ============================================================
# TOOL REGISTRY  (still used by Ollama fallback path)
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
    "write_file":          None,
    "list_directory":      lambda p: list_directory(p if p else "."),
    "create_folder":       create_folder,
    "move_file":           None,
    "delete_file":         delete_file,
    "get_file_info":       get_file_info,
    "open_url":            open_url,
    "get_current_tab":     lambda _: get_current_tab(),
    "browser_open":        browser_open,
    "browser_read_page":   lambda _: browser_read_page(),
    "browser_click":       browser_click,
    "browser_type":        None,
    "browser_press":       browser_press,
    "browser_screenshot":  lambda p: browser_screenshot(p if p else "~/Desktop/jarvis-browser.png"),
    "browser_close":       lambda _: browser_close(),
    "send_notification":   None,
    "get_calendar_events": lambda _: get_calendar_events(),
    "add_reminder":        add_reminder,
    "music_play_pause":    lambda _: music_play_pause(),
    "music_next":          lambda _: music_next(),
    "music_previous":      lambda _: music_previous(),
    "get_current_song":    lambda _: get_current_song(),
    "send_imessage":       None,
    "get_weather":         lambda c: get_weather(c if c else "Chennai"),
}

TOOLS_LIST = "\n".join([f"- {name}" for name in TOOLS.keys()])

# ============================================================
# SYSTEM PROMPT  (Ollama fallback only)
# ============================================================

SYSTEM_PROMPT = f"""You are Jarvis, a personal AI assistant that controls a Mac.

You have access to these tools:
{TOOLS_LIST}

When you need to use a tool, respond EXACTLY like this:
TOOL: tool_name
INPUT: the input to the tool

For tools that need two inputs (write_file, move_file, send_notification, send_imessage, browser_type), separate with a comma:
TOOL: write_file
INPUT: ~/Desktop/note.txt, hello world

When you have a final answer, respond like this:
ANSWER: your response

Never mix formats. Only one action per response."""

# ============================================================
# MEMORY
# ============================================================

MEMORY_FILE = "memory.json"
MAX_MEMORY_MESSAGES = 40  # keep last 40 exchanges to avoid context overflow

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            print("[Memory loaded]\n")
            return json.load(f)
    return [{"role": "system", "content": SYSTEM_PROMPT}]

def save_memory(messages):
    with open(MEMORY_FILE, 'w') as f:
        json.dump(messages, f, indent=2)

def trim_memory(messages):
    """Keep system prompt + last MAX_MEMORY_MESSAGES messages."""
    system = [m for m in messages if m["role"] == "system"]
    rest = [m for m in messages if m["role"] != "system"]
    if len(rest) > MAX_MEMORY_MESSAGES:
        rest = rest[-MAX_MEMORY_MESSAGES:]
    return system + rest

# ============================================================
# VOICE
# ============================================================

recognizer = sr.Recognizer()
voice_microphone_index = None

def get_microphones():
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
        return None
    preferred_words = ("macbook", "built-in", "internal")
    avoided_words = ("iphone", "teams")
    for index, name in microphones:
        if any(w in name.lower() for w in preferred_words):
            voice_microphone_index = index
            return voice_microphone_index
    for index, name in microphones:
        if not any(w in name.lower() for w in avoided_words):
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
        return False
    if not microphones:
        print("[Microphones] none found")
        return False
    print("[Microphones]")
    for index, name in microphones:
        print(f"  {index}: {name}")
    return True

def listen(microphone_index=None) -> str:
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
        return ""

def speak(text: str):
    clean = text.replace("*", "").replace("_", "").replace("`", "")
    try:
        subprocess.run(["say", clean])
    except Exception as e:
        print(f"[Speech output error: {e}]")

def normalized_command(text: str) -> str:
    cleaned = text.lower().strip()
    cleaned = cleaned.replace("\\", " slash ")
    cleaned = re.sub(r"[^a-z0-9/ ]+", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    command_map = {
        "slash memory": "/memory", "slash memories": "/memory",
        "memory": "/memory", "memory size": "/memory",
        "list tools": "/tools", "show tools": "/tools",
        "clear memory": "/clear", "wipe memory": "/clear",
        "turn on voice": "/voice", "turn off voice": "/voice",
        "voice off": "/voice", "voice on": "/voice",
        "exit": "exit", "quit": "exit", "bye": "exit",
    }
    return command_map.get(cleaned, text)

# ============================================================
# OLLAMA FALLBACK — parse + run
# ============================================================

def parse_response(text: str):
    lines = text.strip().split('\n')
    for i, line in enumerate(lines):
        if line.startswith("TOOL:"):
            tool_name = line.replace("TOOL:", "").strip()
            input_val = ""
            for j in range(i + 1, len(lines)):
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
            return f"Error running {name}: {e}"
    return f"Unknown tool: {name}"

def chat(messages):
    try:
        response = ollama.chat(
            model="qwen2.5-coder:7b",
            messages=messages
        )
        return response['message']['content']
    except Exception as e:
        return (
            "ANSWER: I could not connect to Ollama. "
            "Run `ollama serve` in a terminal tab, then try again. "
            f"Details: {e}"
        )

def ollama_loop(user_input: str, messages: list) -> str:
    """Send to Ollama and run up to 5 tool calls. Returns final answer string."""
    messages.append({"role": "user", "content": user_input})
    for _ in range(5):
        response_text = chat(messages)
        print(f"\n[Jarvis thinking]: {response_text}\n")
        result = parse_response(response_text)
        if result[0] == "answer":
            messages.append({"role": "assistant", "content": result[1]})
            return result[1]
        elif result[0] == "tool":
            tool_output = run_tool(result[1], result[2])
            print(f"[Tool: {result[1]}] → {tool_output}\n")
            messages.append({"role": "assistant", "content": response_text})
            messages.append({"role": "user", "content": f"Tool result: {tool_output}"})
    return "I couldn't complete that in time."

# ============================================================
# MAIN LOOP
# ============================================================

def main():
    print("Jarvis online. (v2.0 — fast routing enabled)")
    print("Commands: /clear  /tools  /memory  /voice  /voice-test  exit\n")

    messages = load_memory()

    if not messages or messages[0].get("role") != "system":
        messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})
    else:
        messages[0]["content"] = SYSTEM_PROMPT

    voice_mode = False

    while True:
        if voice_mode:
            user_input = listen(voice_microphone_index).strip()
            if not user_input:
                continue
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

        # --- Slash commands ---
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
                speak("Voice mode on. I'm listening.")
            else:
                speak("Voice mode off.")
            continue

        # --- Fast route (no Ollama) ---
        fast_result = quick_route(user_input)
        if fast_result is not None:
            print(f"Jarvis: {fast_result}\n")
            if voice_mode:
                speak(fast_result)
            continue

        # --- Ollama fallback ---
        answer = ollama_loop(user_input, messages)
        messages = trim_memory(messages)
        save_memory(messages)
        print(f"Jarvis: {answer}\n")
        if voice_mode:
            speak(answer)


if __name__ == "__main__":
    main()