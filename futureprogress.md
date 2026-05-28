# Jarvis Future Progress

Roadmap ideas that should be designed carefully before implementation.

## Goal Mode: Complete Tasks End-to-End

- Build a `/goal` mode where Jarvis works toward a final outcome, not just a single command.
- Make Jarvis create a plan, execute steps, observe results, retry failures, and keep going until the task is complete or blocked.
- Store goal state so long tasks can survive restarts and continue later.
- Add progress updates for every major step, including what was tried, what worked, what failed, and what is next.
- Add completion proof before Jarvis says a task is done, such as a saved file, confirmation number, screenshot, calendar event, or final report.
- Use existing tools first: browser automation, internet research, file writing, calendar, reminders, messages, and command execution.
- Add approval checkpoints before irreversible or sensitive actions, including payments, bookings, submissions, messages, emails, personal data sharing, or deleting files.
- Add a retry policy so Jarvis can try alternate paths instead of stopping after one failed attempt.
- Add a blocker policy so Jarvis asks only for the missing detail when it genuinely cannot continue.

## Examples

- Complete an assignment: read requirements, research, outline, draft, cite sources, create final file, ask for approval before submission.
- Book a restaurant reservation: search restaurants, check availability, try online booking, call if needed, confirm details, save proof.
- Research a purchase decision: collect sources, compare options, choose a winner, save report with bibliography.

## Voice Calling Layer

- Add a phone-call integration only after Goal Mode is stable.
- Use a calling provider, speech-to-text, text-to-speech, and a real-time conversation loop.
- Give Jarvis a call script, allowed facts, fallback responses, and a clear stop condition.
- Require approval before making calls that use the user's identity or personal details.
- Save call outcome, confirmation details, and any follow-up tasks.

## Design Notes

- Keep the system modular: planner, executor, verifier, memory, approvals, and tools should be separate pieces.
- Avoid one giant function that tries to do everything.
- Goal Mode should be persistent, inspectable, and resumable.
- "At any cost" should mean persistent and creative within safe limits, not unsafe, dishonest, or irreversible without approval.
