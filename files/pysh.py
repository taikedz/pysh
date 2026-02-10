import os
import sys
import shlex
import subprocess
import argparse
import pathlib

""" Convenience suite for system scripting in python
"""

class PySh:
    def __init__(self, topfile):
        self._topfile = pathlib.Path(topfile)
        self._topdir = self._topfile.parent
        self.args = ArgumentParserPysh()
        self.user = UserPysh()


    def open(self, filepath, mode='r'):
        return open(self._topdir/filepath, mode)

    
    def env(self, name, defval=None):
        return os.getenv(name, defval)


    def shjoin(self, tokens):
        return shlex.join(tokens)


    def process(self, command, text=False) -> tuple[int, str, str]:
        if isinstance(command, str):
            command = shlex.split(command)

        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        so, se = p.communicate()

        if text is True:
            so = str(so, 'utf-8')
            se = str(se, 'utf-8')

        return p.returncode, so, se


    def shell(self, command) -> None:
        os.system(command, shell=True)


class UserPysh:
    def ask(self, prompt):
        print(prompt, end='', flush=True)
        res = sys.stdin.readline()
        return res.strip("\n")


    def confirm(self, prompt):
        res = self.ask(prompt)
        return res.lower() in ["yes", "y"]


    def choose(self, prompt, options):
        raise NotImplementedError("not implemented. use ask()")


    def name(self):
        return os.getenv("USERNAME")

    def uid(self):
        return os.getenv("UID")


class ArgumentParserPysh:
    def __init__(self):
        self._parser = argparse.ArgumentParser()
        self._positionals_locked = False


    def parse(self):
        return self._parser.parse_args()


    def add_argument(self, *a, **k):
        self._parser.add_argument(*a, **k)


    def positionals(self, *names):
        assert not self._positionals_locked, "INTENRAL FATAL: Positional args can no longer be added."
        if len(names) == 1 and names[0] in ["+", "*"]:
            self._parser.add_argument("positionals", nargs=names[0])
            return

        for name in names:
            self._parser.add_argument(name)


    def flags(self, *flags):
        for flag in flags:
            if not flag.startswith("--"):
                if flag.startswith("-"):
                    flag = f"-{flag}"
                else:
                    flag = f"--{flag}"
            self._parser.add_argument(flag, action="store_true")


    def options(self, *opts):
        for flag, defval in opts:
            if not flag.startswith("--"):
                if flag.startswith("-"):
                    flag = f"-{flag}"
                else:
                    flag = f"--{flag}"
            self._parser.add_argument(flag, default=defval, type=type(defval))

