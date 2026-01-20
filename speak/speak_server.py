import subprocess
import sys
from mcp.server.fastmcp import FastMCP

# Initialize the MCP Server
mcp = FastMCP("MacOS-Voice")

@mcp.tool()
def speak(message: str):
    """
    Speaks the provided message aloud using the macOS 'say' command.
    Use this to announce high level commentary, completed tasks, next steps, or ask questions.
    Do NOT use this for code blocks or technical data.
    """
    try:
        # This call waits until the 'say' command finishes
        subprocess.run(["say", message], check=True)
        return f"Successfully spoke: {message}"
    except Exception as e:
        return f"Error speaking: {str(e)}"

if __name__ == "__main__":
    mcp.run()
