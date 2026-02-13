# Py/Sh - Use python instead of shell

Mini-library to just set up a python replacement for shell scripting with the nice-to-haves

## Motivation

Rather than write a lot of complicated shell scripting with its weird argument pass-arounds and global variables, lack of rich types, exception-based error handling, and all that, simply use python.

PySh provides common system scripting utilities in a single object for your convenience, with user interaction utilities, script path resolution, and more.

Can be used, for example, for install scripts, setup utilities, and more.

* Provides quick-usage argument definitions with minimal boilerplate
* Provides a logging utility with out-of-the-box date and time stamps, and optional file
* No-boilerplate access to shell calls (no capture) and commands (capturing output)
* Provides easy access to files that reside with the script file, independent of what the current working directory is
    * this is geared towards deployment/installation helper scripts
* Fast access to commonly useful utilites in a single namespace on `PYSH.fs.*` such as `glob()`, `isdir`/`isfile` checking, and others

## Usage

Install it

```sh
./install.sh
```

Use it anywhere

```sh
# Create a new project, add assets and executable
pysh ./name-of-file.py
```

Run the resulting project

```sh
# Load venv etc, run script
./name-of-file.py.sh arg1 arg2 ...
```

Using python instead of raw shell scripting is now a .... piece o' pysh. (_unapologetic_)

## `pysh` library

The main part of the `pysh` utility is the tooling added in the sidecar library.

In this git repo, run `python3` and then

```python
import files.pysh as pysh # in your project, just "import pysh"
help(pysh)
```

## Limitations

Scripts that rely on a series of `sudo` calls may cause each one to require a password, due to each being in a new subshell. This is governed by the runtime sudo implementation.

## Example

Edit your `main()` function in your main file. You can add succinct argument parsing, access OS information, and more, without tons of imports.

Here's an example of a fictitious installer script. It takes arguments, uses logging, resolves files next to the installer script, and has a verbose mode, all setup within the first few lines and a single import.

```python
# Set a custom log name (set to None for no actual log file)
logname = "my-tools-installation.log"
PYSH = pyshlib.PySh(__file__, logname)

def main():
    # Quickly define some arguments and parse them
    PYSH.args.flags("--verbose", "--web") # bools
    PYSH.args.options("--bindir", "~/.local/bin")
    PYSH.args.positionals(rest="cmds", nargs="*")
    args = PYSH.args.parse()

    if args.verbose:
        # Set a custom log that will display the minutiae
        PYSH.set_log(pyshlib.LogPysh(
            files=logname,
            level=pyshlib.LogLevel.DEBUG,
            file_level=pyshlib.LogLevel.DEBUG
            ))

    if args.cmds:
        # Path expansions
        bindest = PYSH.expandpath(args.bindir)

        mandatory = PYSH.fs.glob(PYSH.fs.localpath()+"/main-bins/*")
        install_these = mandatory + args.cmds

        PYSH.log.debug(f"Into {bindest}/ :")

        for item in install_these:
            # copy from installer's location to deployment location
            localfile = PYSH.localpath(item)
            PYSH.log.debug(f"    Installing {localfile}")

            PYSH.shell(f"cp {localfile} {bindest}/")

    if args.web:
        if osname := PYSH.os_info()[1] in ["Ubuntu", "Debian"]:
            command = "sudo apt-get install apache2"

        elif osname in ["Red Hat", "Fedora"]:
            command = "sudo dnf install httpd"
        else:
            PYSH.log.error("Unsupported OS")
            exit(1)

        print("Installing web server")
        status, stdout, stderr = PYSH.cmd(command)
        # If not success, bails with the output, else, runs silent
        assert status == 0, stderr
        print("Web server successsfully installed")
```

