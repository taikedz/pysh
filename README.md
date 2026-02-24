# Py/Sh - Use python instead of shell

Mini-library to just set up a python replacement for shell scripting with the nice-to-haves

Licensed under MIT License, do what you want with it (just retain the copyright notice with the file).

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

Add it to your project, or to your pthonpath. Import it, and use its handy implementations.

Using python instead of raw shell scripting is now a .... piece o' pysh. (_unapologetic_)

## `pyshlib` library

The main part of the `pyshlib` utility is the tooling added in the sidecar library.

Add it to yoru project then begin a script thus:

```python
import pyshlib

def main():
    ... # your implementation


if __name__ == "__main__":
    # Nicer CLI behaviour
    pyshlib.Main(main)
```

Try viewing help:

```python
help(pyshlib)
```

## Limitations

Scripts that rely on a series of `sudo` calls _may_ cause each one to require a password, due to each being in a new subshell. This is governed by the runtime sudo implementation.

## Example

Edit your `main()` function in your main file. You can add succinct argument parsing, access OS information, and more, without tons of imports.

Here's an example of a fictitious installer script. It takes arguments, uses logging, resolves files next to the installer script, and has a verbose mode, all setup within the first few lines and a single import.

```python
# Set a custom log name (set to None for no actual log file)
logname = "my-tools-installation.log"
LOG = pyshlib.Log(files=logname)

FS = pyshlib.Filesys(__file__)
Sys = pyshlib.System()

def main():
    global LOG
    # Quickly define some arguments and parse them
    args = pyshlib.ArgumentParser()
    args.flags("--verbose", "--web") # bools
    args.options("--bindir", "~/.local/bin")
    args.moreargs("target_cmds", nargs="*")
    args = args.parse()

    if args.verbose:
        # Set a custom log that will display the minutiae
        LOG = pyshlib.Log(
            files=logname,
            level=pyshlib.Log.DEBUG,
            file_level=pyshlib.Log.DEBUG
            )

    # Path expansions
    bindest = FS.expand_path(args.bindir)
    install_these = FS.glob(FS.asset_path()+"/main-bins/*")

    if args.target_cmds:
        install_these += args.target_cmds

        LOG.debug(f"Into {bindest}/ :")

    for item in install_these:
        # copy from installer's location to deployment location
        LOG.debug(f"    Installing {item}")

        Sys.shell(f"cp {localfile} {bindest}/")

    if args.web:
        if osname := Sys.os_info()[1] in ["Ubuntu", "Debian"]:
            command = "sudo apt-get install apache2"

        elif osname in ["Red Hat", "Fedora"]:
            command = "sudo dnf install httpd"
        else:
            LOG.error("Unsupported OS")
            exit(1)

        print("Installing web server")
        status, stdout, stderr = Sys.cmd(command)
        # If not success, bails with the output, else, runs silent
        assert status == 0, stderr
        print("Web server successsfully installed")


if __name__ == "__main__":
    pyshlib.Main(main)

```
