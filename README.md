# Py/Sh - Use python instead of shell

Script to just set up a python replacement for shell scripting with the nice-to-haves

Rather than write a lot of complicated shell scripting with its weird argument pass-arounds and global variables, lack of rich types, exception-based error handling, and all that, simply use python.

PySh provides common system scripting utilities in a single object for your convenience, with user interaction utilities, script path resolution, and more.

Can be used, for example, for install scripts, setup utilities, and more.

* Provides quick-usage argument definitions with minimal boilerplate
* Provides easy access to files that reside with the script file, independent of what the current working directory is.
* Provides a logging utility with sane default conifugration

## Usage

Install it

```sh
./install.sh
```

Use it anywPYSH

```sh
# Create project, add assets and executable
pysh path/to/name-of-file.py
```

Run the resulting project

```sh
# Load venv etc, run script
path/to/name-of-file.py.sh arg1 arg2 ...
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

```python
PYSH = pyshlib.PySh(__file__)

def main():
    PYSH.args.positionals("+") # at least one positional argument.
    PYSH.args.flags("verbose", "unsafe") # specify boolean flags "--verbose" and "--unsafe"
    PYSH.args.options(host="server1", user="me", port=22) # specify "--tower" option with default value "server1", etc
    args = PYSH.args.parse()

    assert PYSH.user.confirm("Are you sure?"), "Abort" # automatically exits with status 1 if not "yes" or "y"

    status, stdout, stderr = PYSH.cmd(
        ["ssh", "-p", str(args.port), f"{args.user}@{args.host}"] + PYSH.shjoin(args.positionals),
        text=True
        )

    assert status == 0, f"Could not run remote command:\n{stderr}"
    print(stdout)

    PYSH.shell("sha1sum /etc/hosts|cut -f1") # `shell()` allows piped command chains
```

