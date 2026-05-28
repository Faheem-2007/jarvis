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
import html as html_lib
import urllib.parse
import urllib.request
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
browser_last_url = None
browser_unavailable_reason = ""

def _short_error(error: str, max_len: int = 260) -> str:
    error = re.sub(r"\s+", " ", str(error)).strip()
    return error[:max_len] + ("..." if len(error) > max_len else "")

def _cleanup_browser_state():
    global browser_playwright, browser_context, browser_page
    try:
        if browser_context is not None:
            browser_context.close()
    except Exception:
        pass
    try:
        if browser_playwright is not None:
            browser_playwright.stop()
    except Exception:
        pass
    browser_playwright = None
    browser_context = None
    browser_page = None

def _ensure_browser():
    global browser_playwright, browser_context, browser_page, browser_unavailable_reason
    if browser_unavailable_reason:
        return None, browser_unavailable_reason
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
        _cleanup_browser_state()
        browser_unavailable_reason = f"Controlled browser unavailable: {_short_error(e)}"
        return None, browser_unavailable_reason

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
    global browser_last_url
    target = _normalize_url(url)
    browser_last_url = target
    page, error = _ensure_browser()
    if error:
        result = subprocess.run(["open", target], capture_output=True, text=True)
        if result.stderr.strip():
            return f"Browser open error: {result.stderr.strip()} ({error})"
        return f"Opened in system browser: {target} ({error})"
    try:
        page.goto(target, wait_until="domcontentloaded", timeout=30000)
        page.bring_to_front()
        return f"Browser opened: {page.title()} | {page.url}"
    except Exception as e:
        result = subprocess.run(["open", target], capture_output=True, text=True)
        if result.stderr.strip():
            return f"Browser open error: {_short_error(e)}; system open also failed: {result.stderr.strip()}"
        return f"Opened in system browser: {target} (controlled browser open failed: {_short_error(e)})"

def _html_title(html_text: str) -> str:
    m = re.search(r"(?is)<title[^>]*>(.*?)</title>", html_text or "")
    return _strip_html(m.group(1)) if m else "Untitled"

def browser_read_page(url: str = "") -> str:
    target = _normalize_url(url) if (url or "").strip() else browser_last_url
    page, error = _ensure_browser()
    if not error:
        try:
            title = page.title()
            page_url = page.url
            text = page.locator("body").inner_text(timeout=8000)
            text = re.sub(r"\n{3,}", "\n\n", text).strip()
            if len(text) > 6000:
                text = text[:6000] + "\n...[truncated]"
            return f"Title: {title}\nURL: {page_url}\n\n{text}"
        except Exception as e:
            error = f"Browser read error: {_short_error(e)}"
    if target:
        try:
            html_text = _http_get(target)
            text = _strip_html(html_text)
            if len(text) > 6000:
                text = text[:6000] + "\n...[truncated]"
            return f"Title: {_html_title(html_text)}\nURL: {target}\n\n{text}"
        except Exception as e:
            return f"{error}. Direct page read also failed: {_short_error(e)}"
    return f"{error}. No page URL is available to read directly."

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
    global browser_playwright, browser_context, browser_page, browser_unavailable_reason, browser_last_url
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
        browser_unavailable_reason = ""
        browser_last_url = None
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

def _applescript_quote(text: str) -> str:
    return '"' + str(text).replace("\\", "\\\\").replace('"', '\\"') + '"'

def _confirm_before_sending(action: str, preview: str) -> bool:
    print(f"\n[Approval required] {action}")
    print(preview[:1500])
    try:
        answer = input("Type YES to approve sending: ").strip()
    except EOFError:
        return False
    return answer == "YES"

def send_imessage(phone: str, message: str) -> str:
    if not _confirm_before_sending(
        f"Send iMessage to {phone}",
        f"Message:\n{message}",
    ):
        return "Message cancelled: approval was not given."
    script = f'''
    tell application "Messages"
        set targetBuddy to {_applescript_quote(phone)}
        set targetService to id of 1st account whose service type = iMessage
        send {_applescript_quote(message)} to buddy targetBuddy of account id targetService
    end tell
    '''
    subprocess.run(["osascript", "-e", script])
    return f"iMessage sent to {phone}"

# --- EMAIL ---

def create_email_draft(recipient: str, subject: str, body: str) -> str:
    recipient = recipient.strip()
    subject = subject.strip() or "Jarvis"
    body = body.strip()
    if not recipient or not body:
        return "Email draft error: recipient and body are required."
    script = f'''
    tell application "Mail"
        set newMessage to make new outgoing message with properties {{subject:{_applescript_quote(subject)}, content:{_applescript_quote(body)}, visible:true}}
        tell newMessage
            make new to recipient at end of to recipients with properties {{address:{_applescript_quote(recipient)}}}
        end tell
        activate
    end tell
    '''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if result.stderr.strip():
        return f"Email draft error: {result.stderr.strip()}"
    return f"Email draft created for {recipient}"

def send_email(recipient: str, subject: str, body: str) -> str:
    recipient = recipient.strip()
    subject = subject.strip() or "Jarvis"
    body = body.strip()
    if not recipient or not body:
        return "Email error: recipient and body are required."
    if not _confirm_before_sending(
        f"Send email to {recipient}",
        f"Subject: {subject}\n\n{body}",
    ):
        return "Email cancelled: approval was not given."
    script = f'''
    tell application "Mail"
        set newMessage to make new outgoing message with properties {{subject:{_applescript_quote(subject)}, content:{_applescript_quote(body)}, visible:true}}
        tell newMessage
            make new to recipient at end of to recipients with properties {{address:{_applescript_quote(recipient)}}}
            send
        end tell
    end tell
    '''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if result.stderr.strip():
        return f"Email send error: {result.stderr.strip()}"
    return f"Email sent to {recipient}"

# --- WEATHER ---

def get_weather(city: str = "Chennai") -> str:
    result = subprocess.run(
        f"curl -s 'wttr.in/{city}?format=3'",
        shell=True, capture_output=True, text=True
    )
    return result.stdout.strip()

# --- INTERNET RESEARCH ---

RESEARCH_REPORT_DIR = "research_reports"
RESEARCH_MAX_SOURCES = 6
RESEARCH_SOURCE_CHARS = 3500
EMAIL_PATTERN = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)

def latest_research_report() -> str | None:
    if not os.path.isdir(RESEARCH_REPORT_DIR):
        return None
    reports = [
        os.path.join(RESEARCH_REPORT_DIR, name)
        for name in os.listdir(RESEARCH_REPORT_DIR)
        if name.endswith(".md")
    ]
    if not reports:
        return None
    return max(reports, key=os.path.getmtime)

def _read_report(path: str | None = None):
    report_path = os.path.expanduser(path.strip()) if path else latest_research_report()
    if not report_path:
        return None, "No research report found."
    if not os.path.exists(report_path):
        return None, f"Report not found: {report_path}"
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            return (report_path, f.read())
    except Exception as e:
        return None, f"Could not read report: {e}"

def _extract_emails(text: str):
    emails = []
    for email in EMAIL_PATTERN.findall(text or ""):
        cleaned = email.strip(".,;:()[]{}<>").lower()
        if cleaned and cleaned not in emails:
            emails.append(cleaned)
    return emails

def _direct_urls(text: str):
    urls = []
    for url in re.findall(r"https?://[^\s,]+", text or ""):
        cleaned = url.rstrip(".,;:)")
        if cleaned not in urls:
            urls.append(cleaned)
    return urls

def _contact_page_candidates(url: str):
    parsed = urllib.parse.urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return []
    base = f"{parsed.scheme}://{parsed.netloc}"
    paths = [parsed.path or "/", "/contact", "/contact-us", "/contact.html", "/about", "/about-us"]
    candidates = []
    for path in paths:
        target = urllib.parse.urljoin(base, path)
        if target not in candidates:
            candidates.append(target)
    return candidates

def _collect_contact_sources(query: str):
    candidates = []
    for url in _direct_urls(query):
        candidates.extend(_contact_page_candidates(url))
    if not candidates:
        try:
            results = web_search(f"{query} contact email")
            for result in results:
                candidates.append(result["url"])
                if any(word in result["url"].lower() for word in ("contact", "about")):
                    candidates.extend(_contact_page_candidates(result["url"]))
        except Exception as e:
            print(f"[Contacts] Search skipped: {e}")

    sources = []
    seen = set()
    for url in candidates:
        if url in seen or not url.startswith(("http://", "https://")):
            continue
        seen.add(url)
        print(f"[Contacts] Checking: {url}")
        try:
            html_text = _http_get(url)
            text = _strip_html(html_text)
            emails = _extract_emails(html_text + "\n" + text)
            if len(text) < 100 and not emails:
                continue
            sources.append({
                "url": url,
                "emails": emails,
                "text": text[:1600],
            })
        except Exception as e:
            print(f"[Contacts] Skipped: {e}")
        if len(sources) >= RESEARCH_MAX_SOURCES:
            break
    return sources

def _write_contact_report(query: str, sources: list[dict], emails: list[str]) -> str:
    os.makedirs(RESEARCH_REPORT_DIR, exist_ok=True)
    date_prefix = datetime.datetime.now().strftime("%Y-%m-%d")
    path = os.path.join(RESEARCH_REPORT_DIR, f"{date_prefix}-{_slugify(query)}-contacts.md")
    source_notes = "\n\n".join(
        f"### Source {index}: {source['url']}\n\n"
        f"Emails found: {', '.join(source['emails']) or 'none'}\n\n"
        f"{source['text']}"
        for index, source in enumerate(sources, start=1)
    )
    content = f"""# Contact Research: {query}

## Emails Found

{chr(10).join(f"- {email}" for email in emails) or "- No email address found."}

## Research Progress

- Checked {len(sources)} readable source(s).
- Preferred direct website/contact pages before general web results.

## Source Notes

{source_notes or "No readable source notes were collected."}
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.rstrip() + "\n")
    return path

def find_contact_emails(query: str) -> str:
    query = (query or "").strip()
    if not query:
        return "Contact research error: provide a company, website, or contact lookup goal."
    sources = _collect_contact_sources(query)
    emails = []
    for source in sources:
        for email in source["emails"]:
            if email not in emails:
                emails.append(email)
    report_path = _write_contact_report(query, sources, emails)
    if not emails:
        return f"No email address found. Contact research saved: {report_path}"
    return f"Found email(s): {', '.join(emails)}\nContact research saved: {report_path}"

def _extract_message_to_send(text: str) -> str:
    m = re.search(r"\bsend\s+(?:an?\s+email\s+|mail\s+|message\s+)?(.+)$", text, re.IGNORECASE)
    if not m:
        return "Hi"
    body = m.group(1).strip()
    body = re.sub(r"\s+(?:to|on|in)\s+(?:their\s+)?(?:mail\s+id|email|contact).*$", "", body, flags=re.IGNORECASE).strip()
    return body or "Hi"

def _contact_query_without_send(text: str) -> str:
    return re.sub(r"\b(?:and\s+)?send\b.+$", "", text, flags=re.IGNORECASE).strip() or text.strip()

def contact_email_workflow(input_val: str) -> str:
    query = _contact_query_without_send(input_val)
    body = _extract_message_to_send(input_val)
    contact_result = find_contact_emails(query)
    emails = _extract_emails(contact_result)
    if not emails:
        return contact_result
    return send_email(emails[0], "Hello", body)

def email_research_report(input_val: str) -> str:
    parts = [part.strip() for part in input_val.split(",", 2)]
    recipient = parts[0] if parts else ""
    report_path = parts[1] if len(parts) > 1 else None
    if not recipient:
        return "Report email error: provide recipient email."
    path, report = _read_report(report_path)
    if not path:
        return report
    subject = f"Research report: {os.path.splitext(os.path.basename(path))[0]}"
    return send_email(recipient, subject, report)

def message_research_report(input_val: str) -> str:
    parts = [part.strip() for part in input_val.split(",", 1)]
    phone = parts[0] if parts else ""
    report_path = parts[1] if len(parts) > 1 else None
    if not phone:
        return "Report message error: provide phone number or contact."
    path, report = _read_report(report_path)
    if not path:
        return report
    title = os.path.splitext(os.path.basename(path))[0]
    excerpt = re.sub(r"\s+", " ", report).strip()[:1200]
    message = f"Research report ready: {title}\n\n{excerpt}"
    if len(report) > len(excerpt):
        message += "\n\nFull report is saved locally in Jarvis."
    return send_imessage(phone, message)

def _slugify(text: str, max_len: int = 70) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return (slug[:max_len].strip("-") or "research")

def _http_get(url: str, timeout: int = 15) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 JarvisResearch/1.0"
            )
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        content_type = response.headers.get("Content-Type", "")
        charset = response.headers.get_content_charset() or "utf-8"
        raw = response.read(2_000_000)
    if "pdf" in content_type.lower():
        return ""
    return raw.decode(charset, errors="replace")

def _clean_search_url(url: str) -> str:
    url = html_lib.unescape(url)
    if url.startswith("//"):
        url = "https:" + url
    parsed = urllib.parse.urlparse(url)
    if "duckduckgo.com" in parsed.netloc and parsed.path.startswith("/l/"):
        target = urllib.parse.parse_qs(parsed.query).get("uddg", [""])[0]
        if target:
            return target
    return url

def _strip_html(html_text: str) -> str:
    html_text = re.sub(r"(?is)<(script|style|noscript|svg).*?</\1>", " ", html_text)
    html_text = re.sub(r"(?is)<br\s*/?>", "\n", html_text)
    html_text = re.sub(r"(?is)</(p|div|li|h[1-6]|tr)>", "\n", html_text)
    text = re.sub(r"(?is)<[^>]+>", " ", html_text)
    text = html_lib.unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def web_search(query: str, max_results: int = RESEARCH_MAX_SOURCES):
    search_url = "https://duckduckgo.com/html/?" + urllib.parse.urlencode({"q": query})
    html_text = _http_get(search_url)
    matches = re.findall(
        r'<a[^>]+class="[^"]*result__a[^"]*"[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
        html_text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    results = []
    seen = set()
    for raw_url, raw_title in matches:
        url = _clean_search_url(raw_url)
        title = _strip_html(raw_title)
        if not url.startswith(("http://", "https://")) or url in seen:
            continue
        seen.add(url)
        results.append({"title": title or url, "url": url})
        if len(results) >= max_results:
            break
    return results

def _fetch_research_sources(query: str):
    print(f"[Research] Searching: {query}")
    results = web_search(query)
    sources = []
    for index, result in enumerate(results, start=1):
        print(f"[Research] Reading source {index}: {result['title']}")
        try:
            page_html = _http_get(result["url"])
            page_text = _strip_html(page_html)
            if len(page_text) < 300:
                continue
            sources.append({
                "id": len(sources) + 1,
                "title": result["title"],
                "url": result["url"],
                "text": page_text[:RESEARCH_SOURCE_CHARS],
            })
        except Exception as e:
            print(f"[Research] Skipped source: {e}")
    return sources

def _fallback_research_report(query: str, sources: list[dict]) -> str:
    bibliography = "\n".join(
        f"- [{source['id']}] {source['title']} - {source['url']}"
        for source in sources
    ) or "- No sources collected."
    notes = "\n\n".join(
        f"### [{source['id']}] {source['title']}\n\n{source['text'][:1200]}"
        for source in sources
    )
    return f"""# Research Report: {query}

## Research Progress

- Searched the web for: {query}
- Collected {len(sources)} readable source(s).
- Ollama was unavailable, so this report contains source notes instead of a synthesized winner.

## Source Notes

{notes or "No readable source notes were collected."}

## Bibliography

{bibliography}
"""

def _ensure_bibliography(report: str, sources: list[dict]) -> str:
    if re.search(r"(?im)^##\s+bibliography\b", report):
        return report
    bibliography = "\n".join(
        f"- [{source['id']}] {source['title']} - {source['url']}"
        for source in sources
    )
    return report.rstrip() + f"\n\n## Bibliography\n\n{bibliography}\n"

def _write_research_report(query: str, report: str) -> str:
    os.makedirs(RESEARCH_REPORT_DIR, exist_ok=True)
    date_prefix = datetime.datetime.now().strftime("%Y-%m-%d")
    path = os.path.join(RESEARCH_REPORT_DIR, f"{date_prefix}-{_slugify(query)}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(report.rstrip() + "\n")
    return path

def internet_research(query: str) -> str:
    query = (query or "").strip()
    if not query:
        return "Research error: please provide a topic to research."
    try:
        sources = _fetch_research_sources(query)
    except Exception as e:
        return f"Research error while searching the web: {e}"
    if not sources:
        return "Research error: I could not collect readable web sources for that topic."

    source_pack = "\n\n".join(
        f"[{source['id']}] {source['title']}\nURL: {source['url']}\n{source['text']}"
        for source in sources
    )
    prompt = f"""Create a practical research report for this user request:
{query}

Use only the sources below. If a detail is missing or uncertain, say so.

The report must include:
- Research Progress
- Executive Summary
- Shortlist / Options Compared
- Pros and Cons for each option
- Price/value notes when available
- Final Winner with clear reasoning
- Risks, caveats, or what to verify before buying/deciding
- Bibliography with numbered source links

Sources:
{source_pack}
"""
    try:
        print("[Research] Synthesizing report with AI...")
        response = ollama.chat(
            model="qwen2.5-coder:7b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a careful internet research assistant. "
                        "Write concise Markdown reports with source citations like [1]."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        )
        report = response["message"]["content"].strip()
    except Exception as e:
        print(f"[Research] AI synthesis fallback: {e}")
        report = _fallback_research_report(query, sources)

    report = _ensure_bibliography(report, sources)
    path = _write_research_report(query, report)
    return f"Research report saved: {path} ({len(sources)} sources)"

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

def _extract_research_query(text: str) -> str | None:
    m = re.search(
        r'(?:research|search(?: about| for)?|find out about|look up|investigate)\s+(.+)',
        text,
        re.IGNORECASE,
    )
    if m:
        return m.group(1).strip()
    return text.strip() or None

def _extract_contact_after_to(text: str) -> str | None:
    m = re.search(r'\bto\s+([^,]+)', text, re.IGNORECASE)
    return m.group(1).strip() if m else None

def _extract_three_part_input(text: str):
    parts = [part.strip() for part in text.split(",", 2)]
    while len(parts) < 3:
        parts.append("")
    return parts[0], parts[1], parts[2]

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

@_route(r'\b(email|mail)\s+report\b')
def _r_email_report(m, text):
    recipient = _extract_contact_after_to(text)
    return email_research_report(recipient or "")

@_route(r'\b(message|text|imessage)\s+report\b')
def _r_message_report(m, text):
    contact = _extract_contact_after_to(text)
    return message_research_report(contact or "")

@_route(r'\b(draft email|draft mail)\b')
def _r_draft_email(m, text):
    m2 = re.search(r'\b(?:draft email|draft mail)\s*[:\-]?\s*(.+)', text, re.IGNORECASE | re.DOTALL)
    if not m2:
        return "Usage: draft email recipient, subject, body"
    recipient, subject, body = _extract_three_part_input(m2.group(1))
    return create_email_draft(recipient, subject, body)

@_route(r'\b(send email|send mail)\b')
def _r_send_email(m, text):
    m2 = re.search(r'\b(?:send email|send mail)\s*[:\-]?\s*(.+)', text, re.IGNORECASE | re.DOTALL)
    if not m2:
        return "Usage: send email recipient, subject, body"
    recipient, subject, body = _extract_three_part_input(m2.group(1))
    return send_email(recipient, subject, body)

@_route(r'\b(send message|send text|send imessage)\b')
def _r_send_message(m, text):
    m2 = re.search(r'\b(?:send message|send text|send imessage)\s*[:\-]?\s*(.+)', text, re.IGNORECASE | re.DOTALL)
    if not m2:
        return "Usage: send message contact, message"
    parts = m2.group(1).split(",", 1)
    if len(parts) != 2:
        return "Usage: send message contact, message"
    return send_imessage(parts[0].strip(), parts[1].strip())

@_route(r'\b(find|search|look up|research)\b.*\b(email|mail id|mail|contact)\b.*\bsend\b')
def _r_contact_email_workflow(m, text):
    return contact_email_workflow(text)

@_route(r'\b(find|search|look up|research)\b.*\b(email|mail id|contact)\b')
def _r_find_contact_emails(m, text):
    return find_contact_emails(text)

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

@_route(r'\b(research|search about|search for|find out about|look up|investigate)\b')
def _r_research(m, text):
    query = _extract_research_query(text)
    return internet_research(query) if query else "Research error: please provide a topic."

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

AUTOMATION_HANDOFF_MARKERS = (
    "couldn't",
    "could not",
    "error:",
    "usage:",
    "unknown tool",
    "unable",
    "not installed",
    "not working",
    "not found",
    "unavailable",
    "provide",
    "needs two inputs",
)

def automation_needs_ai(result: str | None) -> bool:
    """Decide whether the fast automation result should be recovered by AI."""
    if result is None:
        return True
    cleaned = result.strip().lower()
    if not cleaned:
        return True
    return any(marker in cleaned for marker in AUTOMATION_HANDOFF_MARKERS)

def build_ai_handoff_input(user_input: str, automation_result: str | None) -> str:
    if automation_result is None:
        return user_input
    return (
        f"{user_input}\n\n"
        "Fast automation tried first but did not complete the request.\n"
        f"Automation result: {automation_result}\n"
        "Recover by selecting the best available tool. "
        "If the request is genuinely ambiguous, ask one short clarification."
    )

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
    "create_email_draft":  None,
    "send_email":          None,
    "email_research_report": email_research_report,
    "message_research_report": message_research_report,
    "find_contact_emails": find_contact_emails,
    "contact_email_workflow": contact_email_workflow,
    "get_calendar_events": lambda _: get_calendar_events(),
    "add_reminder":        add_reminder,
    "music_play_pause":    lambda _: music_play_pause(),
    "music_next":          lambda _: music_next(),
    "music_previous":      lambda _: music_previous(),
    "get_current_song":    lambda _: get_current_song(),
    "send_imessage":       None,
    "get_weather":         lambda c: get_weather(c if c else "Chennai"),
    "internet_research":   internet_research,
}

TOOLS_LIST = "\n".join([f"- {name}" for name in TOOLS.keys()])

# ============================================================
# SYSTEM PROMPT  (Ollama fallback only)
# ============================================================

SYSTEM_PROMPT = f"""You are Jarvis, a personal AI assistant that controls a Mac.

You have access to these tools:
{TOOLS_LIST}

The program tries simple automation before asking you. If you receive a message
saying fast automation did not complete the request, recover by choosing the
best tool or by asking one short clarification question.

When you need to use a tool, respond EXACTLY like this:
TOOL: tool_name
INPUT: the input to the tool

For tools that need two inputs (write_file, move_file, send_notification, send_imessage, browser_type), separate with a comma:
TOOL: write_file
INPUT: ~/Desktop/note.txt, hello world

For email tools that need three inputs (create_email_draft, send_email), separate with commas:
TOOL: create_email_draft
INPUT: person@example.com, Subject line, Email body

For sharing the latest research report:
TOOL: email_research_report
INPUT: person@example.com

TOOL: message_research_report
INPUT: phone number or contact name

For finding a company contact email:
TOOL: find_contact_emails
INPUT: company name or website URL

For finding a contact email and sending a short approved email:
TOOL: contact_email_workflow
INPUT: company name or website URL and the message to send

For internet research requests, use internet_research with the full research goal:
TOOL: internet_research
INPUT: EV cars below 15 lakhs in India with pros, cons, winner, and bibliography

Do not send unsolicited bulk outreach or spam. For lead outreach, draft messages
or send only to user-provided recipients with approval. Sending tools will ask
for confirmation before anything leaves the computer.

If browser_open says it opened in the system browser because the controlled
browser is unavailable, do not retry browser_open repeatedly. Use
browser_read_page with the URL, internet_research, find_contact_emails, or
contact_email_workflow instead.

When you have a final answer, respond like this:
ANSWER: your response

Never mix formats. Only one action per response."""

# ============================================================
# MEMORY
# ============================================================

MEMORY_FILE = "memory.json"
MAX_MEMORY_MESSAGES = 40  # trigger compression after this many raw messages
RECENT_MEMORY_MESSAGES = 24  # keep this many raw messages after compression
MEMORY_SUMMARY_MAX_CHARS = 5000
MEMORY_FACTS_MAX_ITEMS = 30
MEMORY_CONTEXT_HEADER = "Long-term memory summary:"
MEMORY_STATE = {
    "summary": "",
    "facts": [],
}

def reset_memory_state():
    MEMORY_STATE["summary"] = ""
    MEMORY_STATE["facts"] = []

def _valid_message(message):
    return (
        isinstance(message, dict)
        and message.get("role") in {"user", "assistant", "system"}
        and isinstance(message.get("content"), str)
    )

def _conversation_messages(messages):
    return [
        m for m in messages
        if _valid_message(m) and m.get("role") != "system"
    ]

def _memory_context_message():
    summary = MEMORY_STATE.get("summary", "").strip()
    facts = [
        str(f).strip()
        for f in MEMORY_STATE.get("facts", [])
        if str(f).strip()
    ][:MEMORY_FACTS_MAX_ITEMS]
    if not summary and not facts:
        return None
    content = MEMORY_CONTEXT_HEADER
    if summary:
        content += f"\n{summary}"
    if facts:
        content += "\n\nDurable facts:\n" + "\n".join(f"- {fact}" for fact in facts)
    return {"role": "system", "content": content}

def _compose_messages(recent_messages):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    context = _memory_context_message()
    if context:
        messages.append(context)
    messages.extend([m for m in recent_messages if _valid_message(m) and m.get("role") != "system"])
    return messages

def _load_memory_payload(payload):
    reset_memory_state()
    if isinstance(payload, dict):
        MEMORY_STATE["summary"] = str(payload.get("summary", "")).strip()
        facts = payload.get("facts", [])
        if isinstance(facts, list):
            MEMORY_STATE["facts"] = [str(f).strip() for f in facts if str(f).strip()][:MEMORY_FACTS_MAX_ITEMS]
        messages = payload.get("messages", [])
        return _conversation_messages(messages if isinstance(messages, list) else [])
    if isinstance(payload, list):
        return _conversation_messages(payload)
    return []

def _format_messages_for_summary(messages, max_chars=9000):
    lines = []
    used = 0
    for message in messages:
        role = message.get("role", "user")
        content = re.sub(r"\s+", " ", message.get("content", "")).strip()
        if not content:
            continue
        line = f"{role}: {content}"
        if len(line) > 700:
            line = line[:700] + "..."
        if used + len(line) > max_chars:
            break
        lines.append(line)
        used += len(line)
    return "\n".join(lines)

def _extract_json_object(text):
    text = text.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1)
    else:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start:end + 1]
    return json.loads(text)

def _fallback_memory_summary(older_messages):
    existing = MEMORY_STATE.get("summary", "").strip()
    compact = _format_messages_for_summary(older_messages, max_chars=2500)
    if not compact:
        return
    combined = f"{existing}\n\nOlder conversation notes:\n{compact}".strip()
    MEMORY_STATE["summary"] = combined[-MEMORY_SUMMARY_MAX_CHARS:]

def compress_memory(older_messages):
    if not older_messages:
        return
    transcript = _format_messages_for_summary(older_messages)
    if not transcript:
        return
    prompt = f"""Compress these older Jarvis conversation messages into long-term memory.

Existing summary:
{MEMORY_STATE.get("summary", "") or "(none)"}

Existing durable facts:
{json.dumps(MEMORY_STATE.get("facts", []), ensure_ascii=False)}

Older messages:
{transcript}

Return only JSON with this shape:
{{
  "summary": "short useful summary, max 250 words",
  "facts": ["durable user preference or project fact", "..."]
}}

Keep facts only if they will matter later. Do not keep throwaway chatter."""
    try:
        response = ollama.chat(
            model="qwen2.5-coder:7b",
            messages=[
                {"role": "system", "content": "You compress assistant memory into concise JSON."},
                {"role": "user", "content": prompt},
            ],
        )
        parsed = _extract_json_object(response["message"]["content"])
        summary = str(parsed.get("summary", "")).strip()
        facts = parsed.get("facts", [])
        if summary:
            MEMORY_STATE["summary"] = summary[:MEMORY_SUMMARY_MAX_CHARS]
        if isinstance(facts, list):
            cleaned_facts = []
            for fact in MEMORY_STATE.get("facts", []) + facts:
                fact = str(fact).strip()
                if fact and fact not in cleaned_facts:
                    cleaned_facts.append(fact)
            MEMORY_STATE["facts"] = cleaned_facts[:MEMORY_FACTS_MAX_ITEMS]
    except Exception as e:
        print(f"[Memory compression fallback: {e}]")
        _fallback_memory_summary(older_messages)

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            print("[Memory loaded]\n")
            return _compose_messages(_load_memory_payload(json.load(f)))
    reset_memory_state()
    return _compose_messages([])

def save_memory(messages):
    recent_messages = _conversation_messages(messages)
    payload = {
        "version": 2,
        "summary": MEMORY_STATE.get("summary", "").strip(),
        "facts": MEMORY_STATE.get("facts", [])[:MEMORY_FACTS_MAX_ITEMS],
        "messages": recent_messages,
    }
    with open(MEMORY_FILE, 'w') as f:
        json.dump(payload, f, indent=2)

def trim_memory(messages):
    """Compress older messages into long-term memory and keep recent raw chat."""
    recent_messages = _conversation_messages(messages)
    if len(recent_messages) > MAX_MEMORY_MESSAGES:
        older_messages = recent_messages[:-RECENT_MEMORY_MESSAGES]
        recent_messages = recent_messages[-RECENT_MEMORY_MESSAGES:]
        compress_memory(older_messages)
    return _compose_messages(recent_messages)

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
                    if all(k in parsed for k in ["recipient", "subject", "body"]):
                        input_val = f"{parsed['recipient']}, {parsed['subject']}, {parsed['body']}"
                        return ("tool", tool_name, input_val)
                    if "phone" in parsed and "message" in parsed:
                        input_val = f"{parsed['phone']}, {parsed['message']}"
                        return ("tool", tool_name, input_val)
                    for key in ["cmd", "text", "query", "app", "city", "level", "path"]:
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
    three_arg = {
        "create_email_draft": create_email_draft,
        "send_email": send_email,
    }
    if name in three_arg:
        parts = input_val.split(',', 2)
        if len(parts) == 3:
            return three_arg[name](parts[0].strip(), parts[1].strip(), parts[2].strip())
        return f"Error: {name} needs three inputs separated by commas"
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
            reset_memory_state()
            messages = _compose_messages([])
            save_memory(messages)
            print("[Memory cleared]\n")
            continue

        if user_input.lower() == "/tools":
            print(f"\nAvailable tools:\n{TOOLS_LIST}\n")
            continue

        if user_input.lower() in {"/memory", "/messages", "/message"}:
            memory_text = f"[{len(_conversation_messages(messages))} recent messages in memory]"
            if MEMORY_STATE.get("summary", "").strip() or MEMORY_STATE.get("facts"):
                memory_text += " + long-term summary"
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
        if not automation_needs_ai(fast_result):
            print(f"Jarvis: {fast_result}\n")
            if voice_mode:
                speak(fast_result)
            continue

        if fast_result is None:
            print("[Automation] No direct route. Asking AI...\n")
        else:
            print(f"[Automation] {fast_result}")
            print("[Automation] Asking AI to recover...\n")

        # --- Ollama fallback ---
        ai_input = build_ai_handoff_input(user_input, fast_result)
        answer = ollama_loop(ai_input, messages)
        messages = trim_memory(messages)
        save_memory(messages)
        print(f"Jarvis: {answer}\n")
        if voice_mode:
            speak(answer)


if __name__ == "__main__":
    main()
