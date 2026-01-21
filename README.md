# Speak MCP Server for MacOS

This is a Model Context Protocol (MCP) server that provides text-to-speech capabilities using the native MacOS `say` command. It allows AI agents (like Claude Desktop or Gemini CLI) to speak to you directly.

**Note: This server is strictly for MacOS systems.**

## Prerequisites

- MacOS
- Python 3 installed

## Installation

1.  Clone this repository or navigate to the project folder.
2.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

### 1. Gemini CLI

To use this with the Gemini CLI, edit your user settings file located at `~/.gemini/settings.json`.

Add your server under the `mcpServers` key:

```json
{
  "mcpServers": {
    "voice": {
      "command": "python3",
      "args": ["/ABSOLUTE/PATH/TO/speak_server.py"]
    }
  }
}
```
*Make sure to replace `/ABSOLUTE/PATH/TO/speak_server.py` with the actual full path to the file.*

### 2. Claude Desktop

To use this with Claude Desktop, edit your configuration file located at:
`~/Library/Application Support/Claude/claude_desktop_config.json`

Add the server configuration:

```json
{
  "mcpServers": {
    "voice": {
      "command": "python3",
      "args": ["/ABSOLUTE/PATH/TO/speak_server.py"]
    }
  }
}
```

### 3. Claude CLI (Claude Code)

If you are using Anthropic's **Claude Code** CLI, you can add the MCP server by running the following command in your terminal:

```bash
claude mcp add voice python3 -- /ABSOLUTE/PATH/TO/speak_server.py
```

Alternatively, you can manually add it to your global Claude CLI config file (usually `~/.claude/config.json`).

## Agent Personalization (`GEMINI.md` / `CLAUDE.md`)

To make the agent more conversational and utilize the voice tool effectively, add the following instructions to your project's context file (e.g., `GEMINI.md` or `CLAUDE.md`) or your custom instructions.

### Recommended Instruction Section:

```
### **Tool Usage: Speak**

You have access to a `speak` tool. Use it to create a more interactive and "voice-first" experience.

**When to Speak:**
1.  **Greetings & Status:** Briefly announce when you start a complex task or complete a milestone.
2.  **Questions:** If you need user input, ask the question aloud.
3.  **Short Explanations:** Provide concise verbal summaries of what you are doing.

**Guidelines:**
*   **Conversational Tone:** Be friendly and direct.
*   **No Code:** NEVER read out code blocks, file paths, raw data, or long logs.
*   **Conciseness:** Keep spoken messages short (1-2 sentences). The tool blocks until speech is finished.
*   **Proactive:** Don't wait to be asked to speak; use it naturally to keep the user informed.
```

## Optimizing Voice Quality

For the best experience, you should configure your Mac's text-to-speech settings to use a high-quality "Siri" or "Enhanced" voice.

1.  Open **System Settings**.
2.  Go to **Accessibility** > **Spoken Content**.
3.  Click on the **System Voice** dropdown.
4.  Select **"Manage Voices..."**.
5.  Look for **"Siri"** voices (e.g., Siri Voice 1, 2, 3, 4) or voices marked as **"Premium"** or **"Enhanced"**.
6.  Download and select one of these high-quality voices.
7.  Set it as your default **System Voice**.

*Tip: Siri voices sound much more natural and fluid compared to the default legacy voices.*