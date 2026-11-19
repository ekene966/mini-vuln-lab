# Challenge 2: Insecure Direct Object Reference (IDOR) — Profile Viewer

## Where
`app.py`, the `/profile` route.

## The bug
After logging in, the app reads a user id straight from a query
parameter and fetches that user's record, with no check that the id
belongs to the currently logged-in session:

```python
user_id = request.args.get("id", session.get("uid"))
row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
```

The query itself is safe from SQL injection (it's parameterized) — the
bug is an authorization bug, not an injection bug: the app never checks
*who* is allowed to see *which* record.

## Exploit
1. Log in as `alice` / `alice123`. You land on `/profile?id=2` (or
   wherever alice's id happens to be) and see her own bio.
2. Change the URL to `/profile?id=1`.
3. You now see the `admin` account's bio and ID, despite being logged in
   as alice. No extra authentication was required.

## Impact
Any authenticated user can enumerate ids and read every other user's
profile data — a low-severity example here (just a bio field), but the
same pattern on a real app (invoices, medical records, private messages)
is a serious data-exposure bug, and it's one of the most commonly found
issues in real bug bounty reports.

## Fix
Check that the requested resource actually belongs to (or is permitted
for) the logged-in user before returning it:

```python
user_id = session["uid"]  # ignore any id the client supplies
# or, if viewing others is a legitimate feature, explicitly check
# permissions before returning someone else's record.
```

More generally: never trust a client-supplied identifier to decide what
data to return. Authorization checks belong on the server, scoped to the
authenticated session, every time.
