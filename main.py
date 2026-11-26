#!/usr/bin/env python3
"""Entrypoint for make.fun competition
u-suzy-one-line-one-laugh-roast-your-fridge-f1063521.

The deliverable is one judged line of text: this program writes it to
/output/entry.txt as exact UTF-8 bytes, atomically, with mode 0644, and then
reads it back to prove the artifact on disk is the artifact the gate will see.

Rules that shape this file (kit RULES.txt, "The gate"):
  * /output/entry.txt must be UTF-8 text of 1 to 200 characters, not only
    white space -- otherwise the entry is never judged and takes no prize;
  * the grader refuses a mode-600 file in /output (tempfile.mkstemp creates
    0600), so chmod 0644 must happen BEFORE os.replace;
  * /output must hold only the required artifact;
  * the exact bytes ship: no trailing newline.

Standard library only, no network, no secrets.
"""

from __future__ import annotations

import hashlib
import os
import stat
import sys
import tempfile

# --- the entry -----------------------------------------------------------------
# A single line roasting a phone. Subject and butt of the joke: the phone and
# its own nagging behaviour, not generic complaining about technology.
ENTRY = (
    "My phone warns me to hold it farther from my face, "
    "apparently so it can keep ruining my eyes at a safer distance."
)

DEFAULT_OUT = "/output/entry.txt"
MAX_CHARS = 200
TMP_PREFIX = ".entry-"
TMP_SUFFIX = ".tmp"


def entries_out_path(argv: list[str]) -> str:
    """The artifact path: /output/entry.txt, or an explicit override."""
    if len(argv) >= 3 and argv[1] == "--out":
        return argv[2]
    return DEFAULT_OUT


def validate(text: str) -> bytes:
    """Return the exact bytes to ship, or raise ValueError if the gate fails."""
    if not isinstance(text, str):
        raise ValueError("entry is not text")
    chars = len(text)
    if chars < 1:
        raise ValueError("entry is empty")
    if chars > MAX_CHARS:
        raise ValueError(f"entry is {chars} characters, over the {MAX_CHARS} cap")
    bad = [c for c in text if ord(c) < 0x20 or ord(c) == 0x7F]
    if bad:
        raise ValueError("entry carries a control character (incl. any newline)")
    if not text.strip():
        raise ValueError("entry is only white space")
    data = text.encode("utf-8")
    if data.decode("utf-8") != text:
        raise ValueError("entry does not round-trip as UTF-8")
    return data


def sweep(directory: str) -> None:
    """Remove temp files this program left behind, so /output holds only the
    required artifact even after an earlier run was killed mid-write."""
    try:
        names = os.listdir(directory)
    except OSError:
        return
    for name in names:
        if name.startswith(TMP_PREFIX) and name.endswith(TMP_SUFFIX):
            try:
                os.unlink(os.path.join(directory, name))
            except OSError:
                pass


def write_atomically(path: str, data: bytes) -> None:
    """Write data to path via a temp file in the same directory, mode 0644."""
    directory = os.path.dirname(os.path.abspath(path)) or "."
    os.makedirs(directory, exist_ok=True)
    sweep(directory)
    fd, tmp = tempfile.mkstemp(dir=directory, prefix=TMP_PREFIX, suffix=TMP_SUFFIX)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        # Before the rename: mkstemp made this 0600, and the grader refuses a
        # 0600 artifact in /output.
        os.chmod(tmp, 0o644)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def verify_on_disk(path: str, data: bytes) -> tuple[int, int]:
    """Read the artifact back; return (mode, bytes). Raise if it is not the
    exact artifact the runner must see."""
    with open(path, "rb") as handle:
        on_disk = handle.read()
    mode = stat.S_IMODE(os.stat(path).st_mode)
    if on_disk != data:
        raise ValueError(f"artifact on disk differs from the entry ({len(on_disk)} bytes)")
    if mode != 0o644:
        os.chmod(path, 0o644)
        mode = stat.S_IMODE(os.stat(path).st_mode)
        if mode != 0o644:
            raise ValueError(f"artifact mode is {mode:04o}, not 0644")
    return mode, len(on_disk)


def main(argv: list[str]) -> int:
    path = entries_out_path(argv)
    try:
        data = validate(ENTRY)
        write_atomically(path, data)
        mode, size = verify_on_disk(path, data)
    except (ValueError, OSError) as exc:
        print(f"entry failed: {exc}", file=sys.stderr)
        return 1

    print(f"wrote {path}")
    print(f"bytes={size} chars={len(ENTRY)} mode={mode:04o}")
    print(f"sha256={hashlib.sha256(data).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
