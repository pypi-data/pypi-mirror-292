import subprocess


def exec_shell_command(*args):
    try:
        result = (
            subprocess.check_output(args, stderr=subprocess.STDOUT).decode().strip()
        )
        return result, None  # Return result and None for the error
    except subprocess.CalledProcessError as e:
        return None, e  # Return None for the result and the error


def read_tag():
    current_tag, err = exec_shell_command("git", "describe", "--tags")
    if err:
        return current_tag, err

    current_tag_rev, _ = exec_shell_command("git", "describe", "--tags", "--abbrev=0")
    if current_tag_rev == current_tag:
        return current_tag[1:], None

    short_commit, _ = exec_shell_command("git", "rev-parse", "--short", "HEAD")
    version = parse_version(current_tag_rev[1:])
    return f"{version}-{short_commit}", None


def patch_git_tag_version():
    """版本号的补丁版本加1"""
    version = read_tag_version()
    new_patch_version = f"v{version['major']}.{version['minor']}.{version['patch']}"
    exec_shell_command("git", "tag", new_patch_version)
    exec_shell_command("git", "push", "origin", new_patch_version)


def parse_version(version_str):
    parts = version_str.split(".")
    return {"major": int(parts[0]), "minor": int(parts[1]), "patch": int(parts[2])}


def read_tag_version():
    current_tag = exec_shell_command("git", "describe", "--tags")
    current_tag_rev = exec_shell_command("git", "describe", "--tags", "--abbrev=0")
    version = parse_version(current_tag_rev[1:])

    if current_tag_rev != current_tag and "pre-release" not in version:
        version["patch"] += 1

    return version
