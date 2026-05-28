# Jarvis Progress Log

Use this file to record what improves in each working session.

## 2026-05-27

- Added an automation-to-AI fallback workflow in `maincodex.py`.
- Changed failed fast automation results, such as unclear commands or tool errors, so they escalate into the Ollama AI workflow instead of silently stopping.
- Added visible terminal handoff messages so it is clear when Jarvis moves from automation to AI recovery.
- Improved memory handling in `maincodex.py`.
- Replaced simple message-count trimming with structured memory: long-term summary, durable facts, and recent raw messages.
- Made old messages compress into a summary after the raw message limit is reached.
- Preserved compatibility with the old `memory.json` list format while saving future memory in the newer structured format.
- Updated `/memory` so it reports recent memory plus whether long-term memory exists.
- Updated `/clear` so it clears recent messages, long-term summary, and durable facts.
- Added an internet research workflow in `maincodex.py`.
- Made Jarvis able to search the web, read multiple sources, synthesize a Markdown research report, pick a final winner when requested, and save the report into `research_reports/`.
- Added bibliography enforcement so saved research reports include numbered source links.
- Added safe email and iMessage sharing workflows in `maincodex.py`.
- Made Jarvis able to draft emails, send approved emails/messages, and share the latest research report by email or iMessage.
- Added approval prompts before outgoing emails or messages are sent.
- Added a contact-email workflow for lead/contact lookup tasks.
- Made Jarvis able to scan company websites/contact pages for email addresses, save contact research notes, and send a short approved email to the first discovered address.
- Improved browser resilience when Playwright fails on macOS.
- Made `browser_open` fall back to the system browser and taught `browser_read_page` to fetch a URL directly when the controlled browser is unavailable.
- Verified the updated file with Python syntax checks.

## Session Note Template

- Improved:
- Reason:
- Verified:
- Follow-up:
