import os
from typing import List


def run_script(commands: List[str]):
    command = " ".join(commands)
    if command.strip():
        os.system(command)
