from langchain_core.tools import tool
import requests
from langchain.tools import tool
from datetime import datetime
from zoneinfo import ZoneInfo

@tool
def get_time_for_timezone(timezone: str) -> dict:
    """
    Get the current local time for a specific IANA timezone.

    Use this tool when the user asks:
    - "What time is it in Tokyo?"
    - "Current time in London"
    - "Time in New York"
    - "Clock in Dubai"

    Input:
        timezone (str): Valid IANA timezone name
                        (e.g., "Asia/Kolkata", "America/New_York")

    Returns:
        dict: {
            "timezone": str,
            "current_time": str (ISO format),
            "formatted_time": str (human-readable)
        }

    If timezone is invalid:
        dict: {"error": "Invalid timezone"}
    """

    try:
        now = datetime.now(ZoneInfo(timezone))
        return {
            "timezone": timezone,
            "current_time": now.isoformat(),
            "formatted_time": now.strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception:
        return {"error": "Invalid timezone"}
@tool
def get_user_location():
    """
Get the user's current approximate location using their public IP address.

Call this tool whenever the user refers to:
- "my location"
- "current location"
- "near me"
- "around me"
- "weather here"

Returns latitude and longitude that can be passed to other tools
such as weather or nearby search APIs.
    """
    resp=requests.get("http://ip-api.com/json")
    return resp.json()

@tool
def get_weather_from_coordinates(latitude:float,longitude:float):
    """
    Get the current weather for a specific location using latitude and longitude.

    Use this tool whenever the user asks about:
    - Current weather
    - Temperature
    - Rain conditions
    - Wind speed
    - Humidity
    - Weather forecast for their current location

    The function returns structured weather data that can be used
    to generate a natural language weather response.

    Inputs:
        latitude (float): GPS latitude
        longitude (float): GPS longitude

    Output:
        JSON dictionary containing current weather details.
    """
    
    api="cb6b65b6dc8c47cb9bf124135230111" #weatherapi.com
    url = "http://api.weatherapi.com/v1/current.json"

    params = {
        "key": api,
        "q": f"{latitude},{longitude}"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        return {
            "location": data["location"]["name"],
            "region": data["location"]["region"],
            "country": data["location"]["country"],
            "temperature_c": data["current"]["temp_c"],
            "condition": data["current"]["condition"]["text"],
            "humidity": data["current"]["humidity"],
            "wind_kph": data["current"]["wind_kph"]
        }

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
    
@tool
def web_search(query: str) -> dict:
    """
    Search the web for up-to-date information.

    Use this tool when:
    - The user asks about recent events
    - The user asks factual questions not in memory
    - You need real-time or external knowledge
    - The answer cannot be determined locally

    Input:
        query (str): Search query

    Returns:
        dict containing:
            - heading
            - abstract
            - source
            - related_topics (list of titles + links)
    """

    url = "https://api.duckduckgo.com/"
    params = {
        "q": query,
        "format": "json",
        "no_redirect": 1,
        "no_html": 1,
        "skip_disambig": 1
    }

    response = requests.get(url, params=params)
    data = response.json()

    return {
        "heading": data.get("Heading"),
        "abstract": data.get("AbstractText"),
        "source": data.get("AbstractSource"),
        "related_topics": [
            {
                "text": topic.get("Text"),
                "first_url": topic.get("FirstURL")
            }
            for topic in data.get("RelatedTopics", [])[:5]
            if isinstance(topic, dict)
        ]
    }
@tool
def get_wikipedia_summary(article_title: str) -> dict:
    """
    Get the summary of a Wikipedia article.

    Use this tool when the user asks:
    - "Who is [Person]?"
    - "What is the history of [Event]?"
    - "Define [Scientific Term]"
    - "Summary of [Movie/Book]"

    Input:
        article_title (str): The specific topic to search for (e.g., "Albert Einstein", "Python_(programming_language)")

    Returns:
        dict: Title, summary extract, and URL.
    """
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{article_title}"
    
    try:
        response = requests.get(url)
        if response.status_code == 404:
            return {"error": "Page not found. Try a different variation of the title."}
        
        data = response.json()
        
        # Handle disambiguation pages
        if data.get("type") == "disambiguation":
            return {"error": "Topic is ambiguous. Please be more specific."}

        return {
            "title": data.get("title"),
            "summary": data.get("extract"),
            "url": data.get("content_urls", {}).get("desktop", {}).get("page")
        }
    except Exception as e:
        return {"error": f"Failed to fetch wikipedia data: {str(e)}"}
@tool
def convert_currency(amount: float, from_currency: str, to_currency: str) -> dict:
    """
    Convert a specific amount of money from one currency to another.

    Use this tool for:
    - "How much is 100 USD in EUR?"
    - "Convert 5000 JPY to GBP"
    - "Price in local currency"

    Inputs:
        amount (float): The amount of money to convert
        from_currency (str): The 3-letter currency code (e.g., "USD")
        to_currency (str): The 3-letter currency code (e.g., "EUR")

    Returns:
        dict: Converted amount and exchange rate.
    """
    # Using a free public API for exchange rates
    url = f"https://api.exchangerate-api.com/v4/latest/{from_currency.upper()}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        rates = data.get("rates", {})
        target_rate = rates.get(to_currency.upper())

        if not target_rate:
            return {"error": f"Currency {to_currency} not supported."}

        converted_amount = amount * target_rate
        
        return {
            "from": from_currency.upper(),
            "to": to_currency.upper(),
            "original_amount": amount,
            "converted_amount": round(converted_amount, 2),
            "exchange_rate": target_rate
        }
    except Exception as e:
        return {"error": f"Currency conversion failed: {str(e)}"}
from bs4 import BeautifulSoup
import math

@tool
def calculate_expression(expression: str) -> dict:
    """
    Evaluate a mathematical expression safely.

    Use this tool for:
    - "Calculate 15% of 1500"
    - "What is the square root of 144?"
    - "50 * 24 + 10"

    Input:
        expression (str): A python-syntax math expression (e.g., "12 * 5", "math.sqrt(16)")

    Returns:
        dict: result of the calculation
    """
    # Define a safe global dictionary with math functions
    safe_dict = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
    
    try:
        # Evaluate using only safe math functions, no external access
        result = eval(expression, {"__builtins__": None}, safe_dict)
        return {"expression": expression, "result": result}
    except Exception as e:
        return {"error": "Invalid math expression. Use standard Python syntax (e.g., 2 + 2, math.sqrt(9))."}

@tool
def scrape_website_text(url: str) -> dict:
    """
    Scrape and extract the visible text content from a specific website URL.

    Use this tool when:
    - The user provides a link and asks "Summarize this article"
    - The user asks "What does this page say?"
    - You need more details than a web search snippet provides

    Input:
        url (str): The full URL of the website to read.

    Returns:
        dict: title, text_content (truncated to 4000 chars to fit context windows)
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Kill all script and style elements
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()

        text = soup.get_text()

        # Break into lines and remove leading/trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)

        return {
            "url": url,
            "title": soup.title.string if soup.title else "No Title",
            "content": text[:4000] + "..." if len(text) > 4000 else text
        }
    except Exception as e:
        return {"error": f"Could not read website: {str(e)}"}
    
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
import os

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
    