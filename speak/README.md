You need to tell the Gemini CLI to look for this server. Edit your user settings file located at ~/.gemini/settings.json.

Add your server under the mcpServers key:

```
{
  "mcpServers": {
    "voice": {
      "command": "python3",
      "args": ["/Users/YOUR_USERNAME/scripts/speak_server.py"]
    }
  }
}
```

Teaching the Agent "When" to Speak:

To ensure it follows your rules (avoiding code blocks, focusing on task updates), you should add instructions to your **`GEMINI.md`** file (usually located in your project root or `~/.gemini/GEMINI.md`).

Add this section:

> ### **Tool Usage: Speak**
> 
> 
> * **Enablement:** Use the `speak` tool when specifically requested and/or to provide high-level status updates.
> * **Content:** Only speak conversational items, next steps, or questions.
> * **Restriction:** NEVER use the `speak` tool to read back code blocks, stack traces, or raw data.
> * **Behavior:** The tool blocks until speech is finished; keep messages concise.
> 


