"""Convert Qt Designer .ui files into Python modules.

Every ``.ui`` file below ``ui/forms`` is converted with the same relative path
below ``ui/generated``. Generated files must not be edited by hand.
"""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys


UI_DIR = Path(__file__).resolve().parent
FORMS_DIR = UI_DIR / "forms"
GENERATED_DIR = UI_DIR / "generated"


def find_uic_command() -> str:
    """Locate the PySide6 UI compiler installed with the active environment."""
    command = shutil.which("pyside6-uic")
    if command:
        return command

    scripts_dir = Path(sys.executable).resolve().parent / "Scripts"
    executable = scripts_dir / "pyside6-uic.exe"
    if executable.is_file():
        return str(executable)

    raise FileNotFoundError(
        "pyside6-uic was not found. Install PySide6 in the active Python environment."
    )


def convert_form(form_path: Path) -> None:
    """Convert one Designer form and raise an error if conversion fails."""
    relative_path = form_path.relative_to(FORMS_DIR).with_suffix(".py")
    output_path = GENERATED_DIR / relative_path
    output_path.parent.mkdir(parents=True, exist_ok=True)

    command = [
        find_uic_command(),
        str(form_path),
        "-o",
        str(output_path),
    ]
    subprocess.run(command, check=True)
    print(f"Converted: {form_path.relative_to(UI_DIR)} -> {output_path.relative_to(UI_DIR)}")


def main() -> int:
    if not FORMS_DIR.is_dir():
        print(f"UI source directory does not exist: {FORMS_DIR}", file=sys.stderr)
        return 1

    forms = sorted(FORMS_DIR.rglob("*.ui"))
    if not forms:
        print(f"No .ui files found in: {FORMS_DIR}", file=sys.stderr)
        return 1

    try:
        for form_path in forms:
            convert_form(form_path)
    except (FileNotFoundError, subprocess.CalledProcessError) as error:
        print(f"UI conversion failed: {error}", file=sys.stderr)
        return error.returncode or 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
