#!/usr/bin/env python3
"""Copy shared/scripts/* into every skill so each skill stays self-contained.

    python tools/sync_shared.py          # copy
    python tools/sync_shared.py --check  # exit 1 if any copy is stale (used in CI)
"""
import filecmp
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "shared", "scripts")
SKILLS = os.path.join(ROOT, "skills")


def main():
    check = "--check" in sys.argv
    stale = []
    for skill in sorted(os.listdir(SKILLS)):
        dest_dir = os.path.join(SKILLS, skill, "scripts")
        if not os.path.isfile(os.path.join(SKILLS, skill, "SKILL.md")):
            continue
        os.makedirs(dest_dir, exist_ok=True)
        for name in sorted(os.listdir(SRC)):
            if not name.endswith(".py"):
                continue
            src, dest = os.path.join(SRC, name), os.path.join(dest_dir, name)
            if not os.path.exists(dest) or not filecmp.cmp(src, dest, shallow=False):
                stale.append(os.path.relpath(dest, ROOT))
                if not check:
                    shutil.copy2(src, dest)
    if check and stale:
        print("Stale copies (run python tools/sync_shared.py):\n  " + "\n  ".join(stale))
        return 1
    print("%d file(s) %s" % (len(stale), "stale" if check else "updated"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
