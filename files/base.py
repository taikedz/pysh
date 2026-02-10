import pysh

HERE = pysh.PySh(__file__)

def main():
    # your scripting here. Example:
    HERE.args.positionals("+")
    HERE.args.flags("--verbose", "--unsafe")
    HERE.args.options(
            ("host", "tower"),
            ("user", "sm"),
            ("port", 22),
        )
    args = HERE.args.parse()

    # TODO - allow '--' separation
    status, stdout, stderr = HERE.process(["ssh", "-p", str(args.port), f"{args.user}@{args.host}", HERE.shjoin(args.positionals)], text=True)

    assert status == 0, f"Could not run remote command:\n{stderr}"
    print(stdout)

# =====

def main_wrap():
    try:
        main()
    except Exception as e:
        if HERE.env("PY_TRACEBACK", "false").lower() == "true":
            raise
        else:
            print(e)
            return 1

main_wrap()
