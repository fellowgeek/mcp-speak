import subprocess
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MacOS-Voice")

@mcp.tool()
def speak(message: str):
    """
    Speaks the provided message aloud using the macOS 'say' command.
    Non-blocking: returns immediately after starting the speech.
    """
    try:
        subprocess.Popen(["say", message])
        return f"Speaking (non-blocking): {message}"
    except Exception as e:
        return f"Error speaking: {str(e)}"

if __name__ == "__main__":
    mcp.run()
