import os
from langchain.tools import tool
@tool
def read_file(file_path: str) -> dict:
    """
    Read the contents of a file from the local file system.

    Use this tool when you need to:
    - "Read the contents of config.yaml"
    - "Check what is inside notes.txt"
    - "Cat the file main.py"

    Input:
        file_path (str): The absolute or relative path to the file.

    Returns:
        dict: The file content or an error message.
    """
    if not os.path.exists(file_path):
        return {"error": f"File '{file_path}' does not exist."}

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"file_path": file_path, "content": content}
    except Exception as e:
        return {"error": f"Failed to read file: {str(e)}"}
@tool
def write_to_file(file_path: str, content: str) -> dict:
    """
    Write text to a file. If the file exists, it overwrites it. If not, it creates it.

    Use this tool when you need to:
    - "Save this code to script.py"
    - "Create a new file called README.md"
    - "Write the summary to notes.txt"

    Inputs:
        file_path (str): The path where the file should be saved.
        content (str): The text content to write to the file.

    Returns:
        dict: Confirmation message.
    """
    try:
        # Ensure the directory exists
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return {"success": True, "message": f"Successfully wrote to {file_path}"}
    except Exception as e:
        return {"error": f"Failed to write file: {str(e)}"}
    
@tool
def list_directory(directory: str = ".") -> dict:
    """
    List all files and folders in a specific directory.

    Use this tool when you need to:
    - "See what files are in the current folder"
    - "List contents of the /logs directory"
    - "Check if a file exists"

    Input:
        directory (str): The path to list (defaults to current directory ".")

    Returns:
        list: A list of filenames in that directory.
    """
    try:
        files = os.listdir(directory)
        return {"directory": directory, "files": files}
    except Exception as e:
        return {"error": f"Failed to list directory: {str(e)}"}
    