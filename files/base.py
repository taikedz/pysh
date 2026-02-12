import files.pyshlib as pyshlib

PYSH = pyshlib.PySh(__file__)

def main():
    "your scripting here."

# =====
# Do not remove - this calls your main() function for you
#
# Stack traces are suppressed for user convenience.
# Set PY_ERRORS=true in your environment to print them.
pyshlib.main_wrap(main)
