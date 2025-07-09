import argparse
import os
import subprocess
import sys

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme

console = Console(
    theme=Theme(
        {"so_file": "bold blue", "error": "bold red", "lib": "cyan", "dim": "grey50"}
    )
)


def find_so_files(root: str) -> list[str]:
    so_files: list[str] = []
    for dirpath, _, filenames in os.walk(root):
        for fname in filenames:
            if fname.endswith(".so"):
                so_files.append(os.path.join(dirpath, fname))
    return so_files


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="SOCk - .so file Checker",
        description="Verifies that all linked dependencies of so files are known via ldconfig",
    )
    parser.add_argument(
        "dirname",
        default="/lib",
        help="The folder in where to look for .so files. (Default is /lib)",
    )
    args = parser.parse_args()

    so_files: list[str] = find_so_files(args.dirname)
    has_missing = 0
    total_checked = 0
    missing_avaliable = 0
    for sofile in so_files:
        try:
            proc = subprocess.run(
                ["ldd", sofile], capture_output=True, text=True, check=False
            )
            total_checked += 1
            missing_lines = [
                line for line in proc.stdout.splitlines() if "not found" in line
            ]
            if missing_lines:
                has_missing += 1
                # File panel header
                file_text = Text("File: ", style="dim") + Text(sofile, style="so_file")
                console.print(
                    Panel(file_text, style="dim", expand=False, padding=(0, 1))
                )
                for line in missing_lines:
                    lib = line.split()[0]
                    error_line = Text("  Missing: ", style="error") + Text(
                        lib, style="lib"
                    )
                    if lib in so_files:
                        missing_avaliable += 1
                        error_line += Text("    Found matching file: ", style="dim") + Text(
                            lib, style="lib"
                        )
                    console.print(error_line)
                console.print()
        except Exception:
            continue

    # Add summary output
    summary_text = (
        f"{has_missing} of {total_checked} .so files have missing dependencies; {missing_avaliable} missing libs are actually present"
    )
    console.print(Panel(summary_text, style="bold", expand=False))

    if has_missing:
        sys.exit(1)


if __name__ == "__main__":
    main()
