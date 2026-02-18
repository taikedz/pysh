# Rewrite thoughts

* Instead of a catch-all object, provide useful modules:
    * Files (filesystem items)
        * (incl files near the running script)
        * (templating)
        * don't try to provide all manner of utilities passthrus
    * Files (templating, )
    * Log (for the sane logger)
    * Args (for the short-handed argument parser)
    * Shell (shell and subprocess access)
    * User (user interactions, querying, etc)
    * Fprint (adds colour, respects `NO_COLOR`, includes prettyprint)

## Example usage

```python
import pyshlib

FS = pyshlib.Files(__file__)
LOG = pyshlib.Log()

def main():
    parser = pyshlib.Args()
    parser.positionals(command=["start", "stop", "logs"], rest="subcommand", nargs="*")
    parser.flags("--verbose")
    parser.options(reqs_file="", venv_name="")
    args = parser.parse()

    if args.reqs_file:
        shell = Venv(venv_name, reqs_file)
    else:
        shell = PyshShell()

    match command:
    case "start":
        LOG.info("Start service")
        cmd = "./bin/service start"
        LOG.debug(cmd)
        return shell.shell(cmd)

    case "stop":
        LOG.info("Stop service")
        cmd = "./bin/service stop"
        LOG.debug(cmd)
        return shell.shell(cmd)

    case "logs":
        status, stdout, stderr = shell.cmd(["./bin/service", "logs"])
        assert status > 0, f"FAIL\n{stderr}"
        comp = PyshCompare(args.subcommand)
        retained = [line for line in stdout.split("\n")
            if (True if not args.subcommmand else are_any_of(args.subcomand, in_any_of=[line]) ) ]
        print("\n---\n".join(retained))


class Venv(pyshlib.PyshShell):
    def __init__(self, reqfile, venvdir):
        self._venvdir = venvdir

        if not filesys.os.isdir(venvdir):
            self.shell(f"python3 -m venv '{venvdir}'")

        if reqfile:
            self.venv_shell(f"pip install {reqfile}")

    def shell(self, shellscript):
        if self._venvdir:
            PyshShell.shell(self, f"""
                . "{self._venvdir}"
                {shellscript}
                """)
        else:
            PyshShell.shell(shellscript)


pyshlib.main_wrap(main)
```
