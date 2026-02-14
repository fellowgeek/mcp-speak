import subprocess
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MacOS-Voice")

@mcp.tool()
def speak(message: str):
    """
    Speaks the provided message aloud using the macOS 'say' command.
    Blocking: returns only after the speech has finished.
    """
    try:
        subprocess.run(["say", message], check=True)
        return f"Finished speaking: {message}"
    except Exception as e:
        return f"Error speaking: {str(e)}"

@mcp.tool()
def speak_non_blocking(message: str):
    """
    Speaks the provided message aloud using the macOS 'say' command.
    Non-blocking: returns immediately after starting the speech.
    """
    try:
        subprocess.Popen(["say", message])
        return f"Started speaking (non-blocking): {message}"
    except Exception as e:
        return f"Error speaking: {str(e)}"

if __name__ == "__main__":
    mcp.run()
