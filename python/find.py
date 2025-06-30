import sys
import subprocess
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

def find_package_containing_file(filename):
    console = Console()
    try:
        result = subprocess.run(
            ["apt-file", "search", filename],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        output = result.stdout.strip()
        if output:
            table = Table(title=f"Packages containing '{filename}'", show_lines=True)
            table.add_column("Package", style="bold green")
            table.add_column("File", style="cyan")
            for line in output.splitlines():
                if ": " in line:
                    pkg, path = line.split(": ", 1)
                    table.add_row(pkg, path)
            console.print(table)
        else:
            console.print(Panel.fit(f"No packages found containing '{filename}'.", style="bold red"))
    except subprocess.CalledProcessError as e:
        if "apt-file: command not found" in e.stderr:
            console.print(Panel.fit(
                "[bold red]Error:[/] apt-file is not installed.\nInstall it with:\n[cyan]sudo apt-get install apt-file[/]\nand update with:\n[cyan]sudo apt-file update[/]",
                title="Fatal Error"
            ))
        else:
            console.print(Panel.fit(f"An error occurred:\n{e.stderr.strip()}", style="bold red"))

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <filename>")
        sys.exit(1)
    filename = sys.argv[1]
    find_package_containing_file(filename)

if __name__ == "__main__":
    main()
