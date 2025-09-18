#!/usr/bin/env python3
"""Download selected Argos Translate language pairs (.argosmodel) into models/argos.

Usage:
  python scripts/download_argos_packages.py --pairs en:pt en:es pt:en

If no pairs provided, defaults to common set: en:pt en:es pt:en es:en.
Respects corporate SSL issues: if download fails, prints manual instructions.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
import argostranslate.package

DEFAULT_PAIRS = ["en:pt", "pt:en", "en:es", "es:en"]
TARGET_DIR = Path("models/argos")

def parse_pairs(pairs: list[str] | None) -> list[tuple[str,str]]:
    if not pairs:
        pairs = DEFAULT_PAIRS
    out: list[tuple[str,str]] = []
    for p in pairs:
        if ":" not in p:
            print(f"Ignoring invalid pair '{p}' (expected from:to)")
            continue
        a,b = p.split(":",1)
        out.append((a.strip(), b.strip()))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", nargs="*", help="Language pairs from:to (e.g. en:pt pt:en)")
    args = ap.parse_args()

    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    try:
        print("Updating Argos package index...")
        argostranslate.package.update_package_index()
    except Exception as e:
        print(f"WARNING: Could not update index ({e}). Will attempt offline matching.")

    needed = set(parse_pairs(args.pairs))
    print(f"Will attempt to download {len(needed)} pairs: {', '.join(f'{a}->{b}' for a,b in needed)}")

    available = []
    try:
        available = argostranslate.package.get_available_packages()
    except Exception as e:
        print(f"ERROR: Cannot fetch available packages list: {e}")
        print("If you are behind corporate SSL, manually download .argosmodel files and place them in models/argos/")
        sys.exit(1)

    success = True
    for pkg in available:
        pair = (pkg.from_code, pkg.to_code)
        if pair in needed:
            try:
                dest_tmp = pkg.download()
                dest_path = TARGET_DIR / Path(dest_tmp).name
                if not dest_path.exists():
                    Path(dest_tmp).replace(dest_path)
                print(f"✔ Downloaded {pair[0]}->{pair[1]} -> {dest_path.name}")
                needed.remove(pair)
            except Exception as e:
                print(f"✖ Failed {pair[0]}->{pair[1]}: {e}")
                success = False

    if needed:
        print("Remaining pairs not found or failed:")
        for a,b in needed:
            print(f"  - {a}:{b}")
        print("You can manually fetch them from: https://www.argosopentech.com/argospm/index/")
    if not success:
        sys.exit(1)
    print("All requested Argos packages processed.")

if __name__ == "__main__":
    main()
