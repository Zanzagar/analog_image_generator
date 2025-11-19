import subprocess
import sys
from pathlib import Path


def test_geo_rules_script():
    script = Path("scripts/validate_geo_anchors.py")
    result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
