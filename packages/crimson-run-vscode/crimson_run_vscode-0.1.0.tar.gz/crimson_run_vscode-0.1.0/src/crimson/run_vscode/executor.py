import yaml
import os
from typing import Any


class VSCodeAutomation:
    def __init__(self, output_dir: str = "temp/run_vscode"):
        self.output_dir = output_dir
        self.commands = []

    @property
    def run_vscode_path(self):
        return f"{self.output_dir}/run_vscode.yaml"

    @property
    def progress_path(self):
        return f"{self.output_dir}/vscode_extension_progress.json"

    def add_command(self, command: str, args: Any = None):
        cmd = {"command": command}
        if args:
            cmd["args"] = args
        self.commands.append(cmd)

    def generate_yaml(self, execute: bool = False):
        config = {"execute": execute, "vscode": self.commands}

        directory = os.path.dirname(self.run_vscode_path)

        if not os.path.exists(directory):
            os.makedirs(directory)

        # Write YAML file
        with open(self.run_vscode_path, "w") as f:
            yaml.dump(config, f)

    def clear_commands(self):
        self.commands = []
