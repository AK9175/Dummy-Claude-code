# Dummy Claude Code

A CLI coding agent built from scratch as part of the [Build Your Own Claude Code](https://codecrafters.io/challenges/claude-code) challenge on CodeCrafters. It uses an LLM (Mistral via their API) to understand prompts and take actions through tool calls — reading files, writing files, and running shell commands.

---

## What I Learnt

### LLM Concepts
- **Tool calling / Function calling** — how to define tools and pass them to an LLM so it can request their execution
- **Agent loop** — the pattern of repeatedly calling the LLM, executing tool calls it requests, feeding results back, until it produces a final text response
- **Non-determinism** — LLMs produce different outputs on each run; `temperature=0` reduces but does not eliminate this
- **Hallucination** — models fabricate answers when information is missing; system prompts can reduce this but not prevent it
- **Model reliability** — different models vary widely in how reliably they generate valid tool call JSON

### API & Tooling
- **OpenAI-compatible APIs** — Groq, Mistral, and OpenRouter all expose the same API interface as OpenAI, so the OpenAI Python SDK works with all of them
- **Rate limits** — free-tier APIs have strict token-per-minute limits; added retry logic to handle 429 errors gracefully
- **Model deprecation** — free-tier models get decommissioned frequently; always check the provider's deprecation page

### Python & Project Structure
- **`uv`** — fast Rust-based Python package manager; replaces pip + venv + pip-compile
- **Virtual environments** — packages live in `.venv/` per project, not globally
- **`tool.uv.package = true`** — tells uv to build and install the project itself, not just its dependencies, which registers CLI entry points defined in `[project.scripts]`
- **`pyproject.toml` script entry points** — how to turn a Python function into a terminal command

---

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          User's Machine                             │
│                                                                     │
│  Terminal                                                           │
│  $ dummy-claude-code -p "Read README and create main.py"           │
│            │                                                        │
│            ▼                                                        │
│  ┌──────────────────────┐                                          │
│  │     CLI (main.py)    │  parses flags, starts REPL or runs once  │
│  └──────────┬───────────┘                                          │
│             │                                                       │
│             ▼                                                       │
│  ┌──────────────────────┐         ┌──────────────────────────┐     │
│  │  Agent Loop          │  HTTPS  │     Mistral AI API       │     │
│  │  (agent.py)          │◄───────►│  mistral-small-latest    │     │
│  │                      │         │  /v1/chat/completions    │     │
│  │  - Builds messages   │         └──────────────────────────┘     │
│  │  - Handles retries   │                                          │
│  │  - Executes tools    │                                          │
│  └──────────┬───────────┘                                          │
│             │                                                       │
│             ▼                                                       │
│  ┌──────────────────────────────────────┐                          │
│  │         Tools (tools.py)             │                          │
│  │                                      │                          │
│  │  Read  ──► open(file)                │                          │
│  │  Write ──► open(file, 'w')           │  runs locally on disk   │
│  │  Bash  ──► subprocess.run(cmd)       │  and shell              │
│  └──────────────────────────────────────┘                          │
└─────────────────────────────────────────────────────────────────────┘
```

### Agent Loop — Request / Response Flow

```
  CLI              Agent Loop             Mistral API          Local Tools
   │                    │                      │                    │
   │ agent_loop(prompt) │                      │                    │
   │───────────────────►│                      │                    │
   │                    │  POST /completions   │                    │
   │                    │  [system, user]      │                    │
   │                    │─────────────────────►│                    │
   │                    │◄─────────────────────│                    │
   │                    │  finish: tool_calls  │                    │
   │                    │  Read("README.md")   │                    │
   │                    │                      │                    │
   │                    │  execute Read ───────┼───────────────────►│
   │                    │◄─────────────────────┼────────────────────│
   │                    │  file contents       │                    │
   │                    │                      │                    │
   │                    │  POST /completions   │                    │
   │                    │  [system, user,      │                    │
   │                    │   assistant(tool),   │                    │
   │                    │   tool(result)]      │                    │
   │                    │─────────────────────►│                    │
   │                    │◄─────────────────────│                    │
   │                    │  finish: stop        │                    │
   │                    │  content: "Done"     │                    │
   │◄───────────────────│                      │                    │
   │  "Done"            │                      │                    │
```

### Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.14 |
| LLM Provider | Mistral AI (`mistral-small-latest`) |
| API Protocol | OpenAI-compatible REST API |
| HTTP Client | OpenAI Python SDK |
| Package Manager | `uv` |
| Config | `python-dotenv` |

### Tools

| Tool | Executes on | What it does |
|------|------------|-------------|
| `Read` | Local filesystem | Reads and returns file contents |
| `Write` | Local filesystem | Creates or overwrites a file |
| `Bash` | Local shell | Runs any shell command, returns stdout + stderr |

---

## Local Setup

### Prerequisites
- Python 3.14+
- [`uv`](https://github.com/astral-sh/uv) installed

Install `uv` if you don't have it:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 1. Clone the repo
```bash
git clone <your-repo-url>
```

### 2. Install dependencies and CLI
```bash
uv sync
```
This installs all dependencies and registers the `dummy-claude-code` command in `.venv/bin/`.

### 3. Set up environment variables
```bash
cp .env.example .env
```
Edit `.env` and add your Mistral API key (get one free at [console.mistral.ai](https://console.mistral.ai)):
```
MISTRAL_API_KEY=your_key_here
```

### 4. Run it

**Single prompt:**
```bash
./your_program.sh -p "List files in the current directory using bash"
# or
.venv/bin/dummy-claude-code -p "List files in the current directory using bash"
```

**Interactive REPL (like Claude Code):**
```bash
.venv/bin/dummy-claude-code
```
```
Dummy Claude Code  |  model: mistral-small-latest
Type 'exit' or press Ctrl+C to quit.

> Read README.md and summarize it
> Write a hello world python script to hello.py
> exit
```

**Use from anywhere in terminal** — add to `~/.zshrc`:
```bash
export PATH="/path/to/Dummy-Claude-code/.venv/bin:$PATH"
```
Then just type `dummy-claude-code` from any directory.

### CLI flags

| Flag | Description |
|------|-------------|
| `-p "prompt"` | Run a single prompt and exit |
| `--model` | Override the model (default: `mistral-small-latest`) |
| `--no-verbose` | Hide tool call logs |

---

## Submit to CodeCrafters

```bash
codecrafters submit
```
