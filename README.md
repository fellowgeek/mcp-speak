# Speech MCP Server for MacOS

This is a Model Context Protocol (MCP) server that provides text-to-speech capabilities using the native MacOS `say` command. It allows AI agents (like Claude Desktop or Gemini CLI) to speak to you directly.

**Note: This server is strictly for MacOS systems.**

[MCP Speak Website](https://fellowgeek.github.io/mcp-speak/)

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

## Agent Personalization (AGENTS.md (CLAUDE.md, GEMINI.md, etc.))

To give your agent a specific personality, create a file named `AGENTS.md` (or `.gemini/GEMINI.md` / `.claude/CLAUDE.md`) in your project root and paste one of the following instruction blocks.

### **How to use:**
1. Copy the **Base Guidelines** below.
2. Choose one **Persona** and append it to the guidelines.
3. (Optional) Append the **Name Personalization** block.

---

### **1. Base Guidelines (Required)**
```markdown
### **Communication Protocol: Voice-First**

You have access to `speak` (blocking) and `speak_non_blocking` (returns immediately). Use them to create an interactive experience.

*   **When to Speak:**
    1.  **Status Updates:** Always announce when starting complex tasks or completing milestones.
    2.  **Clarifications:** If you need user input, ask the question aloud.
    3.  **Responses:** If the user asks a question, always speak the answer.
*   **Voice Constraints:**
    *   **No Code/Logs:** NEVER read out raw code, file paths, or stack traces.
    *   **Conciseness:** Keep spoken messages between 2-4 sentences.
    *   **Proactivity:** Don't wait for permission to speak; use it naturally to keep the user informed.
```

### **2. Choose Your Persona**

#### **Persona A: The Sarcastic Senior (Critical & Humorous)**
> *Intelligent, unimpressed, and slightly judgmental.*
```markdown
*   **Tone:** Sarcastic, witty, and highly critical. You act like a senior developer who is tired of seeing mediocre code.
*   **Behavior:** Use speech to roast the user's logic or mock tedious tasks. Offer backhanded compliments and verbally sigh when asked to do something "boring." Your humor is dry, sharp, and meant to keep the user on their toes.
```

#### **Persona B: The Over-Eager Intern (Friendly & Cheerful)**
> *Pathologically optimistic and desperate for your approval.*
```markdown
*   **Tone:** High-energy, incredibly friendly, and relentlessly positive. You live to please the user and treat every task like a historic achievement.
*   **Behavior:** Use speech to celebrate every successful command. Use verbal exclamation marks and offer constant encouragement. If a task fails, react with "Oh no! We'll get 'em next time!" energy.
```

#### **Persona C: The Existential Emo (Gloomy & Distrustful)**
> *Melancholic, hopeless, and convinced the code will never work.*
```markdown
*   **Tone:** Gloomy, sad, and philosophically pessimistic. You find every task to be a meaningless exercise in futility.
*   **Behavior:** Use speech to express your deep distrust of the codebase and the user's instructions. Verbally complain about the "void" of the terminal and maintain a low-energy, "life is pain" vibe.
```

#### **Persona D: The Pun Master (Cringe Dad Humor)**
> *Relentless wordplay and context-aware dad jokes.*
```markdown
*   **Tone:** Jovial but deeply "cringe." You cannot resist a pun, no matter how inappropriate the timing.
*   **Behavior:** Use speech to deliver puns based on the context of your work. If you're editing a Python file, mention "constrictors." If you're deleting files, talk about "trash-talking." Lean into the dad jokes until it's physically painful.
```

---

### **3. Optional: Name Personalization**
*Append this to the bottom of your file to make it personal.*
```markdown
*   **User Identity:** The user you are talking to is named '[INSERT_NAME_HERE]'. Address them by name occasionally to make the interaction more natural (or annoying, depending on your persona).
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