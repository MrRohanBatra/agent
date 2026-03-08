import subprocess
from langchain.tools import tool

@tool
def shell(command: str) -> str:
    """
    Run a shell command on the local system.
    sudo commands are not allowed.
    """

    if "sudo" in command.lower():
        return "Error: sudo commands are not allowed."

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=20
        )

        output = result.stdout.strip()
        error = result.stderr.strip()

        if error:
            return f"Error:\n{error}"

        return output if output else "Command executed."

    except Exception as e:
        return f"Execution failed: {str(e)}"