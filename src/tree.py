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
    Returns a dict with keys: "Depends", "Recommends", "Suggests" for normal mode.
    """
    package = parse_package_name(package)
    logger.debug(f"Getting dependencies for {package}")
    try:
        output = await trio.to_thread.run_sync(
            lambda: subprocess.check_output(
                ["apt-cache", "depends", package],
                text=True,
                stderr=subprocess.DEVNULL
            )
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Error occurred when checking dependencies for {package}:\n{e}")
        return {"Depends": [], "Recommends": [], "Suggests": []}
    deps = {"Depends": [], "Recommends": [], "Suggests": []}
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("Depends:"):
            dep = line.split(":", 1)[1].strip().split(" | ")[0].strip()
            deps["Depends"].append(dep)
        elif show_recommends and line.startswith("Recommends:"):
            dep = line.split(":", 1)[1].strip().split(" | ")[0].strip()
            deps["Recommends"].append(dep)
        elif show_suggests and line.startswith("Suggests:"):
            dep = line.split(":", 1)[1].strip().split(" | ")[0].strip()
            deps["Suggests"].append(dep)
    return deps

async def get_reverse_dependencies(package: str) -> List[str]:
    """
    Returns a list of packages which depend (directly) on the given package.
    """
    package = parse_package_name(package)
    logger.debug(f"Getting reverse dependencies for {package}")
    try:
        output = await trio.to_thread.run_sync(
            lambda: subprocess.check_output(
                ["apt-cache", "rdepends", package],
                text=True,
                stderr=subprocess.DEVNULL
            )
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Error occurred when checking reverse dependencies for {package}:\n{e}")
        return []
    rdeps = set()
    recording = False
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("Reverse Depends:"):
            recording = True
            continue
        if recording:
            # Lines are packages, indented or not
            pkg = line.strip()
            if pkg and not pkg.startswith(" "):
                pkg = pkg.split(" ", 1)[0]
            pkg = parse_package_name(pkg)
            if pkg and pkg != package:
                rdeps.add(pkg)
    logger.debug(f"Reverse dependencies for {package}: {rdeps}")
    return list(sorted(rdeps))

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

async def build_reverse_tree(
    package: str,
    visited: Set[str],
    parent_tree: Tree,
    all_branches: Dict[str, Tree],
    nursery: Any = None
):
    if package in visited:
        parent_tree.add(f"[yellow]{package}[/yellow] [dim](already listed)")
        return
    visited.add(package)
    branch = parent_tree.add(f"[bold]{package}[/bold]")
    all_branches[package] = branch

    rdeps = await get_reverse_dependencies(package)
    logger.debug(f"Package '{package}': {len(rdeps)} reverse dependencies")
    for rdep in rdeps:
        if nursery:
            nursery.start_soon(build_reverse_tree, rdep, visited, branch, all_branches, nursery)
        else:
            await build_reverse_tree(rdep, visited, branch, all_branches)

@logger.catch
def main():
    parser = argparse.ArgumentParser(
        description="Display a Debian dependency tree or reverse dependency tree (async with trio)."
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
    parser.add_argument(
        "--reverse", "-R",
        action="store_true",
        help="Show reverse dependency tree (list packages which depend on the input packages)"
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
    root = Tree("[bold]Dependency Tree[/bold]" if not args.reverse else "[bold]Reverse Dependency Tree[/bold]")

    logger.info(f"Building tree for {len(packages)} packages (reverse={args.reverse})")

    async def runner():
        async with trio.open_nursery() as nursery:
            for pkg in packages:
                if pkg not in visited:
                    if args.reverse:
                        nursery.start_soon(
                            build_reverse_tree,
                            pkg, visited, root, all_branches, nursery
                        )
                    else:
                        nursery.start_soon(
                            build_dep_tree,
                            pkg, visited, root, all_branches,
                            args.recommends, args.suggests, nursery
                        )

    trio.run(runner)
    print(root)

if __name__ == "__main__":
    main()
