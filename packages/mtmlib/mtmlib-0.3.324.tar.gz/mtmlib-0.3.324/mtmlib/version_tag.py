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


def parse_version(version_str):
    # Example version parsing logic
    print("version_str", version_str)
    parts = version_str.split(".")
    major, minor, patch = (int(parts[0]), int(parts[1]), int(parts[2]))
    return {"major": major, "minor": minor, "patch": patch}


def read_tag_version():
    current_tag = exec_shell_command("git", "describe", "--tags")
    current_tag_rev = exec_shell_command("git", "describe", "--tags", "--abbrev=0")
    version = parse_version(current_tag_rev[1:])

    if current_tag_rev != current_tag and "pre-release" not in version:
        version["patch"] += 1

    return version
