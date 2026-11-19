# MiniVulnLab

A small, intentionally vulnerable Flask web app built for hands-on
security training. It ships three real, exploitable vulnerabilities from
the OWASP Top 10 family, each with its own write-up covering the bug,
the exploit, the impact, and the fix.

**Run this only on localhost or an isolated lab network. Never deploy it
anywhere reachable from the internet — it is deliberately insecure.**

## Why this exists

Most "vulnerable app" projects you run are black boxes — you attack them
without necessarily understanding the code behind the bug. This one is
small enough to read end to end, so it doubles as practice for *finding*
vulnerabilities by reading source, not just exploiting a known target.

## Challenges

| # | Vulnerability | Route | Write-up |
|---|---|---|---|
| 1 | SQL injection — authentication bypass | `/login` | [docs/01-sqli-login-bypass.md](docs/01-sqli-login-bypass.md) |
| 2 | IDOR — broken access control | `/profile?id=` | [docs/02-idor-profile.md](docs/02-idor-profile.md) |
| 3 | OS command injection | `/diagnostics` | [docs/03-command-injection-ping.md](docs/03-command-injection-ping.md) |

Each doc includes a working payload, an explanation of why it works, and
a corrected version of the vulnerable code.

## Setup

```bash
git clone <this-repo-url>
cd mini-vuln-lab
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

The app starts at `http://127.0.0.1:5000`. Seed accounts (all
intentionally weak, for lab use only):

| Username | Password |
|---|---|
| admin | S3cureAdminPass! |
| alice | alice123 |
| bob   | bobpassword |

## Stack

Python 3, Flask, SQLite — no external services required.

## Scope / disclaimer

This project is for personal security education and portfolio purposes.
It is not a product and carries no warranty. The vulnerabilities are
planted on purpose; do not reuse these code patterns in anything real.
