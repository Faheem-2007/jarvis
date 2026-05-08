Here's the complete updated picture with sensors/cameras/microphones added:

What Jarvis Is
A personal AI agent that runs on your Mac. You talk to it in plain English, it decides what to do, uses tools to actually do it, and responds. The long term goal is a system that can control your entire Mac, react to the physical world around you through cameras, microphones and sensors, and automate everything from LeetCode to Gmail to smart home devices — all from a single brain.

What We Built Today
A working agent loop in /Users/faheem/jarvis/main.py. Here's what it currently does:

Takes your text input
Sends it to qwen3:14b running locally via Ollama
AI decides whether to use a tool or answer directly
If tool needed: runs it, feeds result back to AI, AI decides next step
Maintains memory across the conversation via a growing messages list
Three tools currently: run_command, read_file, write_file

What's working:

File creation and reading
Running any shell command
Opening Mac applications
Memory within a session (forgets on restart)

Known issues:

Slow — qwen3:14b is heavy
Sometimes calls the same tool twice before settling
Memory dies when you exit — nothing saved to disk


The Architecture (understand this deeply)
External triggers (mic, camera, sensor)
       ↓
You type OR Jarvis wakes automatically
       ↓
messages list (full conversation history)
       ↓
chat() — sends entire history to brain (qwen3 or Claude API)
       ↓
AI returns plain text
       ↓
parse_response() — detects TOOL: or ANSWER:
       ↓
if TOOL: → run_tool() executes the Python function
         → result added to messages
         → loop continues
if ANSWER: → print to screen, add to messages, wait for next input
This loop is the entire project. Every feature you add is just a new tool function or a new trigger. The loop never changes.

What Needs To Be Added (complete order)
Phase 1 — Core (after exams, week 1-2)

Claude API as brain — replaces qwen3. Faster, smarter, better tool calling. One function swap. Costs ~₹150-200/month at personal use.
Persistent memory — save messages to a JSON file on exit, load on startup. Jarvis remembers across sessions.
Clean open_app tool — dedicated function for launching Mac apps so Jarvis stops confusing "open file" with "read file contents."
Slash commands — /clear, /save, /model built into the input loop.

Phase 2 — Power tools (week 3-4)

Browser control via Playwright — Jarvis opens Chrome, navigates URLs, clicks buttons, reads page content.
LeetCode solver — Playwright opens the problem, reads it, AI generates solution, pastes and submits.
File system navigation — move, delete, rename, search files across your Mac.
Screenshot + vision — Jarvis takes a screenshot, sends it to Claude vision API, understands what's on screen and acts on it. This is how it navigates GUIs it can't control programmatically.

Phase 3 — Integrations (month 2)

Gmail + Google Calendar — read emails, draft replies, check schedule, set reminders.
Voice input — speak to Jarvis instead of typing. Whisper model running locally handles transcription. This is the bridge between you and the trigger system below.
Smart home — Home Assistant API if you have smart devices.

Phase 4 — Triggers and Sensors (month 2-3)
This is the part that makes Jarvis proactive instead of reactive. Right now Jarvis only acts when you type. Triggers make it act on its own when something happens in the physical world.

Wake word detection — Jarvis listens passively in the background via your Mac microphone. When it hears "Hey Jarvis" it activates and starts listening for your command. Library: pvporcupine (Porcupine wake word engine, runs locally, very lightweight).

python# how it works under the hood
import pvporcupine
import pyaudio

# porcupine listens to raw audio stream
# when it detects the wake word it returns a positive result
# your code then starts recording and sends to Whisper for transcription
# Whisper converts speech to text
# that text gets injected into the Jarvis agent loop as if you typed it

Continuous microphone monitoring — beyond wake word, Jarvis can listen for specific sounds. Loud noise, glass breaking, someone calling your name. Library: pyaudio for raw audio, a small classifier model to identify sounds.
Camera triggers — use your Mac webcam or an external USB camera. Two use cases:

Motion detection — Jarvis activates when it detects movement in frame. Library: opencv-python. Simple frame difference algorithm, no heavy model needed.
Face recognition — Jarvis recognizes you specifically and logs when you sit down at your desk, automatically pulling up your context. Library: face_recognition.
Visual understanding — capture a frame, send to Claude vision API, Jarvis describes what it sees and acts on it. Example: point camera at a whiteboard full of notes and say "summarize that."



python# motion detection skeleton
import cv2

def watch_camera(callback):
    cap = cv2.VideoCapture(0)  # 0 = built-in webcam
    ret, prev_frame = cap.read()
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    
    while True:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(prev_gray, gray)  # compare frames
        if diff.mean() > threshold:          # if enough changed
            callback("Motion detected")      # trigger Jarvis
        prev_gray = gray

External sensors via Raspberry Pi or Arduino — temperature, humidity, door/window open sensors, motion PIR sensors. These connect to your Mac via USB serial or over your local network and send events that trigger Jarvis. This is the full smart home layer.

python# serial sensor trigger skeleton
import serial

def watch_sensors(callback):
    ser = serial.Serial('/dev/ttyUSB0', 9600)  # Arduino connected via USB
    while True:
        line = ser.readline().decode().strip()
        if line == "MOTION":
            callback("Motion sensor triggered")
        elif line == "DOOR_OPEN":
            callback("Front door opened")

Scheduled triggers — Jarvis wakes up at specific times without any physical trigger. "Every morning at 8am, check my calendar and brief me." Uses Python's schedule library running in a background thread.

pythonimport schedule
import threading

def morning_brief():
    # inject this into Jarvis as if you typed it
    handle_input("Give me my morning briefing — check calendar and summarize today")

schedule.every().day.at("08:00").do(morning_brief)

# run scheduler in background thread so it doesn't block the main loop
threading.Thread(target=schedule.run_pending, daemon=True).start()

The Trigger Architecture
When you add all these triggers the main loop needs to change slightly. Instead of only input() waiting for you to type, Jarvis needs to accept input from multiple sources simultaneously:
Microphone (wake word) ──┐
Camera (motion/face) ────┤──→ input queue ──→ agent loop ──→ tools ──→ action
Sensors (Arduino/Pi) ────┤
Scheduler (time-based) ──┤
You typing ──────────────┘
All triggers push events into a single queue. The agent loop pulls from that queue. This way it doesn't matter where the trigger came from — Jarvis handles it the same way.
pythonimport queue
import threading

input_queue = queue.Queue()

# each trigger runs in its own thread and puts events in the queue
def mic_thread():
    # wake word detection loop
    while True:
        if wake_word_detected():
            text = transcribe_speech()
            input_queue.put(text)

def camera_thread():
    while True:
        if motion_detected():
            input_queue.put("Motion detected in camera")

# main loop pulls from queue instead of input()
while True:
    user_input = input_queue.get()  # blocks until something arrives
    messages.append({"role": "user", "content": user_input})
    # rest of agent loop unchanged

What Needs To Change In Current Code
The chat() function after exams:
pythonimport anthropic

client = anthropic.Anthropic(api_key="your-key")

def chat(messages):
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=messages
    )
    return response.content[0].text
Persistent memory:
pythonimport os

MEMORY_FILE = "memory.json"

if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, 'r') as f:
        messages = json.load(f)
else:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# on exit
with open(MEMORY_FILE, 'w') as f:
    json.dump(messages, f)

Complete Tech Stack
LayerTechnologyPurposeBrainClaude API (after exams) / qwen3 (now)reasoning and decisionsAgent loopPythonorchestrationMac controlsubprocess + AppleScriptopen apps, run commandsBrowserPlaywrightweb automation, LeetCodeMemory (short)JSON filepersist conversationsMemory (long)ChromaDBvector search over historyVoice inputWhisper (local)speech to textWake wordPorcupinealways-on triggerCameraOpenCVmotion, face detectionVisionClaude vision APIunderstand what camera seesSensorsPySerial + Arduino/Piphysical world triggersSchedulerschedule librarytime-based triggersIntegrationsGoogle APIGmail, CalendarSmart homeHome Assistant APIlights, locks, devices

Current File Structure
/Users/faheem/jarvis/
├── main.py          ← entire agent (what we built today)
├── test.txt         ← test file
├── faheem.txt       ← test file
└── venv/            ← python environment
After exams target structure:
/Users/faheem/jarvis/
├── main.py              ← entry point + main loop
├── brain.py             ← Claude API chat function
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
│   ├── conversation.json ← persistent chat history
│   └── vector_store/    ← ChromaDB files
└── venv/

Save this. Come back after exams and we build it piece by piece in exactly this order. Phase 1 is two focused days of work. By end of summer Jarvis is a genuinely powerful system.
#5th april 2026
dependencies yet to be downloaded pip install anthropic playwright beautifulsoup4
playwright install chromium pip install anthropic playwright openai-whisper pvporcupine pyaudio opencv-python face_recognition pyserial schedule google-api-python-client
and more