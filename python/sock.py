#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "rich",
# ]
# ///

import os
import subprocess

from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.theme import Theme

# Catppuccin Macchiato color theme mapping
custom_theme = Theme({
    "so_file": "bold blue",
    "error": "bold red",
    "lib": "cyan",
    "dim": "grey50"
})

console = Console(theme=custom_theme)

def find_so_files(root):
    """Recursively find .so files under the given root directory."""
    so_files = []
    for dirpath, _, filenames in os.walk(root):
        for fname in filenames:
            if fname.endswith('.so'):
                so_files.append(os.path.join(dirpath, fname))
    return so_files

def main():
    so_files = find_so_files("/lib")
    for sofile in so_files:
        try:
            proc = subprocess.run(
                ["ldd", sofile],
                capture_output=True,
                text=True,
                check=False
            )
            missing_lines = [line for line in proc.stdout.splitlines() if "not found" in line]
            if missing_lines:
                # File panel header
                file_text = Text("File: ", style="dim") + Text(sofile, style="so_file")
                console.print(Panel(file_text, style="dim", expand=False, padding=(0,1)))
                for line in missing_lines:
                    lib = line.split()[0]
                    error_line = Text("  Missing: ", style="error") + Text(lib, style="lib")
                    console.print(error_line)
                console.print()
        except Exception:
            continue

if __name__ == "__main__":
    main()
