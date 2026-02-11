from genericpath import isfile
import os
import platform
import sys
import shlex
import subprocess
import argparse
import pathlib
import tempfile

""" Convenience suite for system scripting in python

Import this library to gain fast access to common desired functionality.
"""

def main_wrap(_func):
    try:
        _func()
    except (KeyboardInterrupt,Exception) as e:
        if os.getenv("PY_TRACEBACK", "false").lower() == "true":
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

        # Passthroughs
        self.Path = pathlib.Path
        self.isdir = os.path.isdir
        self.isfile = os.path.isfile
        self.makedirs = lambda p: os.makedirs(p, exist_ok=True)
        self.remove = os.remove


    def open_replacing(self, filepath, substitutions:dict[str,str]) -> str:
        """
        Open filepath, and replace any key with corresponding value.

        A substition dict `{'KEY': 'value'}` will replace any instances of `%KEY%` in the file
        with literal `value`.

        :param filepath: ASCII file path to open
        :param substitutions: key-value substitutions
        """
        with open(filepath) as fh:
            text = ''.join(fh.readlines())
        for k,v in substitutions.items():
            text = text.replace(f"%{k}%", v)
        return text
    

    def sudo_write(self, filepath, data, mode='w'):
        """ Write a file to a protected location
        """
        filename = self.tempfile()
        with open(filename, mode) as fh:
            fh.write(data)
        self.shell(f"sudo mv {filename} {filepath}")


    def tempfile(self, dir_abspath=None) -> str:
        """ Create a temp file.

        If dir is specified, makes the temp file in that directory
        If text is set to False, 
        """
        if dir_abspath:
            self.makedirs(dir_abspath)
        _, name = tempfile.mkstemp(dir=dir_abspath)
        return name


    def localpath(self, path='') -> pathlib.Path:
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


    def process(self, command, text=False) -> tuple[int, str|bytes, str|bytes]:
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


    def shell(self, command) -> int:
        """ Run a shell command. Piping is allowed. Output is not captured.

        Returns the command's exit-code
        """
        return os.system(command)


    def os_info(self) -> tuple[str,str,str]:
        """ Return the operating system name and version as of /etc/hosts (Linux and Unix only)
        """
        plat = platform.system().lower()
        if os.path.isfile("/etc/os-release"):
            with open("/etc/os-release") as fh:
                lines = [line.split("=", maxsplit=1) for line in fh.readlines()]
            data = {k:v.strip('\n"') for k,v in lines}
            return platform.system(), data["ID"], data["VERSION_ID"]

        elif plat == "windows":
            return "Windows", platform.win32_edition(), platform.win32_ver()[0]

        else:
            raise RuntimeError(f"Unknown system type: {plat}")


class UserPysh:
    def ask(self, prompt) -> str:
        """ Ask a user for input
        """
        print(prompt, end='', flush=True)
        res = sys.stdin.readline()
        return res.strip("\n")


    def confirm(self, prompt) -> bool:
        """ Ask a user for a yes/no response as 'y' or 'yes'
        Return True if y/yes , False if n/no, or ask again if neither.
        """
        res = ""
        while res.lower() not in ["y", "yes", "no", "n"]:
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
        if 0 < res and res <= len(options):
            return options[res-1]
        else:
            raise ValueError("Out of range")


    def name(self) -> str|None:
        """ Return the current user name
        """
        return os.getenv("USERNAME")


    def uid(self) -> int:
        """ Return the current user ID
        """
        return int(os.getenv("UID", -1))


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

