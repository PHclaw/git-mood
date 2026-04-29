"""Git log parsing utilities."""

import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional
import os

from .models import Commit


def parse_git_log(repo_path: str, days: int = 30, author: Optional[str] = None) -> list[Commit]:
    """
    Parse git log output and return list of Commit objects.
    
    Args:
        repo_path: Path to git repository
        days: Number of days to look back
        author: Optional author filter
    
    Returns:
        List of Commit objects
    """
    repo = Path(repo_path).resolve()
    
    if not (repo / ".git").exists():
        raise FileNotFoundError(f"Not a git repository: {repo}")
    
    # Build git log command
    cmd = [
        "git", "-C", str(repo),
        "log",
        f"--since={days} days ago",
        '--pretty=format:%H|%an|%ae|%at|%s',
        "--no-merges",
    ]
    
    if author:
        cmd.extend(["--author", author])
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="replace",
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"git log failed: {e.stderr}") from e
    
    commits = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        
        parts = line.split("|", 4)
        if len(parts) != 5:
            continue
        
        hash_str, author_name, author_email, timestamp, message = parts
        
        try:
            ts = datetime.fromtimestamp(int(timestamp))
        except ValueError:
            continue
        
        commit = Commit(
            hash=hash_str,
            message=message,
            author=f"{author_name} <{author_email}>",
            timestamp=ts,
        )
        commits.append(commit)
    
    return commits


def get_repo_name(repo_path: str) -> str:
    """Get the repository name from path or remote URL."""
    repo = Path(repo_path).resolve()
    
    # Try to get from remote
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True,
        )
        url = result.stdout.strip()
        # Extract name from URL
        if url.endswith(".git"):
            url = url[:-4]
        return url.split("/")[-1]
    except:
        pass
    
    # Fallback to directory name
    return repo.name


def get_all_authors(repo_path: str) -> list[str]:
    """Get list of all authors who have committed to the repo."""
    repo = Path(repo_path).resolve()
    
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "shortlog", "-sne", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="replace",
        )
        authors = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            # Format: "  123  Author Name <email>"
            parts = line.strip().split("\t", 1)
            if len(parts) == 2:
                authors.append(parts[1])
        return authors
    except:
        return []
