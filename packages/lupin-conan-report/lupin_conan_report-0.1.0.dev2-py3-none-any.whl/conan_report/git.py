import subprocess

from conan_report.logger_manager import die


def get_remote_origin_url() -> str:
    """
    Get the remote origin URL of the current repository.

    Returns:
        str: The remote origin URL of the current repository.
    """
    process = subprocess.Popen(
        ["git", "config", "--get", "remote.origin.url"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, _ = process.communicate()

    if process.returncode != 0:
        die("Failed to get remote origin URL")

    gitlab_url = stdout.decode("utf-8").strip()
    if gitlab_url.startswith("https://gitlab.com/"):
        return gitlab_url[:-4] if gitlab_url.endswith(".git") else gitlab_url
    else:
        a = gitlab_url.find(":")
        if a != -1:
            gitlab_url = gitlab_url.replace(":", "/")
        gitlab_location = gitlab_url.find("@gitlab.com")
        gitlab_url = gitlab_url[gitlab_location + 1 :]
        gitlab_url = "https://" + gitlab_url
    return gitlab_url[:-4] if gitlab_url.endswith(".git") else gitlab_url


def get_current_branch() -> str:
    """
    Get the current branch of the current repository.

    Returns:
        str: The current branch of the current repository.
    """
    process = subprocess.Popen(
        ["git", "branch", "--show-current"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, _ = process.communicate()

    if process.returncode != 0:
        die("Failed to get current branch")

    return stdout.decode("utf-8").strip()


def get_commit_hash() -> str:
    """
    Get the commit hash of the current repository.

    Returns:
        str: The commit hash of the current repository.
    """
    process = subprocess.Popen(
        ["git", "rev-parse", "HEAD"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, _ = process.communicate()

    if process.returncode != 0:
        die("Failed to get commit hash")

    return stdout.decode("utf-8").strip()


def _is_tag_exists() -> bool:
    """
    Check if the current repository has a tag.

    Returns:
        bool: True if the current repository has a tag, False otherwise.
    """
    process = subprocess.Popen(
        ["git", "tag"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, _ = process.communicate()

    if process.returncode != 0:
        die("Failed to get tags")

    return len(stdout.decode("utf-8").strip()) > 0


def get_commit_tag() -> str:
    """
    Get the commit tag of the current repository.

    Returns:
        str: The commit tag of the current repository.
    """
    if _is_tag_exists():
        process = subprocess.Popen(
            ["git", "describe", "--tags"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, _ = process.communicate()

        if process.returncode != 0:
            die("Failed to get commit tag")
        return stdout.decode("utf-8").strip()
    return ""
