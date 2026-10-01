#!/usr/bin/env python3
"""Credential helper used only by the isolated publication subprocess."""
import os, re, sys
from pathlib import Path

if 'username' in sys.argv[-1].lower():
    print('x-access-token')
else:
    raw=Path(os.environ['EVENT_BINDING_TOKEN_FILE']).read_text().strip()
    match=re.search(r'(?:github_pat_|gh[pousr]_)[A-Za-z0-9_]+',raw)
    token=match.group(0) if match else raw
    if not token or '\n' in token or '\r' in token:
        raise SystemExit('Invalid credential file')
    print(token)
