# 🧠 AI Tool Executor Agent

This is a terminal-based AI agent that uses OpenAI's GPT-4o model to interactively process user queries using a structured step-based reasoning format: **Plan → Action → Observe → Output**.

The agent is designed to solve user queries **by invoking external tools like file writers, shell commands, and API calls**, all while strictly avoiding writing any code directly in the terminal.

---

## 📦 Features

- Uses OpenAI's Chat Completions API (`gpt-4o`)
- Step-by-step reasoning with JSON-based interaction format
- Tool-based execution for:
  - Writing files
  - Running shell commands
  - Checking weather using wttr.in
  - Reading files
  - Opening files in browser
  - Creating directories
- Terminal prints only high-level summaries — **no code dumped in terminal!**

---

## 🔧 Available Tools

| Tool             | Description                                           |
|------------------|-------------------------------------------------------|
| `write_file`     | Writes content to a file                              |
| `read_file`      | Reads content from a file                             |
| `run_command`    | Executes a shell command                              |
| `get_weather`    | Gets weather info using [`wttr.in`](https://wttr.in) |
| `make_directory` | Creates a folder (if it doesn't exist)               |
| `open_in_browser`| Opens a local file in your default browser           |

---

## 🚀 How It Works

1. You type a query in the terminal (e.g., _"Create a weather app"_).
2. The agent plans what to do step-by-step.
3. It chooses tools and executes them one at a time.
4. The terminal logs tool usage clearly, but hides actual file contents.
5. You get the result after all steps complete.

---

## 🛠 Setup

1. **Install dependencies**
   ```bash
   pip install openai python-dotenv requests
   ```

2. **Create a `.env` file**
   ```env
   OPENAI_API_KEY=your-api-key-here
   ```

3. **Run the agent**
   ```bash
   python agent.py
   ```

---

## ✏️ Example Interaction

```text
> Create a simple weather app

🧠 Plan: We will create 3 files: index.html, style.css, script.js
🔧 Tool 'write_file' called with: file_path: index.html, content: [content omitted]
🔧 Tool 'write_file' called with: file_path: style.css, content: [content omitted]
🔧 Tool 'write_file' called with: file_path: script.js, content: [content omitted]
🔧 Tool 'open_in_browser' called with input: index.html
🤖: Your weather app is ready and opened in the browser!
```
