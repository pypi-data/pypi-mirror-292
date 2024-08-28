from .util import make_solver
from .blockers import compute_single_card_blocker_effects, SingleCardBlockerEffects
from ..conf import pious_conf
import json
from os import path as osp
import os
import time
import sys


class PioPlugin:
    def __init__(self):
        self.solver = make_solver()
        log_dir = osp.join(
            pious_conf.get_pio_install_directory(), "Plugins", "PiousPlugin", "Logs"
        )
        if not osp.exists(log_dir):
            os.makedirs(log_dir)
        self.log_file = osp.join(log_dir, f"pious{time.time()}.log")
        self.log_file_fd = open(self.log_file, "w")

    def handle_input(self, *s):
        return self.solver._run(*s)

    def handle_plugin_line(self, line):
        if line.startswith("[PIOUS]"):
            line = line[7:].strip()
            command = json.loads(line)
            if command["command"] == "blockers":
                b: SingleCardBlockerEffects = compute_single_card_blocker_effects()
                for k, v in b.equity_deltas:
                    self.solver.echo(f"{k}: {v}")

        else:
            return self.handle_input(line)

    def run_plugin(self):
        self.log_file_fd.write(f"STARTING")
        while True:
            line = input()
            self.log_file_fd.write(f"[INPUT] {line}\n")
            response = self.handle_plugin_line(line)
            sys.stdout.write(response + "\n")
            sys.stdout.flush()
            self.log_file_fd.write(f"[RESPONSE] {response}\n")
