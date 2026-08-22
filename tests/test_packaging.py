import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class InstalledWheelTemplateTests(unittest.TestCase):
    def test_installed_wheel_exposes_the_default_yard_template(self):
        repository = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as raw_temp:
            root = Path(raw_temp)
            wheels = root / "wheels"
            installed = root / "installed"
            wheels.mkdir()
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "--disable-pip-version-check",
                    "wheel",
                    "--no-deps",
                    "--no-build-isolation",
                    "--wheel-dir",
                    str(wheels),
                    str(repository),
                ],
                cwd=root,
                check=True,
                capture_output=True,
                text=True,
            )
            wheel = next(wheels.glob("system_gap_master-*.whl"))
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "--disable-pip-version-check",
                    "install",
                    "--no-deps",
                    "--target",
                    str(installed),
                    str(wheel),
                ],
                cwd=root,
                check=True,
                capture_output=True,
                text=True,
            )
            environment = os.environ.copy()
            environment["PYTHONPATH"] = str(installed)
            smoke = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    (
                        "from system_gap_master.instance_manager import "
                        "_default_template_root, load_template; "
                        "root = _default_template_root(); "
                        "template = load_template(root); "
                        "assert root.is_dir(); "
                        "assert template.version == '1.6.0'; "
                        "print(root)"
                    ),
                ],
                cwd=root,
                env=environment,
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn("yard_template", smoke.stdout)


if __name__ == "__main__":
    unittest.main()
