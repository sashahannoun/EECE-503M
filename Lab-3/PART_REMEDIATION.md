# Lab 3 — Remediation (Sacha Hannoun, 202404910)

All four fixes are in `staff.py` (original path: src/helpdesk/views/staff.py).

| Vulnerability | Function | Fix |
|---|---|---|
| Broken access control (IDOR) | view_ticket, export_ticket | Check `HelpdeskUser(request.user).can_access_queue(ticket.queue)`; deny with 403 if not allowed |
| Privilege escalation | promote_user | Require `request.user.is_superuser`; deny with 403 otherwise |
| CSRF | change_email | Removed `@csrf_exempt` so Django's CSRF token check applies |
| Command injection | export_ticket | Removed `subprocess(shell=True)`; the file is written in Python and the label is used only as a path-stripped filename |

Verified after fix: ticket 4 denied to rmasri (403), promote refuses a non-admin (403),
tokenless POST rejected (403 CSRF), and `label=x; id #` returns the ticket file with no `id` output.
