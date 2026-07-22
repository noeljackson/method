#!/usr/bin/env python3
"""Print the Noel Method acceptance digest for a ProjectProfile."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from methodlib import profile_payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="print the Noel Method acceptance digest for a ProjectProfile"
    )
    parser.add_argument("profile", type=Path)
    args = parser.parse_args()
    text = args.profile.read_text(encoding="utf-8")
    print(hashlib.sha256(profile_payload(text).encode()).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
