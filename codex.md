# Codex Project Notes

This repository is `Jarvis`, a personal AI assistant for macOS. It is currently a single-file Python agent in `main.py` that uses a local Ollama model as its brain and can control macOS, files, voice input/output, and a Playwright-driven browser.

## Current Shape

- Main entry point: `main.py`
- Project overview: `readme.txt`
- Small local test/context files: `test.txt`, `faheem.txt`
- Private runtime data is intentionally ignored: `memory.json`, `browser_profile/`, virtual environments, env/secrets files, Python cache, and macOS metadata.

`main.py` is about 926 lines and contains the full application:

- Tool functions for system info, Mac control, clipboard, files, browser automation, notifications, calendar/reminders, Spotify, Messages, and weather.
- A `TOOLS` registry mapping tool names to callable functions.
- A `SYSTEM_PROMPT` that instructs the model to respond using strict `TOOL:/INPUT:` or `ANSWER:` formats.
- Memory loading/saving via `memory.json`.
- Voice support using `SpeechRecognition`, PyAudio, Google speech recognition, and macOS `say`.
- Response parsing, tool execution, Ollama chat, and the interactive main loop.

## Runtime Behavior

The agent loop is:

1. User types or speaks a request.
2. The full conversation history is sent to the local LLM through `ollama.chat`.
3. The model returns either a tool call or a final answer.
4. `parse_response()` extracts `TOOL`, `INPUT`, or `ANSWER`.
5. `run_tool()` executes the requested function.
6. Tool results are appended back into the message history.
7. The loop allows up to 5 tool calls before a final answer.
8. Conversation memory is saved to `memory.json`.

The active model is `qwen2.5-coder:7b` through Ollama. The README notes that the brain could later be swapped to Gemini or another API by changing the chat function.

## Important Commands

Slash commands handled by the main loop:

- `/clear` clears conversation memory.
- `/tools` lists registered tools.
- `/memory` shows stored message count.
- `/voice` toggles voice mode.
- `/voice-test` diagnoses microphone setup.
- `exit` saves memory, closes the controlled browser, and quits.

Spoken commands are normalized in `normalized_command()`, so phrases like "memory", "show tools", "clear memory", and "voice off" map to slash commands.

## Tool Surface

System info:

- `get_time`, `get_battery`, `get_wifi`, `get_disk_space`, `get_ram_usage`, `get_cpu_usage`, `get_uptime`, `get_active_app`, `get_volume`, `get_brightness`

Mac control:

- `set_volume`, `set_brightness`, `open_app`, `quit_app`, `take_screenshot`, `lock_screen`, `sleep_mac`, `empty_trash`, `type_text`, `mute`, `unmute`

Clipboard and files:

- `read_clipboard`, `write_clipboard`
- `run_command`, `read_file`, `write_file`, `list_directory`, `create_folder`, `move_file`, `delete_file`, `get_file_info`

Browser:

- `open_url`, `get_current_tab`
- `browser_open`, `browser_read_page`, `browser_click`, `browser_type`, `browser_press`, `browser_screenshot`, `browser_close`
- Prefer `browser_open` over `open_url` because the Playwright browser can then be read and controlled.
- Browser profile path: `~/jarvis/browser_profile`
- Optional browser channel env var: `JARVIS_BROWSER_CHANNEL`

Integrations:

- `send_notification`
- `get_calendar_events`, `add_reminder`
- `music_play_pause`, `music_next`, `music_previous`, `get_current_song`
- `send_imessage`
- `get_weather` using `wttr.in`, defaulting to Chennai

## Dependencies

Core:

- `ollama`

Voice:

- `SpeechRecognition`
- `pyaudio`

Browser automation:

- `playwright`
- Chromium installed through Playwright

Optional future cloud brain:

- `google-genai`

The README says to install browser support with:

```bash
pip install playwright
playwright install chromium
```

## Development Notes For Future Codex

- Keep changes scoped. This repo is intentionally simple and currently centered on `main.py`.
- Do not touch ignored runtime/private data unless the user explicitly asks.
- Be careful with tool functions that execute shell commands or delete files. `delete_file()` uses `rm -rf`.
- Several functions build shell or AppleScript commands from strings, so quoting and injection risk matter if changing tool inputs.
- For browser work, maintain the controlled Playwright flow: open/read/click/type/press/screenshot/close.
- For multi-argument tools, `run_tool()` splits `INPUT` on the first comma. Preserve that contract unless also updating the prompt and parser.
- Memory is always refreshed with the current `SYSTEM_PROMPT` at startup.
- The future roadmap in `readme.txt` points toward modularizing into `brain.py`, `tools/`, `triggers/`, and `memory/`, but the current implementation is still single-file.

## Local Context Files

- `test.txt` contains `hello world`.
- `faheem.txt` contains a small Two Sum note: use a hash map to store values and indices, check each complement, return indices when found.

Last captured by Codex: 26 May 2026.
