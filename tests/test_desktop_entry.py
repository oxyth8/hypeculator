import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INSTALL_SCRIPT = PROJECT_ROOT / "scripts" / "install-desktop-entry"
UNINSTALL_SCRIPT = PROJECT_ROOT / "scripts" / "uninstall-desktop-entry"


class DesktopEntryTests(unittest.TestCase):
    def test_user_desktop_entry_installation_and_removal(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            environment = os.environ | {"XDG_DATA_HOME": temporary_directory, "HOME": temporary_directory}
            legacy_file = Path(temporary_directory) / "applications" / "calculator.desktop"
            legacy_file.parent.mkdir(parents=True)
            legacy_file.write_text(f"Exec={PROJECT_ROOT}/.venv/bin/calculator\n")
            subprocess.run([str(INSTALL_SCRIPT)], check=True, env=environment, capture_output=True)

            desktop_file = Path(temporary_directory) / "applications" / "hypeculator.desktop"
            icon_file = Path(temporary_directory) / "icons" / "hicolor" / "512x512" / "apps" / "hypeculator.png"
            content = desktop_file.read_text()
            self.assertIn("[Desktop Entry]", content)
            self.assertIn("Type=Application", content)
            self.assertIn("Name=Hypeculator", content)
            self.assertIn("Comment=Fast and reliable desktop calculator", content)
            self.assertIn("GenericName=Calculator", content)
            self.assertIn(f'Exec="{temporary_directory}/.local/bin/hypeculator"', content)
            self.assertIn("Icon=hypeculator", content)
            self.assertIn("StartupWMClass=hypeculator", content)
            terminal_launcher = Path(temporary_directory) / ".local" / "bin" / "hypeculator"
            self.assertEqual(terminal_launcher.resolve(), PROJECT_ROOT / ".venv" / "bin" / "hypeculator")
            self.assertIn("Terminal=false", content)
            self.assertIn("Categories=Utility;Calculator;", content)

            validator = shutil.which("desktop-file-validate")
            if validator:
                subprocess.run([validator, str(desktop_file)], check=True)

            subprocess.run([str(UNINSTALL_SCRIPT)], check=True, env=environment, capture_output=True)
            self.assertFalse(desktop_file.exists())
            self.assertFalse(icon_file.exists())
            self.assertFalse(legacy_file.exists())
            self.assertFalse(terminal_launcher.exists())
