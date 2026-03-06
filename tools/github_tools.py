from langchain.tools import tool
import requests
@tool
def get_github_repo_info(owner: str, repo: str) -> dict:
    """
    Get information about a GitHub repository.

    Use this tool when the user asks:
    - "How many stars does X repo have?"
    - "Show info about the React repo"
    - "Open issues in LangChain repo"
    - "Repository stats for owner/repo"

    Inputs:
        owner (str): GitHub username or organization name
        repo (str): Repository name

    Returns:
        dict containing:
            - name
            - description
            - stars
            - forks
            - open_issues
            - default_branch
            - url

        If repository not found:
            {"error": "Repository not found"}
    """

    url = f"https://api.github.com/repos/{owner}/{repo}"

    headers = {}

    # Optional: Use token if available
    token = ""
    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return {"error": "Repository not found"}

    data = response.json()

    return {
        "name": data["name"],
        "description": data["description"],
        "stars": data["stargazers_count"],
        "forks": data["forks_count"],
        "open_issues": data["open_issues_count"],
        "default_branch": data["default_branch"],
        "url": data["html_url"]
    }
import base64

@tool
def get_github_file_content(owner: str, repo: str, file_path: str) -> dict:
    """
    Read the content of a specific file in a GitHub repository.

    Use this tool when the user asks:
    - "Read the main.py file in langchain repo"
    - "What is in the requirements.txt?"
    - "Check the code in src/utils.js"

    Inputs:
        owner (str): GitHub username/org (e.g., "langchain-ai")
        repo (str): Repository name (e.g., "langchain")
        file_path (str): Path to the file (e.g., "libs/core/README.md")

    Returns:
        dict: content (decoded text), size, and download_url.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
    
    # AUTHENTICATION IS HIGHLY RECOMMENDED HERE
    headers = {
        "Accept": "application/vnd.github.v3+json",
        # "Authorization": "Bearer YOUR_GITHUB_TOKEN" 
    }

    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 404:
            return {"error": "File not found. Check the path."}
        
        data = response.json()
        
        if isinstance(data, list):
            return {"error": "Path points to a directory, not a file."}

        # GitHub API returns content as base64
        file_content = base64.b64decode(data["content"]).decode("utf-8")

        return {
            "path": data["path"],
            "size": data["size"],
            "content": file_content[:8000] # Truncate if too large for context window
        }
    except Exception as e:
        return {"error": str(e)}
@tool
def search_code_in_repo(owner: str, repo: str, query: str) -> dict:
    """
    Search for a specific keyword or code snippet inside a repository.

    Use this tool when the user asks:
    - "Where is the 'Calculator' class defined?"
    - "Find usages of 'api_key' in the repo"
    - "Search for 'TODO' comments"

    Inputs:
        owner (str): GitHub username
        repo (str): Repository name
        query (str): The term to search for

    Returns:
        list: A list of files and specific snippets where the code appears.
    """
    # GitHub Code Search Syntax: "query repo:owner/repo"
    search_query = f"{query} repo:{owner}/{repo}"
    url = "https://api.github.com/search/code"
    
    params = {"q": search_query, "per_page": 5}
    headers = {
        "Accept": "application/vnd.github.v3+json",
        # "Authorization": "Bearer YOUR_GITHUB_TOKEN"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        if "items" not in data:
            return {"error": data.get("message", "Search failed")}

        results = []
        for item in data["items"]:
            results.append({
                "file_name": item["name"],
                "path": item["path"],
                "html_url": item["html_url"]
            })
            
        return {"count": data["total_count"], "top_results": results}
    except Exception as e:
        return {"error": str(e)}

@tool
def list_repo_issues(owner: str, repo: str, state: str = "open") -> dict:
    """
    List issues or pull requests for a repository.

    Use this tool for:
    - "What are the open bugs in this project?"
    - "Show me the latest pull requests"
    - "Are there any issues about 'login'?"

    Inputs:
        owner (str): GitHub username
        repo (str): Repository name
        state (str): 'open', 'closed', or 'all' (default: 'open')

    Returns:
        list: Titles, numbers, and user info of issues.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    
    params = {
        "state": state,
        "sort": "updated",
        "direction": "desc",
        "per_page": 5
    }
    headers = {
        # "Authorization": "Bearer YOUR_GITHUB_TOKEN"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        if isinstance(data, dict) and "message" in data:
             return {"error": data["message"]}

        issues = []
        for issue in data:
            issues.append({
                "number": issue["number"],
                "title": issue["title"],
                "user": issue["user"]["login"],
                "is_pull_request": "pull_request" in issue,
                "url": issue["html_url"]
            })
            
        return {"repo": repo, "issues": issues}
    except Exception as e:
        return {"error": str(e)}
@tool
def get_repo_file_structure(owner: str, repo: str, path: str = "") -> dict:
    """
    List the files and folders in a specific directory of a repository.
    
    Use this tool to explore the file structure before reading a file.
    
    Inputs:
        owner (str): GitHub username
        repo (str): Repository name
        path (str): The subdirectory path (leave empty "" for root)
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {
        # "Authorization": "Bearer YOUR_GITHUB_TOKEN"
    }

    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        if isinstance(data, dict) and "message" in data:
             return {"error": data["message"]}

        structure = []
        for item in data:
            structure.append({
                "name": item["name"],
                "type": item["type"], # 'file' or 'dir'
                "path": item["path"]
            })
            
        return {"current_path": path, "contents": structure}
    except Exception as e:
        return {"error": str(e)}
