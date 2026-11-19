# Challenge 1: SQL Injection — Login Bypass

## Where
`app.py`, the `/login` route.

## The bug
The login handler builds its SQL query with an f-string instead of a
parameterized query:

```python
query = (
    f"SELECT * FROM users WHERE username = '{username}' "
    f"AND password = '{password}'"
)
row = conn.execute(query).fetchone()
```

User input is concatenated directly into the SQL string, so anything the
attacker types becomes part of the query itself.

## Exploit
On the login form, enter:

- Username: `admin' --`
- Password: (anything, it's ignored)

The resulting query becomes:

```sql
SELECT * FROM users WHERE username = 'admin' --' AND password = '...'
```

`--` starts a SQL comment, so everything after it (including the password
check) is ignored. The query now just asks "find the user named admin,"
which always succeeds, logging you in as `admin` with no valid password.

A classic variant that also works here:

- Username: `' OR '1'='1`
- Password: `' OR '1'='1`

This turns the WHERE clause into something always true, returning the
first row in the table regardless of credentials.

## Impact
Full authentication bypass — an attacker becomes any user, including the
admin account, without knowing a password.

## Fix
Use parameterized queries so user input is always treated as data, never
as part of the SQL syntax:

```python
row = conn.execute(
    "SELECT * FROM users WHERE username = ? AND password = ?",
    (username, password),
).fetchone()
```

In a real app, passwords should also never be stored or compared in
plaintext — they should be hashed with a slow, salted algorithm (e.g.
bcrypt or argon2) and compared with a constant-time check.
