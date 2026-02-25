# (C) 2026 TaiKedz
# Conveyed to you under the terms of the MIT License. See LICENSE.txt or
# https://mit-license.org/ . Essentially: do what you want with it, but
# please do retain this copyright notice.

from datetime import datetime
import glob
import hashlib
import logging
import os
import platform
import re
import shutil
import sys
import shlex
import subprocess
import argparse
import pathlib
import tempfile
import time
from typing import Any

# Current version - a series of numbers, optionally 'dev' at the end if not-released
PYSH_VERSION=(0,3,1,)

""" Convenience suite for system scripting in python.
Add a single-import and use classes/functions with helpful defaults.

Import this library to gain fast access to common desired functionality.

Provided as a single sidecar file for your convenience.
"""

def Main(_func, error_mask="PY_ERRORS", ename=None):
    """Wrap your main function to suppress tracebacks (nicer for users)

    Specify an error mask, e.g. `PY_ERRORS` - if `export PY_ERRORS=true` is set in environment,
    then tracebacks are printed.

    e.g.

        def main():
            ... # implementation here ...

        pyshlib.Main(main, ename=__name__)
    """
    try:
        if ename is None or ename == "__main__":
            _func()
    except (KeyboardInterrupt,Exception) as e:
        if os.getenv(error_mask, "false").lower() == "true":
            raise
        else:
            print(e)
            exit(1)


class System:
    def env(self, name, defval=None):
        """ Get an environment variable
        """
        return os.getenv(name, defval)


    def shjoin(self, tokens):
        """ Join shell tokens
        """
        return shlex.join(tokens)


    def cmd(self, command, text=True) -> tuple[int, str|bytes, str|bytes]:
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
        """ Return the platform, operating system name and version as of /etc/hosts (Linux and Unix only)

        E.g. ("Linux", "Ubuntu", "24.04") or ("Windows", "Enterprise", "11")
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



class _LogBase(logging.Logger):
    ERROR = logging.ERROR
    WARN = logging.WARN
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    _FORMAT_STRING = '%(asctime)s | %(levelname)s | %(name)s : %(message)s'


class Log(_LogBase):

    def __init__(self, name="main", fmt_string=_LogBase._FORMAT_STRING, level=_LogBase.WARN, console=True, files=None, file_level=_LogBase.DEBUG):
        logging.Logger.__init__(self, name, _LogBase.DEBUG)
        formatter_obj = logging.Formatter(fmt_string)

        if files is None:
            files = []
        elif isinstance(files, str):
            files = [files]

        def _add_stream(handler:logging.Handler, local_level, **kwargs):
            handler = handler(**kwargs)
            handler.setLevel(local_level)
            handler.setFormatter(formatter_obj)
            self.addHandler(handler)

        if console is True:
            _add_stream(logging.StreamHandler, local_level=level, stream=sys.stdout)

        for filepath in files:
            _add_stream(logging.FileHandler, file_level, filename=filepath)


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



class Filesys:
    def __init__(self, asset_root):
        """Create a filesystem helper using `topfile` path as the root for assets
        """
        self._script = pathlib.Path(asset_root)
        self._assetsdir = self._script.parent
        self.scriptname = self._script.name


    def tempfile(self, dir_abspath=None) -> str:
        """ Create a temp file.

        If dir is specified, makes the temp file in that directory
        If text is set to False,
        """
        if dir_abspath:
            self.makedirs(dir_abspath)
        _, name = tempfile.mkstemp(dir=dir_abspath)
        return name


    def cp(self, src, dst, dirmode=511):
        """ Make parent directories, and copy a file to destination
        """
        os.makedirs(pathlib.Path(dst).parent, exist_ok=True, mode=dirmode)
        shutil.copy(src, dst)


    def mv(self, src, dst, dirmode=511):
        """ Make parent directories, and move a file to destination
        """
        os.makedirs(pathlib.Path(dst).parent, exist_ok=True, mode=dirmode)
        shutil.move(src, dst)


    def asset_path(self, path='') -> pathlib.Path:
        """ Resolve a path starting in the same directory as current script
        """
        return self._script / path


    def expand_path(self, path) -> str:
        """ Expand the user component of a path

        Use python formatting notation to substitute environment variables
        e.g. the following lead to the same result

            expand_path("~/Documents/{USER}")
            expand_path("/home/{USER}/Documents/{USER}")
            expand_path("{HOME}/Documents/{USER}")
        """
        path = os.path.expanduser(path)
        return path.format(os.environ)


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


    def glob(self, pat) -> list[str]:
        return glob.glob(pat)


class Color:
    def __init__(self):
        noclr = os.getenv("NO_COLOR", "0") == "1"
        colors = {
            "RST":"0",
            "RED":"31",
            "GRN":"32",
            "YELW":"33",
            "BLUE":"34",
            "MAUV":"35",
            "TEAL":"36",
        }
        self._colors = {k:('' if noclr else f"\033[{v};1m") for k,v in colors.items()}

    def clr(self, clr, txt):
        if clr not in self._colors:
            return txt
        return f"{self._colors.get(clr)}{txt}{self._colors.get('RST')}"

    def print(self, text, color):
        print(self.clr(color, text))


class User:
    """ Prompt user and display information. Uses Color class.
    """
    def read_user(self, prompt) -> str:
        """ Ask a user for input
        """
        print(prompt, end='', flush=True)
        res = sys.stdin.readline()
        return res.strip("\n")

    def ask(self, prompt) -> str:
        return self.read_user(Color().clr("BLUE", prompt))


    def confirm(self, prompt) -> bool:
        """ Ask a user for a yes/no response as 'y' or 'yes'
        Return True if y/yes , False if n/no, or ask again if neither.
        """
        res = ""
        while res.lower() not in ["y", "yes", "no", "n"]:
            res = self.read_user(f"{Color().clr("TEAL", prompt)} y/N> ")
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

        res = self.read_user(Color().clr("TEAL", prompt))
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

class LineHandler:
    def __init__(self, data:str|list[str]):
        if isinstance(data, str):
            data = data.split("\n")
        self._data:list[str] = data

    def match(self, pattern, regex=False, group:int|None=None) -> 'LineHandler':
        if regex:
            if group is None:
                extract = lambda m,s: s
            else:
                extract = lambda m,s: m.group(group)
            pat = re.compile(pattern)
            return LineHandler([line for line in self._data if extract(re.match(pat, line), line)])
        else:
            return LineHandler([line for line in self._data if pattern in line])

    def exclude(self, pattern, regex=False) -> 'LineHandler':
        if regex:
            pat = re.compile(pattern)
            return LineHandler([line for line in self._data if re.match(pat, line) is None])
        else:
            return LineHandler([line for line in self._data if pattern not in line])

    def replace(self, target, replacement, regex=False) -> 'LineHandler':
        if regex:
            pat = re.compile(target)
            return LineHandler([re.sub(pat, replacement, line) for line in self._data])
        else:
            return LineHandler([line.replace(target, replacement) for line in self._data])

class ArgumentParser:
    """
    A quick-spec argument parser.

        parser = pysh.ArgumentParser("cmd prefix tokens")
        parser.positionals("arg1", "arg2", "arg3")
        args = parser.parse()
        print(args.arg2)
    """
    def __init__(self, command_leadup=None, **k):
        self._parser = argparse.ArgumentParser(command_leadup, **k)


    def parse(self, argv):
        """ Parse arguments as currently defined
        """
        assert argv is not None, f"Use parse parse_argv() to parse top-level command line arguments"
        return self._parser.parse_args(argv)


    def parse_argv(self):
        """ Parse system command line arguments
        """
        return self._parser.parse_args()


    def add_argument(self, *a, **k):
        """ Add a raw argument to the parser. See argparse.ArgumentParser.add_argument(...)
        """
        self._parser.add_argument(*a, **k)


    def args(self, *names, **choices:list[str]):
        """ Add named positional arguments

        For positional arguments with a value list, this constrains the discrete available choices
        """
        for name in names:
            self._parser.add_argument(name)

        for k,v in choices.items():
            if isinstance(v, list):
                self._parser.add_argument(k, choices=v)
            else:
                raise ValueError(f"Positional {repr(k)} must take a list of choices, not {repr(v)}")

    def moreargs(self, name, nargs="+", help="Target items"):
        """ Declare existence of more optional arguments.

        Use `nargs="+"` to specify one or more ; use `nargs="*"` to specify zero or more
        """
        self.add_argument(name, nargs=nargs, help=help)


    def flags(self, *flags:str):
        """ Add boolean flags. During runtime, unset flags are false, set flags are true
        """
        for flag in flags:
            flag = f"--{flag.lstrip("-/")}" # force 2-dash convention
            self._parser.add_argument(flag, action="store_true")


    def options(self, **opts:Any):
        """ Add options with default values

        The default value is added as-is, with a type coercion of the same type as value, except in the case of a tuple

        If the default value of an item is a tuple, this indicates a set of fixed choices, and the default value will be the first in the tuple.
        """
        defval:tuple|Any
        for flag, defval in opts.items():
            flag = f"--{flag.lstrip("-/")}" # force 2-dash convention

            if isinstance(defval, tuple):
                self._parser.add_argument(flag, default=defval[0], choices=defval, type=type(defval[0]))
            else:
                self._parser.add_argument(flag, default=defval, type=type(defval))



class Time:

    def __init__(self, dtspec=None):
        if dtspec is None:
            self._thetime = datetime.now()
        else:
            self._thetime = datetime.fromisoformat(dtspec)


    def sleep(self, duration):
        time.sleep(duration)


    def date(self):
        return self._thetime


    def seconds_since(self, date:datetime):
        return (self._thetime - date).total_seconds()
