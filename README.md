# Py/Sh - Use python instead of shell

Script to just set up a python replacement for shell scripting with the nice-to-haves

Rather than write a lot of complicated shell scripting with its weird argument pass-arounds and global variables, lack of rich types, exception-based error handling, and all that, simply use python.

PySh provides common system scripting utilities in a single object for your convenience, with user interaction utilities, script path resolution, and more.

## Usage

Install it

```sh
./install.sh
```

Use it anywhere

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
def main():
    HERE.args.positionals("+") # at least one positional argument.
    HERE.args.flags("verbose", "--unsafe") # come out as "--verbose" and "--unsafe"
    HERE.args.options(host="tower", user="sm", port=22)
    args = HERE.args.parse()

    assert HERE.user.confirm("Are you sure?"), "Abort" # automatically exits with status 1

    status, stdout, stderr = HERE.process(
        ["ssh", "-p", str(args.port), f"{args.user}@{args.host}"] + HERE.shjoin(args.positionals),
        text=True
        )

    assert status == 0, f"Could not run remote command:\n{stderr}"
    print(stdout)
```

