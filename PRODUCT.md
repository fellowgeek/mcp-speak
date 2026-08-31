# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Primary users are AI engineers, software developers, and power users building and running agentic coding workflows (e.g., using Google Antigravity, Claude Code, Claude Desktop, Cursor, Windsurf, or Codex) on macOS. They want clear, real-time auditory status updates, milestone announcements, and persona-driven feedback without having to constantly shift visual focus or read dense terminal logs during pairing sessions.

## Product Purpose

Provide an MCP-native text-to-speech server that enables AI agents to communicate verbally using persona-tailored voices. The server transforms AI interactions from purely text-based output into an interactive pairing experience with neural voice design, zero reference audio requirements, and reliable native macOS speech fallback.

## Positioning

Unlike generic TTS bridges or heavy remote voice APIs, MCP Speak runs locally on macOS (with Apple Silicon MPS acceleration via OmniVoice) with strict sequential FIFO queuing, sub-second latency, and zero required reference audio. It provides an immediate plug-and-play Model Context Protocol interface and automated agent instruction generation.

## Operating Context

- macOS environments with Apple Silicon (M-series) running local agentic workflows.
- IDEs and agent runtimes supporting MCP: Google Antigravity (AGY), Claude Desktop / CLI, Cursor, Windsurf, and Codex.
- Paired coding sessions where agents proactively announce progress, ask clarifying questions, and deliver feedback via `speak` and `speak_non_blocking` tools.
- Web documentation, showcase, and prompt generator hosted at GitHub Pages (`index.html`).

## Capabilities and Constraints

- **Capabilities:**
  - Zero-shot neural voice cloning from reference audio recordings in `voices/` (`.wav` with optional `.txt` transcript).
  - Prompt-based neural voice design using OmniVoice with custom timbre, pitch, speed, and accents when reference audio is omitted.
  - Native macOS `say` fallback engine for high reliability when neural dependencies are absent.
  - Asynchronous, non-overlapping FIFO audio queue for `speak_non_blocking` tool calls.
  - Synchronous execution support via `speak` tool.
  - Interactive CLI setup wizard (`setup.py`) configuring client MCP settings and generating agent instruction files (`AGENTS.md`, `GEMINI.md`, `CLAUDE.md`, `.cursorrules`).
  - Standalone web documentation and configuration builder (`index.html`).
- **Constraints:**
  - Designed specifically for macOS with Apple Silicon MPS acceleration for OmniVoice.
  - Requires Python 3.12+ environment provisioned through `run.sh`.

## Brand Commitments

- **Name:** Speak MCP / `mcp-speak`.
- **Persona Catalog:** Curated set of distinct agent personalities (e.g., Agent Smith, Sarcastic Senior, Over-Eager Intern, Neutral Mainframe, Pun Master, Tech Priest, Nature Narrator, Poet, Head Chef, Existential Emo).
- **Style:** Clean, dark-mode terminal and glassmorphic developer aesthetic across documentation and web surfaces.

## Evidence on Hand

- Core MCP server implementation in [`speak_server.py`](speak_server.py).
- Web showcase and interactive generator in [`index.html`](index.html).
- Persona definitions and guidelines in [`personas/`](personas/).
- Interactive setup script in [`setup.py`](setup.py).
- Shell bootstrapper in [`run.sh`](run.sh).

## Product Principles

1. **Voice-First Utility:** Spoken audio must enhance situational awareness during developer workflows without obstructing coding velocity or demanding screen focus.
2. **Personality-Driven Immersion:** AI personas should possess consistent, recognizable vocal identities tailored to their operational roles.
3. **Zero-Friction Integration:** Configuring the MCP server and generating multi-agent instructions across any supported IDE must be automated and turn-key.
4. **Resilient Reliability:** Audio output failures or missing neural model files must gracefully degrade to native system speech without crashing agent tasks.

## Accessibility & Inclusion

- Audio feedback serves as an assistive layer for multitasking and visual fatigue reduction.
- Web interface must support WCAG contrast guidelines, dark/light modes, keyboard navigation, and clear typographic hierarchy.
