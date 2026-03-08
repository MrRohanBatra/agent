from .time_tools import *
from .location_tools import *
from .weather_tools import *
from .web_tools import *
from .github_tools import *
from .file_tools import *
from .music_tools import play_music
from .sheel_tool import *

TOOLS=[
    read_file,
    write_to_file,
    list_directory,
    get_github_file_content,
    get_github_repo_info,
    get_repo_file_structure,
    search_code_in_repo,
    list_repo_issues,
    get_time_for_timezone,
    get_user_location,
    get_weather_from_coordinates,
    play_music,
    web_search,
    shell
]