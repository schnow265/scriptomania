import argparse
import os
import subprocess
import sys
import tempfile
import toml
import pygit2
import docker

def parse_args():
    parser = argparse.ArgumentParser(description="Manage git worktrees and Docker containers.")
    parser.add_argument('--repo', required=True, help='Path to the bare cloned git repo.')
    parser.add_argument('--toml', required=True, help='Path to the TOML config file.')
    parser.add_argument('--branch', required=True, help='Branch to checkout as worktree.')
    parser.add_argument('--worktree-dir', required=False, help='Directory for the worktree.')
    parser.add_argument('--connect', action='store_true', help='Connect to the running container.')
    args = parser.parse_args()
    return args

def load_config(toml_path):
    with open(toml_path, "r") as f:
        return toml.load(f)

def ensure_worktree(repo_path, branch, worktree_dir):
    repo = pygit2.Repository(repo_path)
    if worktree_dir is None:
        worktree_dir = os.path.join(tempfile.gettempdir(), f"{os.path.basename(repo_path)}_{branch}_worktree")
    if not os.path.exists(worktree_dir):
        os.makedirs(worktree_dir)
    # Add worktree if not already present
    try:
        repo.add_worktree(worktree_dir, branch)
    except Exception as e:
        if "already exists" not in str(e):
            raise
    return os.path.abspath(worktree_dir)

def docker_run(config, worktree_dir):
    client = docker.from_env()
    image = config["container"]["image"]
    name = config["container"].get("name", "git_worktree_container")
    additional_mounts = config["container"].get("additional_mounts", [])
    # Prepare volume mounts
    volumes = {
        os.path.abspath(worktree_dir): {'bind': '/worktree', 'mode': 'rw'}
    }
    for m in additional_mounts:
        if isinstance(m, dict):
            src = os.path.abspath(m.get("src"))
            dst = m.get("dst")
            mode = m.get("mode", "rw")
            if src and dst:
                volumes[src] = {'bind': dst, 'mode': mode}
        elif isinstance(m, str):
            parts = m.split(":")
            if len(parts) >= 2:
                src = os.path.abspath(parts[0])
                dst = parts[1]
                mode = parts[2] if len(parts) > 2 else "rw"
                volumes[src] = {'bind': dst, 'mode': mode}
    # Pull image if not present
    try:
        client.images.get(image)
    except docker.errors.ImageNotFound:
        print(f"Pulling image {image}...")
        client.images.pull(image)
    # Check if container exists
    try:
        container = client.containers.get(name)
        if container.status != "running":
            container.start()
    except docker.errors.NotFound:
        container = client.containers.run(
            image,
            "sleep infinity",
            name=name,
            volumes=volumes,
            working_dir="/worktree",
            detach=True,
            tty=True,
            stdin_open=True
        )
    return container

def docker_connect(container):
    # Use docker CLI for interactive shell
    os.execvp("docker", ["docker", "exec", "-it", container.name, "bash"])

def main():
    args = parse_args()
    config = load_config(args.toml)
    worktree_dir = ensure_worktree(args.repo, args.branch, args.worktree_dir)
    container = docker_run(config, worktree_dir)
    if args.connect:
        docker_connect(container)
    else:
        print(f"Worktree at {worktree_dir} mounted to container '{container.name}'. Use --connect to enter.")

if __name__ == "__main__":
    main()