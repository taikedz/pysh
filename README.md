# Py/Sh - Use python instead of shell

Mini-library to just set up a python replacement for shell scripting with the nice-to-haves

Licensed under MIT License, do what you want with it (just retain the copyright notice with the file).

## Motivation

Rather than write a lot of complicated shell scripting with its weird argument pass-arounds and global variables, lack of rich types, exception-based error handling, and all that, simply use python.

PySh provides common system scripting utilities in a single object for your convenience, with user interaction utilities, script path resolution, and more.

Can be used, for example, for install scripts, setup utilities, and more.

* Provides quick-usage argument definitions with minimal boilerplate
* Provides a preconfigured logging utility with out-of-the-box date and time stamps, and optional files
* Minimal boilerplate access to shell calls (no capture) and commands (capturing output)
* Provides easy access to asset files that reside with the script file, independent of what the current working directory is
    * this is geared towards deployment/installation helper scripts, or scripts that use templates
* Fast access to commonly useful utilites in a single namespace on `PYSH.fs.*` such as `glob()`, `isdir`/`isfile` checking, and others

## Usage

Add it to your project, or to your pythonpath.

```sh
PYSHVER=v0.3.0 # Adjust for your desired version
curl "https://raw.githubusercontent.com/taikedz/pysh/refs/tags/$PYSHVER/pyshlib.py" > myproject/pyshlib.py
```

Import it, and use its handy implementations.

Using python instead of raw shell scripting is now a .... piece o' pysh. (_unapologetic_)

## `pyshlib` library

The main part of the `pyshlib` utility is the tooling added in the sidecar library.

Add it to yoru project then begin a script thus:

```python
import pyshlib

def main():
    Sys = pyshlib.System() # use Pyshlib utilities
    ...

    ... # your implementation


# Nicer CLI behaviour
pyshlib.Main(main, ename=__name__)
```

Try viewing help:

```python
help(pyshlib)
```

## Limitations

Scripts that rely on a series of `sudo` calls _may_ cause each one to require a password, due to each being in a new subshell. This is governed by the runtime sudo implementation.

## Example

A preview example can be found in [./example.md](example.md)
