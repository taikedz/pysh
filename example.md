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


# `ename` allows conventional check for `__main__`
pyshlib.Main(main, ename=__name__)

```

