"""Regression checks for the runtime experiment's evidence and input guards."""

import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tool.ci import runtime_probe


class RuntimeProbeTest(unittest.TestCase):
    """Keep invalid downloads and partial loading successes from passing."""

    def test_corrupt_archive_never_reaches_code_signing(self):
        """Untrusted upstream bytes are rejected before any native operation."""
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "probe"
            with patch.object(runtime_probe.urllib.request, "urlopen",
                              return_value=io.BytesIO(b"corrupt")):
                with patch.object(runtime_probe, "run") as native:
                    with self.assertRaisesRegex(ValueError, "archive checksum"):
                        runtime_probe.prepare(output, "test identity", "test profile")
            native.assert_not_called()

    def test_failed_download_does_not_hide_other_loading_results(self):
        """Keep all three observations, and fail even if a cached reload works."""
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            success = subprocess.CompletedProcess([], 0, "loaded=1.32.0\n", "")
            failure = subprocess.CompletedProcess([], 5, "quarantine=0086\n",
                                                  "library load disallowed by system policy")
            with patch.object(runtime_probe.subprocess, "run",
                              side_effect=[success, failure, success]) as process:
                with contextlib.redirect_stdout(io.StringIO()):
                    passed = runtime_probe.exercise(output)
            self.assertFalse(passed)
            self.assertEqual(process.call_count, 3)
            evidence = json.loads((output / "results.json").read_text())
            self.assertEqual(evidence["downloaded"]["exitCode"], 5)
            self.assertIn("system policy", evidence["downloaded"]["stderr"])
            self.assertEqual(evidence["cached"]["exitCode"], 0)

    def test_zero_exit_without_runtime_initialization_does_not_pass(self):
        """A crashed or replaced probe cannot pass by returning zero alone."""
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            result = subprocess.CompletedProcess([], 0, "", "")
            with patch.object(runtime_probe.subprocess, "run", return_value=result):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertFalse(runtime_probe.exercise(output))


if __name__ == "__main__":
    unittest.main()
