# cobalt-cli-linux

Cobalt is an agentic DeepSeek-powered CLI assistant designed for Debian Linux. It can execute shell commands, read and write local files, maintain a local conversation history, and interact with the DeepSeek API in a production-friendly Python package layout.

## Features

- DeepSeek chat completions via HTTP client
- Safe local shell execution with bash
- Persistent JSON conversation history in the user's home directory
- File read/write operations for scriptable agent workflows
- PyPI-ready package metadata and console script entrypoint

## Installation

```bash
python -m pip install cobalt-cli-linux
```

## Environment variables

```bash
export DEEPSEEK_API_KEY="your_api_key_here"
export DEEPSEEK_MODEL="deepseek-chat"
export DEEPSEEK_BASE_URL="https://api.deepseek.com"
```

## Usage

```bash
cobalt "List the top 10 files in the current directory"
```

You can also pass arguments directly:

```bash
cobalt --api-key "$DEEPSEEK_API_KEY" "Show the current user and OS info"
```

## Project layout

- src/cobalt_cli_linux/agent.py - orchestration logic for tool use and model responses
- src/cobalt_cli_linux/cli.py - command-line entrypoint
- src/cobalt_cli_linux/deepseek_client.py - DeepSeek HTTP client
- src/cobalt_cli_linux/executor.py - shell command execution
- src/cobalt_cli_linux/history.py - local JSON conversation history
- src/cobalt_cli_linux/config.py - environment-based settings

## Notes

This package is intentionally built to work on Debian Linux and uses standard POSIX shell commands. The default history file is stored at ~/.cobalt/history.json.
