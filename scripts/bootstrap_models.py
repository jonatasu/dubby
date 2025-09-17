from __future__ import annotations

"""
Optional helper to pre-download translation packages for Argos Translate.
"""


def main():
    try:
        import argostranslate.package as pkg  # type: ignore
    except Exception:
        print("Argos Translate not installed. Skipping.")
        return

    try:
        available = pkg.get_available_packages()
        targets = [("en", "pt"), ("pt", "en")]
        for fr, to in targets:
            matches = [p for p in available if getattr(p, "from_code", None) == fr and getattr(p, "to_code", None) == to]
            if not matches:
                continue
            p = matches[0]
            print(f"Installing Argos package {fr}->{to}...")
            pkg.install_from_path(p.download())
    except Exception:
        print("Could not bootstrap Argos packages.")


if __name__ == "__main__":
    main()
