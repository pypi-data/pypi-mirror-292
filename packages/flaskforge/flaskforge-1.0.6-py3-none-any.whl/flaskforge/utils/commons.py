import os
import subprocess


def dirname(path, levels=1):
    parent_directory = path
    for _ in range(levels):
        parent_directory = os.path.dirname(parent_directory)
    return parent_directory


def join_path(*path):
    new_path = (p for p in path if p != ".")
    return os.path.join(*new_path)


def exec_command(command: str, echo=True) -> str:
    # Run the command and capture the output
    result = subprocess.run(command, shell=True, text=True, capture_output=True)

    if echo:
        print(result.stdout) if result.stdout else print(result.stderr)
    # Return the output
    return result.stdout
