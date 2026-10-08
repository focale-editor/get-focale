"""Validate source pinning and private callback arguments without remote writes."""

from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

from tool.ci import build_identity as identity

SHA = 'a' * 40


class BuildIdentityTests(unittest.TestCase):
    """Keep public dispatch inputs restricted to immutable Focale releases."""

    def test_only_numeric_release_tags_and_full_commits_are_allowed(self):
        for tag in ('0.0.2', 'v0.0.2'):
            identity.validate_inputs(tag, SHA)
        for tag, sha in [('main', SHA), ('0.0.2\nmalicious', SHA), ('0.00.2', SHA),
                         ('0.0.2', 'HEAD'), ('0.0.2', SHA + '\n')]:
            with self.subTest(tag=tag, sha=sha), self.assertRaises(ValueError):
                identity.validate_inputs(tag, sha)

    def test_moved_source_tag_is_rejected_before_inspecting_or_building(self):
        with patch.object(identity.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, 'b' * 40)) as run:
            with self.assertRaisesRegex(ValueError, 'no longer matches'):
                identity.record(Path('source'), '0.0.2', SHA, True)
            self.assertEqual(run.call_count, 1)

    def test_verified_source_produces_only_minimal_public_provenance(self):
        with patch.object(identity.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, SHA)):
            result = identity.record(Path('source'), '0.0.2', SHA, False)
        self.assertEqual(result, {'schemaVersion': 1, 'sourceRepository': 'focale-editor/focale',
                                  'sourceSha': SHA, 'tag': '0.0.2', 'prerelease': False})

    def test_callback_preserves_tag_run_and_false_prerelease(self):
        provenance = {'schemaVersion': 1, 'sourceRepository': 'focale-editor/focale',
                      'sourceSha': SHA, 'tag': '0.0.2', 'prerelease': False}
        with patch.object(identity.subprocess, 'run') as run:
            identity.notify(provenance, '12345')
        arguments = run.call_args.args[0]
        for value in ('target=publish', 'tag=0.0.2', 'build_run_id=12345', 'prerelease=false',
                      'build_repository=focale-editor/get-focale'):
            self.assertIn(value, arguments)

    def test_invalid_callback_never_dispatches(self):
        provenance = {'schemaVersion': 1, 'sourceRepository': 'focale-editor/focale',
                      'sourceSha': SHA, 'tag': '0.0.2', 'prerelease': True}
        for key, value in [('sourceRepository', 'fork/focale'), ('schemaVersion', 0),
                           ('prerelease', 'false'), ('tag', 'main')]:
            with self.subTest(key=key), patch.object(identity.subprocess, 'run') as run:
                with self.assertRaises(ValueError):
                    identity.notify({**provenance, key: value}, '12345')
                run.assert_not_called()


if __name__ == '__main__':
    unittest.main()
