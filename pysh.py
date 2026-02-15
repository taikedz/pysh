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
        /



pyshlib.main_wrap(main)
