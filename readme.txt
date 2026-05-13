Jarvis — Personal AI Assistant for Mac
=======================================

What Jarvis Is
--------------
A personal AI agent that runs on your Mac. You talk to it in plain English (text or voice),
it decides what to do, uses tools to actually do it, and responds. The long-term goal is a
system that can control your entire Mac, react to the physical world through cameras,
microphones and sensors, and automate everything from LeetCode to Gmail to smart home
devices — all from a single brain.


Current Status (May 2026)
-------------------------
Jarvis has grown from a 3-tool prototype into a fully working agent with 40+ tools,
voice input/output, persistent memory, and full browser automation. Everything runs
from a single file: main.py (~930 lines).


What's Working
--------------

Brain & Agent Loop:
  - LLM brain via Ollama (qwen2.5-coder:7b running locally)
  - Can be swapped to Gemini API with a single function change
  - Agent loop: user input → LLM decides → tool or answer → loop
  - Up to 5 tool calls per turn before final answer
  - TOOL:/INPUT:/ANSWER: response format with robust parsing

Persistent Memory:
  - Conversation history saved to memory.json on exit
  - Loaded on startup — Jarvis remembers across sessions
  - /clear command to wipe and start fresh

Voice Input & Output:
  - Speech-to-text via Google Speech Recognition (SpeechRecognition + PyAudio)
  - Text-to-speech via Mac's built-in "say" command
  - Toggle with /voice command
  - Microphone auto-detection (prefers MacBook built-in mic)
  - Spoken commands normalized to slash commands (e.g. "memory" → /memory)
  - /voice-test to diagnose mic issues

System Info Tools (9):
  - get_time — current date and time
  - get_battery — battery level and charging status
  - get_wifi — connected network and IP address
  - get_disk_space — disk usage
  - get_ram_usage — memory pressure
  - get_cpu_usage — CPU load
  - get_uptime — system uptime
  - get_active_app — currently focused application
  - get_volume / get_brightness — audio and display levels

Mac Control Tools (10):
  - set_volume / set_brightness — adjust levels
  - open_app / quit_app — launch and close applications
  - take_screenshot — capture screen to file
  - lock_screen / sleep_mac — security and power
  - empty_trash — clear Finder trash
  - type_text — simulate keyboard input
  - mute / unmute — audio toggle

Clipboard Tools (2):
  - read_clipboard — read from pasteboard
  - write_clipboard — copy text to pasteboard

File System Tools (7):
  - run_command — execute any shell command
  - read_file / write_file — read and write files
  - list_directory — list directory contents
  - create_folder — make directories
  - move_file / delete_file — move and remove files
  - get_file_info — file metadata via stat

Browser Control via Playwright (8):
  - browser_open — navigate to any URL (with shortcut support: "youtube", "google", etc.)
  - browser_read_page — extract visible text from current page
  - browser_click — click elements by visible text or CSS selector
  - browser_type — type into form fields (search boxes, inputs)
  - browser_press — press keyboard keys (Enter, Tab, etc.)
  - browser_screenshot — capture full-page screenshot
  - browser_close — close the controlled browser
  - Persistent browser profile saved in browser_profile/

Integration Tools (7):
  - get_calendar_events — today's Calendar events via AppleScript
  - add_reminder — add to Reminders app
  - music_play_pause / music_next / music_previous — Spotify control
  - get_current_song — currently playing track from Spotify
  - send_imessage — send iMessage to a phone number
  - send_notification — macOS notification via AppleScript
  - get_weather — weather via wttr.in (default: Chennai)

Slash Commands:
  - /clear — wipe conversation memory
  - /tools — list all available tools
  - /memory — show number of stored messages
  - /voice — toggle voice input/output mode
  - /voice-test — test microphone setup
  - exit — save memory and quit


The Architecture
----------------

  You type or speak
         ↓
  messages list (full conversation history)
         ↓
  chat() — sends entire history to LLM brain
         ↓
  AI returns plain text
         ↓
  parse_response() — detects TOOL: or ANSWER:
         ↓
  if TOOL: → run_tool() executes the Python function
           → result added to messages
           → loop continues (up to 5 iterations)
  if ANSWER: → print to screen, speak if voice mode, save memory

This loop is the entire project. Every feature is just a new tool function.
The loop itself never changes.


File Structure
--------------

  /Users/faheem/jarvis/
  ├── main.py              ← entire agent (~930 lines)
  ├── memory.json          ← persistent conversation history (gitignored)
  ├── browser_profile/     ← Playwright browser session data (gitignored)
  ├── readme.txt           ← this file
  ├── faheem.txt           ← test file
  ├── test.txt             ← test file
  ├── .gitignore           ← excludes private data from git
  └── venv/                ← Python virtual environment (gitignored)


Dependencies
------------

  Core:
    pip install ollama

  Voice:
    pip install SpeechRecognition pyaudio

  Browser automation:
    pip install playwright
    playwright install chromium

  For Gemini API brain (optional swap):
    pip install google-genai


Future Roadmap
--------------

Phase 1 — Brain Upgrade:
  - Swap to cloud API (Gemini or Claude) as primary brain for faster, smarter responses
  - Add error handling and retry logic for API rate limits
  - Modularize main.py into separate files (brain.py, tools/, triggers/)

Phase 2 — Power Tools:
  - LeetCode solver — Playwright opens problem, AI generates solution, pastes and submits
  - Screenshot + vision — send screenshots to vision API, understand what's on screen
  - Enhanced file search across the Mac

Phase 3 — Integrations:
  - Gmail + Google Calendar via Google API
  - Smart home control via Home Assistant API

Phase 4 — Triggers and Sensors:
  - Wake word detection ("Hey Jarvis") via Porcupine
  - Camera motion/face detection via OpenCV
  - External sensors via Arduino/Raspberry Pi (serial)
  - Scheduled triggers (morning briefings, reminders)
  - All triggers feed into a unified input queue

Target modular structure:

  /Users/faheem/jarvis/
  ├── main.py              ← entry point + main loop
  ├── brain.py             ← LLM API chat function
  ├── tools/
  │   ├── mac_control.py   ← open apps, run commands
  │   ├── browser.py       ← Playwright automation
  │   ├── files.py         ← file operations
  │   └── integrations.py  ← Gmail, Calendar
  ├── triggers/
  │   ├── microphone.py    ← wake word + voice input
  │   ├── camera.py        ← motion, face detection
  │   └── scheduler.py     ← time-based triggers
  ├── memory/
  │   ├── conversation.json
  │   └── vector_store/    ← ChromaDB for long-term memory
  └── venv/


Last updated: 11th May 2026, 10:06 PM IST
Last updated: 14th May 2026