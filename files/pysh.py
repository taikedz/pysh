import os
import sys
import shlex
import subprocess
import argparse
import pathlib

""" Convenience suite for system scripting in python
"""

def main_wrap(_func):
    try:
        _func()
    except (KeyboardInterrupt,Exception) as e:
        if HERE.env("PY_TRACEBACK", "false").lower() == "true":
            raise
        else:
            print(e)
            exit(1)


class PySh:
    def __init__(self, topfile):
        self._topfile = pathlib.Path(topfile)
        self._topdir = self._topfile.parent
        self.args = ArgumentParserPysh()
        self.user = UserPysh()


    def open(self, filepath, mode='r'):
        """ Open a file in the same directory as the current script
        """
        return open(self._topdir/filepath, mode)


    def path(self, path=''):
        """ Resolve a path starting in the same directory as current script
        """
        return self._topfile / path

    
    def env(self, name, defval=None):
        """ Get an environment variable
        """
        return os.getenv(name, defval)


    def shjoin(self, tokens):
        """ Join shell tokens
        """
        return shlex.join(tokens)


    def process(self, command, text=False) -> tuple[int, str, str]:
        """ Execute a single command subprocess, return the status, stdout and stderr.

        Piping is not allowed.

        Set `text=True` to return stdout and stderr as strings instead of byte strings
        """
        if isinstance(command, str):
            command = shlex.split(command)

        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        so, se = p.communicate()

        if text is True:
            so = str(so, 'utf-8')
            se = str(se, 'utf-8')

        return p.returncode, so, se


    def shell(self, command) -> None:
        """ Run a shell command. Piping is allowed. Output is not captured.
        """
        os.system(command, shell=True)


class UserPysh:
    def ask(self, prompt) -> str:
        """ Ask a user for input
        """
        print(prompt, end='', flush=True)
        res = sys.stdin.readline()
        return res.strip("\n")


    def confirm(self, prompt) -> bool:
        """ Ask a user for a yes/no response as 'y' or 'yes'
        Return True if y/yes , False otherwise
        """
        res = self.ask(prompt)
        return res.lower() in ["yes", "y"]


    def choose(self, prompt, options):
        """ Display the list of options, ask user to choose from list via number

        Return the chosen string

        Raises ValueError if user entered non-int or value out of range
        """
        i = 1
        for item in options:
            print(f"  {i}: {item}")
            i+=1

        res = self.ask(prompt)
        res = int(res)
        if 0 < res and res <= len(res):
            return options[res-1]
        else:
            raise ValueError("Out of range")


    def name(self) -> str:
        """ Return the current user name
        """
        return os.getenv("USERNAME")

    def uid(self) -> int:
        """ Return the current user ID
        """
        return int(os.getenv("UID"))


    def os(self) -> tuple[str,str]:
        """ Return the OS name and version as of /etc/hosts (Linux and Unix only)
        """
        if not os.name == "posix":
            # TODO - implement for Windows
            raise RuntimeError("Only available on POSIX systems")

        with open("/etc/hosts") as fh:
            lines = [line.split("=", maxsplit=1) for line in fh.readlines()]
        data = {k:v.strip('\n"') for k,v in lines}
        return data["ID"], data["VERSION_ID"]


class ArgumentParserPysh:
    def __init__(self):
        self._parser = argparse.ArgumentParser()
        self._positionals_locked = False


    def parse(self):
        """ Parse arguments as currently defined
        """
        return self._parser.parse_args()


    def add_argument(self, *a, **k):
        """ Add a raw argument to the parser. See argparse.ArgumentParser.add_argument(...)
        """
        self._parser.add_argument(*a, **k)


    def positionals(self, *names):
        """ Add named positional arguments, or '+' or '*'
        """
        assert not self._positionals_locked, "INTENRAL FATAL: Positional args can no longer be added."
        if len(names) == 1 and names[0] in ["+", "*"]:
            self._parser.add_argument("positionals", nargs=names[0])
            return

        for name in names:
            self._parser.add_argument(name)


    def flags(self, *flags):
        """ Add boolean flags. During runtime, unset flags are flase, set flags are true
        """
        for flag in flags:
            if not flag.startswith("--"):
                if flag.startswith("-"):
                    flag = f"-{flag}"
                else:
                    flag = f"--{flag}"
            self._parser.add_argument(flag, action="store_true")


    def options(self, **opts):
        """ Add options with default values
        """
        for flag, defval in opts.items():
            if not flag.startswith("--"):
                if flag.startswith("-"):
                    flag = f"-{flag}"
                else:
                    flag = f"--{flag}"
            self._parser.add_argument(flag, default=defval, type=type(defval))

