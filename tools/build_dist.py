#!/usr/bin/env python3
"""Package each skill as dist/<skill>.zip (the folder at the zip root), ready to
upload as a custom skill in the Claude apps or through the Skills API.

    python tools/build_dist.py
"""
import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, "skills")
DIST = os.path.join(ROOT, "dist")


def main():
    os.makedirs(DIST, exist_ok=True)
    for name in sorted(os.listdir(SKILLS)):
        src = os.path.join(SKILLS, name)
        if not os.path.isfile(os.path.join(src, "SKILL.md")):
            continue
        out = os.path.join(DIST, name + ".zip")
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            for root, dirs, files in os.walk(src):
                dirs[:] = sorted(d for d in dirs if d != "__pycache__")
                for f in sorted(files):
                    full = os.path.join(root, f)
                    z.write(full, os.path.join(name, os.path.relpath(full, src)))
        print("%s (%d KB)" % (os.path.relpath(out, ROOT), os.path.getsize(out) // 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
