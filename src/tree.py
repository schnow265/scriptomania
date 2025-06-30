# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "rich",
#     "loguru",
#     "trio"
# ]
# ///

import subprocess
import sys
import argparse
from typing import List, Dict, Set, Any
from rich import print
from rich.tree import Tree
from loguru import logger
import trio

def parse_package_name(package: str) -> str:
    """Strip angle brackets, quotes, and whitespace from a package name."""
    return package.strip().strip("<>").strip('"').strip("'")

async def get_package_dependencies(package: str, show_recommends: bool = False, show_suggests: bool = False) -> Dict[str, List[str]]:
    """
    Returns a dict with keys: "Depends", "Recommends", "Suggests".
    Each key maps to a list of packages.
    """
    package = parse_package_name(package)
    logger.debug(f"Getting dependencies for {package}")
    try:
        # Wrap check_output in a lambda to provide keyword arguments
        output = await trio.to_thread.run_sync(
            lambda: subprocess.check_output(
                ["apt-cache", "depends", package],
                text=True,
                stderr=subprocess.DEVNULL
            )
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Error occured when checking dependencies for {package}:\n{e}")
        return {"Depends": [], "Recommends": [], "Suggests": []}
    deps = {"Depends": [], "Recommends": [], "Suggests": []}
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("Depends:"):
            dep = line.split(":", 1)[1].strip()
            dep = dep.split(" | ")[0].strip()
            deps["Depends"].append(dep)
        elif show_recommends and line.startswith("Recommends:"):
            dep = line.split(":", 1)[1].strip()
            dep = dep.split(" | ")[0].strip()
            deps["Recommends"].append(dep)
        elif show_suggests and line.startswith("Suggests:"):
            dep = line.split(":", 1)[1].strip()
            dep = dep.split(" | ")[0].strip()
            deps["Suggests"].append(dep)
    return deps

async def build_dep_tree(
    package: str,
    visited: Set[str],
    parent_tree: Tree,
    all_branches: Dict[str, Tree],
    show_recommends: bool = False,
    show_suggests: bool = False,
    nursery: Any = None
):
    if package in visited:
        parent_tree.add(f"[yellow]{package}[/yellow] [dim](already listed)")
        return
    visited.add(package)
    branch = parent_tree.add(f"[bold]{package}[/bold]")
    all_branches[package] = branch

    deps = await get_package_dependencies(package, show_recommends=show_recommends, show_suggests=show_suggests)
    logger.debug(
        f"Package '{package}': {len(deps['Depends'])} Depends, "
        f"{len(deps['Recommends'])} Recommends, {len(deps['Suggests'])} Suggests"
    )

    for dep in deps["Depends"]:
        if nursery:
            nursery.start_soon(build_dep_tree, dep, visited, branch, all_branches, show_recommends, show_suggests, nursery)
        else:
            await build_dep_tree(dep, visited, branch, all_branches, show_recommends, show_suggests)
    if show_recommends:
        for dep in deps["Recommends"]:
            if nursery:
                nursery.start_soon(build_dep_tree_optional, dep, visited, branch, all_branches, "blue", "recommends", show_recommends, show_suggests, nursery)
            else:
                await build_dep_tree_optional(dep, visited, branch, all_branches, "blue", "recommends", show_recommends, show_suggests)
    if show_suggests:
        for dep in deps["Suggests"]:
            if nursery:
                nursery.start_soon(build_dep_tree_optional, dep, visited, branch, all_branches, "green", "suggests", show_recommends, show_suggests, nursery)
            else:
                await build_dep_tree_optional(dep, visited, branch, all_branches, "green", "suggests", show_recommends, show_suggests)

async def build_dep_tree_optional(
    package: str,
    visited: Set[str],
    parent_tree: Tree,
    all_branches: Dict[str, Tree],
    color: str,
    label: str,
    show_recommends: bool = False,
    show_suggests: bool = False,
    nursery: Any = None
):
    if package in visited:
        parent_tree.add(f"[yellow]{package}[/yellow] [dim](already listed)")
        return
    visited.add(package)
    branch = parent_tree.add(f"[bold {color}]{package}[/bold {color}] [dim][{label}][/dim]")
    all_branches[package] = branch

    deps = await get_package_dependencies(package, show_recommends=show_recommends, show_suggests=show_suggests)
    logger.debug(
        f"Optional package '{package}': {len(deps['Depends'])} Depends, "
        f"{len(deps['Recommends'])} Recommends, {len(deps['Suggests'])} Suggests"
    )

    for dep in deps["Depends"]:
        if nursery:
            nursery.start_soon(build_dep_tree, dep, visited, branch, all_branches, show_recommends, show_suggests, nursery)
        else:
            await build_dep_tree(dep, visited, branch, all_branches, show_recommends, show_suggests)
    if show_recommends:
        for dep in deps["Recommends"]:
            if nursery:
                nursery.start_soon(build_dep_tree_optional, dep, visited, branch, all_branches, "blue", "recommends", show_recommends, show_suggests, nursery)
            else:
                await build_dep_tree_optional(dep, visited, branch, all_branches, "blue", "recommends", show_recommends, show_suggests)
    if show_suggests:
        for dep in deps["Suggests"]:
            if nursery:
                nursery.start_soon(build_dep_tree_optional, dep, visited, branch, all_branches, "green", "suggests", show_recommends, show_suggests, nursery)
            else:
                await build_dep_tree_optional(dep, visited, branch, all_branches, "green", "suggests", show_recommends, show_suggests)

@logger.catch
def main():
    parser = argparse.ArgumentParser(
        description="Display a Debian dependency tree with optional/recommended dependencies colorized (async with trio)."
    )
    parser.add_argument(
        "package_file",
        metavar="packages.txt",
        help="Path to a text file with one package name per line"
    )
    parser.add_argument(
        "--recommends", "-r",
        action="store_true",
        help="Show recommended dependencies in the tree"
    )
    parser.add_argument(
        "--suggests", "-s",
        action="store_true",
        help="Show suggested dependencies in the tree"
    )
    args = parser.parse_args()

    try:
        with open(args.package_file, "r") as f:
            packages = [parse_package_name(line) for line in f if line.strip()]
    except Exception as e:
        print(f"[red]Failed to read file:[/red] {e}")
        sys.exit(1)

    visited = set()
    all_branches = {}
    root = Tree("[bold]Dependency Tree[/bold]")

    logger.info(f"Building tree for {len(packages)} packages")

    async def runner():
        async with trio.open_nursery() as nursery:
            for pkg in packages:
                if pkg not in visited:
                    nursery.start_soon(
                        build_dep_tree,
                        pkg, visited, root, all_branches,
                        args.recommends, args.suggests, nursery
                    )

    trio.run(runner)
    print(root)

if __name__ == "__main__":
    main()