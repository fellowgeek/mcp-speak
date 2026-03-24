import subprocess
import queue
import threading
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MacOS-Voice")

# Thread-safe queue for speech requests
speech_queue = queue.Queue()

def speech_worker():
    """
    Worker thread that processes speech requests one by one.
    """
    while True:
        message, event = speech_queue.get()
        try:
            subprocess.run(["say", message], check=True)
        except Exception as e:
            # We can't easily return errors to the caller if it's non-blocking,
            # but we can log it.
            print(f"Error in speech worker: {str(e)}")
        finally:
            if event:
                event.set()
            speech_queue.task_done()

# Start the background worker thread
threading.Thread(target=speech_worker, daemon=True).start()

@mcp.tool()
def speak(message: str):
    """
    Speaks the provided message aloud using the macOS 'say' command.
    Blocking: returns only after the speech has finished.
    """
    event = threading.Event()
    speech_queue.put((message, event))
    
    # Wait for the worker thread to finish speaking this message
    event.wait()
    return f"Finished speaking: {message}"

@mcp.tool()
def speak_non_blocking(message: str):
    """
    Speaks the provided message aloud using the macOS 'say' command.
    Non-blocking: returns immediately after queuing the speech.
    """
    speech_queue.put((message, None))
    return f"Queued for speaking (non-blocking): {message}"

if __name__ == "__main__":
    mcp.run()
