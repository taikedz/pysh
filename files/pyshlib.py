# (C) 2026 TaiKedz
# Conveyed to you under the terms of the MIT License. See LICENSE.txt or
# https://mit-license.org/ . Essentially: do what you want with it, but
# please do retain this copyright notice.

from datetime import datetime
import hashlib
import os
import platform
import re
import sys
import shlex
import subprocess
import argparse
import pathlib
import tempfile
import time

""" Convenience suite for system scripting in python.
Add a single-import and use functions with helpful defaults.

Import this library to gain fast access to common desired functionality.

Provided as a single sidecar file for your convenience.

Usage:

    import pyshlib
    pysh = pyshlib.PySh(__file__)

    def main():
        ''' Use pysh now. You have access to arg parsing helpers,
        file-location utilties, system and user info, and more.
        '''

    # Wrap your main to suppress stack traces by default ;
    #   user can enable them by setting env `PY_ERRORS=true`
    pysh.main_wrap(main)

"""

def main_wrap(_func):
    try:
        _func()
    except (KeyboardInterrupt,Exception) as e:
        if os.getenv("PY_ERRORS", "false").lower() == "true":
            raise
        else:
            print(e)
            exit(1)


class PySh:

    def __init__(self, topfile):
        self.args = ArgumentParserPysh()
        self.user = UserPysh()
        self.fs = FileSystemPysh(topfile)
        self.util = UtilPysh()


    def env(self, name, defval=None):
        """ Get an environment variable
        """
        return os.getenv(name, defval)


    def shjoin(self, tokens):
        """ Join shell tokens
        """
        return shlex.join(tokens)


    def cmd(self, command, text=False) -> tuple[int, str|bytes, str|bytes]:
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


# class LogPysh:
#     def __init__(self, level="warn", file_level="info"):
#         """ TODO - set up with a useful date-time format
#         Logs go to both terminal and to file ; if corresponding level is `None`, that channel is suppressed at runtime
#         Also provide a `fail()` which logs a fatal and exits with custom status code

#         Ensure logging level can be changed during runtime - or re-created
#         """


class UtilPysh:
    def date(self, spec:str|None=None) -> datetime:
        """ Produce a datetime object. If `spec` is specified, produce an object based on that date-time.
        Else, produce the current date and time object.

        Datetime objects can be compared and subtracted, for effectual temporal math.

        e.g.
            old = PYSH.date()
            PYSH.sleep(1)
            new = PYSH.date()
            assert (new - old).total_seconds() > 0
            assert (old - new).total_seconds() < 0
        """
        if spec:
            assert re.match(r"^\d{4}-\d{2}-\d{2}(T| )\d{2}:\d{2}:\d{2}(\.\d+)?$", spec), (
                f"Invalid date+time spec: {repr(spec)} ."
                " Specify time as 'YYYY-MM-DD hh:mm:ss[.msec]'"
            )
            return datetime.fromisoformat(spec)
        else:
            return datetime.now()


    def hash(self, hashalgo=hashlib.sha1, data:bytes|None=None):
        """ Produce a hash of supplied data. If data is literal `None`, then a basic hash based on system time is produced.

        Default hash is sha1. Find other has functions from `hashlib` in the Python standard library.
        """
        hashobj = hashalgo()
        if data is None:
            data = bytes(self.date().isoformat(), 'utf-8')
        hashobj.update(data)
        return hashobj.hexdigest()


    def sleep(self, duration):
        """ Sleep for the given duration, in seconds
        """
        time.sleep(duration)


class FileSystemPysh:
    # Passthroughs
    Path = pathlib.Path
    isdir = os.path.isdir
    isfile = os.path.isfile
    remove = os.remove

    def __init__(self, topfile):
        self._topfile = pathlib.Path(topfile)
        self._topdir = self._topfile.parent


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


    def makedirs(self, path):
        """ Make directories down specified path, no error if they already exist
        """
        os.makedirs(path, exist_ok=True)


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
        os.system(f"sudo mv {filename} {filepath}")


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


    def parse(self, argv:list[str]|None=None):
        """ Parse arguments as currently defined
        """
        return self._parser.parse_args(argv)


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

