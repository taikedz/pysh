# Py/Sh - Use python instead of shell

Script to just set up a python replacement for shell scripting with the nice-to-haves

```sh
# Create project, add assets
pysh create name-of-file.py

# Load venv etc, run script
pysh run name-of-file.py
```

## Limitations

Scripts that rely on a series of `sudo` calls may cause each one to require a password, due to each being in a new subshell. This is governed by the runtime sudo implementation.
