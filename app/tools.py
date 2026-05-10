import subprocess

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "Read",
            "description": "Read and return the contents of a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The path to the file to read",
                    }
                },
                "required": ["file_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "Write",
            "description": "Write content to a file",
            "parameters": {
                "type": "object",
                "required": ["file_path", "content"],
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The path of the file to write to",
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to write to the file",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "Bash",
            "description": "Execute a shell command",
            "parameters": {
                "type": "object",
                "required": ["command"],
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The shell command to execute",
                    }
                },
            },
        },
    },
]


def execute_tool(name: str, args: dict) -> str:
    if name == "Read":
        try:
            with open(args["file_path"], "r") as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"

    if name == "Write":
        try:
            with open(args["file_path"], "w") as f:
                f.write(args["content"])
            return "true"
        except Exception as e:
            return "false"

    if name == "Bash":
        try:
            result = subprocess.run(
                args["command"],
                shell=True,
                capture_output=True,
                text=True,
            )
            output = result.stdout + result.stderr
            return output if output else "(no output)"
        except Exception as e:
            return f"Error executing command: {e}"

    return f"Unknown tool: {name}"
