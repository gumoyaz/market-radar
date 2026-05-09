from __future__ import annotations

import importlib
from pathlib import Path

import app  # noqa: F401


def module_available(name: str) -> tuple[bool, str]:
    try:
        importlib.import_module(name)
        return True, "ok"
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def main() -> None:
    candidates = [
        Path(r"C:\OpenAPI"),
        Path(r"C:\Kiwoom"),
        Path(r"C:\Program Files\Kiwoom"),
        Path(r"C:\Program Files (x86)\Kiwoom"),
    ]

    print("Kiwoom install path check")
    found_any = False
    for path in candidates:
        exists = path.exists()
        print(f"- {path}: {'FOUND' if exists else 'missing'}")
        found_any = found_any or exists

    print()
    print("Python dependency check")
    for name in ["PyQt5", "PyQt5.QAxContainer", "win32com.client", "pythoncom"]:
        ok, detail = module_available(name)
        print(f"- {name}: {'FOUND' if ok else 'missing'} ({detail})")

    print()
    if not found_any:
        print("Result: Kiwoom OpenAPI+ install path not detected.")
    else:
        print("Result: Kiwoom-related install path detected.")


if __name__ == "__main__":
    main()
