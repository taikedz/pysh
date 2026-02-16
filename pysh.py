#!/usr/bin/env python3

""" Example usage of pyshlib

Implements the `pysh` script as a python script.
Also implements additional options which would have been harder to do nicely in bash
"""

from files import pyshlib

PYSH = pyshlib.PySh(__file__)

def main():
    PYSH.args.flags("venv")
    PYSH.args.options(venv_name=".venv", requirements="")
    PYSH.args.positionals("target")
    args = PYSH.args.parse()

    target = PYSH.fs.Path(args.target)

    if not PYSH.fs.exists(target):
        PYSH.fs.cp(PYSH.fs.localpath("files/base.py"), args.target)

    if not PYSH.fs.exists(target.parent/"pysh.py"):
        PYSH.fs.cp(PYSH.fs.localpath("files/pysh.py"), target.parent/"pysh.py")

    ignorefile = f"{target.parent}/.gitignore"
    if ( PYSH.fs.isfile(ignorefile)
         and PYSH.shell(f"""grep -q '*.pyc' "{ignorefile}" """) != 0
        ):
        with open(ignorefile, 'a') as fh:
            fh.write("*.pyc\n")

    if args.venv:
        prep_venv(target.parent, args.venv_name, args.requirements)

        targetsh = f"{target}.sh"
        if not PYSH.fs.isfile(targetsh):
            data = PYSH.fs.open_replacing(PYSH.fs.localpath("files/run.sh"), {"TARGET": str(target)})
            with open(targetsh, 'w') as fh:
                fh.write(data)
            PYSH.shell(f"chmod 755 {targetsh}")


def prep_venv(target_dir, venv_name, req_file):
    if not PYSH.fs.isdir(target_dir/venv_name):
        PYSH.shell(f"python3 -m venv {venv_name}")
    if req_file and PYSH.fs.isfile(req_file):
        PYSH.shell(f"""
        set -e
        . {venv_name}/bin/activate
        pip install -r {req_file}
        """)
    else:
        PYSH.log.warning(f"Could not find {repr(req_file)}")

# Wrap the main function so that stacktraces are suppressed
# Nicer for the user. Can be overridden withby setting `PY_ERRORS=true`
pyshlib.main_wrap(main)
