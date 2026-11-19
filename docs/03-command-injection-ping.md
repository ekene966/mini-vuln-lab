# Challenge 3: OS Command Injection — "Ping" Diagnostics Tool

## Where
`app.py`, the `/diagnostics` route.

## The bug
The diagnostics page takes a `host` value from the user and drops it
straight into a shell command:

```python
cmd = f"ping -c 1 {host}"
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
```

Because `shell=True` is used with a string built from user input, shell
metacharacters in `host` are interpreted by the shell, not treated as a
plain hostname.

## Exploit
On the diagnostics form, submit a host value of:

```
127.0.0.1; id
```

or

```
127.0.0.1 && whoami
```

The shell runs `ping -c 1 127.0.0.1`, then — because of the `;` or `&&`
— also runs the second command (`id` / `whoami`), and its output is
returned in the page alongside the ping output. Any shell command the
attacker chooses now executes with the same privileges as the Flask
process.

## Impact
Remote code execution. In this lab that means reading files, listing
processes, etc. as the user running `python app.py`. On a real server
with this bug, it's a path to full compromise of the host.

## Fix
Never build a shell command from untrusted input. Two safer approaches,
in order of preference:

1. Avoid the shell entirely — call the underlying library directly, or
   pass arguments as a list with `shell=False` so there's no shell to
   interpret metacharacters:

   ```python
   subprocess.run(["ping", "-c", "1", host], shell=False, ...)
   ```

   This alone still lets an attacker pass `host` values ping will
   accept but that aren't real hosts, so it should be paired with:

2. Validate the input against a strict allow-list before using it at
   all (e.g., a regex for a valid IPv4/IPv6 address or hostname), and
   reject anything that doesn't match.
