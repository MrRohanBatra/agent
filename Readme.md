# 🤖 Qwen Local AI Agent

A conversational AI agent powered by **Qwen** (via Ollama) with persistent memory, voice output, and a rich set of integrated tools. The agent runs fully locally, remembers user preferences across sessions, and can interact with the web, GitHub, Spotify, the local filesystem, and more.

---

## ✨ Features

- 🧠 **Persistent Memory** — Remembers user preferences, profile, and context across sessions using a JSON-based memory store
- 🗣️ **Text-to-Speech** — Speaks responses aloud using Piper TTS (`en_US-lessac-medium`)
- 🔧 **Tool-Calling Agent** — Automatically selects and invokes the right tool based on the user's message
- 📜 **Conversation History** — Maintains a rolling window of the last 50 messages for contextual responses
- 💾 **Multi-User Support** — Each user has an isolated memory profile stored in `memory_new.json`
- 📝 **Conversation Logging** — Saves all exchanges to `conversation.md` with timestamps

---

## 🛠️ Available Tools

| Tool | Description |
|------|-------------|
| `get_time_for_timezone` | Get current local time for any timezone |
| `get_user_location` | Detect user's approximate location via IP |
| `get_weather_from_coordinates` | Fetch current weather using lat/lon |
| `web_search` | Search the web using Tavily AI |
| `get_github_repo_info` | Get stars, forks, and issues for a GitHub repo |
| `get_github_file_content` | Read a specific file from a GitHub repository |
| `get_repo_file_structure` | Browse a repo's directory structure |
| `search_code_in_repo` | Search for code or keywords in a GitHub repo |
| `list_repo_issues` | List open/closed issues from a GitHub repo |
| `read_file` | Read a local file from the filesystem |
| `write_to_file` | Write or create a local file |
| `list_directory` | List contents of a local directory |
| `play_music` | Search and play music on Spotify |
| `shell` | Execute shell commands (sudo not allowed) |
| `update_memory` | Store structured user memory (called automatically) |

---

## 📁 Project Structure

```

├── Readme.md           
├── agent.log
├── agent.py
├── agent_file
├── agent_with_audio.py
├── agent_with_stream.py # main execute file
├── audio
│   ├── out.wav
│   ├── speak.py
│   └── voices
│       ├── en_US-lessac-medium.onnx
│       └── en_US-lessac-medium.onnx.json
├── conversation.md
├── gui.py
├── index.html
├── memory.json
├── memory_new.json
├── music_player.py
├── music_tool.py
├── report.txt
├── requirements.txt
├── spotify_token.json
├── tools
│   ├── __init__.py
│   ├── file_tools.py
│   ├── github_tools.py
│   ├── location_tools.py
│   ├── music_tools.py
│   ├── sheel_tool.py
│   ├── time_tools.py
│   ├── weather_tools.py
│   └── web_tools.py
├── tools_old.py
└── try.py

8 directories, 50 files

```

---

## ⚙️ Installation

### 1. Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com/) installed and running
- Spotify Premium account (for music playback)
- [Piper TTS](https://github.com/rhasspy/piper) installed

### 2. Pull the Qwen model

```bash
ollama pull qwen3.5:2b
```

### 3. Install Python dependencies

```bash
pip install langchain langchain-ollama langchain-core spotipy tavily-python requests sounddevice numpy piper-tts
```

### 4. Download Piper Voice Model

Place the following files in `audio/voices/`:
- `en_US-lessac-medium.onnx`
- `en_US-lessac-medium.onnx.json`

Download from the [Piper releases page](https://github.com/rhasspy/piper/releases).

### 5. Configure API Keys

Update the following in the source files:

| File | Variable | Service |
|------|----------|---------|
| `tools/weather_tools.py` | `api` | [WeatherAPI](https://www.weatherapi.com/) key |
| `tools/web_tools.py` | `api_key` | [Tavily](https://tavily.com/) API key |
| `tools/music_tools.py` | `client_id`, `client_secret` | [Spotify Developer](https://developer.spotify.com/) app credentials |

---

## 🚀 Usage

```bash
python agent.py
```

On startup, you'll be prompted to enter a username. The agent then loads your memory profile and begins the conversation loop.

```
Enter Username: rohan
🤖 Agent initialized. Type 'exit' to quit.
📊 Keeping last 50 messages in history
--------------------------------------------------
You-> What's the weather like here?
Agent: It's currently 31°C and partly cloudy in Delhi.
```

Type `exit` to quit.

---

## 🧠 Memory System

The agent automatically saves information about you as you chat. Memory is organized into three sections:

- **`user_profile`** — Name, GitHub username, and other identity info
- **`preferences`** — Likes, dislikes, and working style preferences
- **`other`** — Current tasks, environment details, and temporary context

Memory is stored per-user in `memory_new.json` and injected into every prompt as context.

---

## 📦 Dependencies Summary

| Package | Purpose |
|---------|---------|
| `langchain` | Agent framework and tool abstraction |
| `langchain-ollama` | Ollama LLM integration |
| `ollama` (qwen3.5:2b) | Local LLM inference |
| `spotipy` | Spotify Web API client |
| `tavily-python` | Web search |
| `requests` | HTTP calls (weather, GitHub, location) |
| `piper-tts` | Text-to-speech synthesis |
| `sounddevice` | Audio playback |
| `numpy` | Audio buffer handling |

---

## 📝 License

This project is for personal/educational use. Make sure to comply with the terms of service for Spotify, GitHub, WeatherAPI, and Tavily when deploying.