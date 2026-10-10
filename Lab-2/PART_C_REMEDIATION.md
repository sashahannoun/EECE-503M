# Lab 2 — Part C Remediation (Sacha Hannoun, 202404910)

Fixed files from the Meridian Service Desk app. Original paths in the project:

| File here        | Original path                         | Layer | Change |
|------------------|---------------------------------------|-------|--------|
| nginx.conf       | lab/nginx.conf                        | 1     | `^~ /media/` block: types{} + octet-stream + Content-Disposition attachment + nosniff — uploads served inert |
| lab.env          | lab/lab.env                           | 2/3   | HELPDESK_VALIDATE_ATTACHMENT_TYPES=True, MERIDIAN_DEBUG=False |
| validators.py    | src/helpdesk/validators.py            | 2     | allowlist by extension, reject multi-dot filenames, verify image bytes with PIL |
| models.py        | src/helpdesk/models.py                | 2     | both attachment_path methods store uploads under a random uuid name |
| staff.py         | src/helpdesk/views/staff.py           | 2     | download_attachment: resolve path then confirm it stays inside MEDIA_ROOT (commonpath); reject with generic error |

Verified post-fix: traversal returns "Invalid path"; .svg and shell.php.png uploads
rejected at the form; allowed uploads stored under a random filename; media files
served as octet-stream downloads.
