#!/usr/bin/env python3
"""Record a pinned private source identity and resume its private publisher."""

import argparse
import json
import os
from pathlib import Path
import re
import subprocess

SOURCE_REPOSITORY = 'focale-editor/focale'


def validate_inputs(tag, source_sha):
    """Reject source references other than a release tag and full commit SHA."""
    if not re.fullmatch(r'v?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)', tag):
        raise ValueError('Expected a numeric Focale release tag.')
    if not re.fullmatch(r'[0-9a-f]{40}', source_sha):
        raise ValueError('Expected a full source commit SHA.')


def record(source, tag, source_sha, prerelease):
    """Check the private tag checkout before exposing its minimal provenance."""
    validate_inputs(tag, source_sha)
    actual = subprocess.run(['git', '-C', str(source), 'rev-parse', 'HEAD'],
                            check=True, capture_output=True, text=True).stdout.strip()
    if actual != source_sha:
        raise ValueError('The source tag no longer matches the requested commit.')
    subprocess.run(['python3', 'tool/distribution/release_pipeline/release_pipeline.py',
                    'inspect', '--tag', tag], cwd=source, check=True,
                   env={key: value for key, value in os.environ.items() if key != 'GITHUB_OUTPUT'})
    return {'schemaVersion': 1, 'sourceRepository': SOURCE_REPOSITORY,
            'sourceSha': source_sha, 'tag': tag, 'prerelease': prerelease}


def notify(provenance, run_id):
    """Request publication using the successful run's existing artifacts."""
    validate_inputs(provenance['tag'], provenance['sourceSha'])
    if (provenance['schemaVersion'] != 1 or provenance['sourceRepository'] != SOURCE_REPOSITORY or
            type(provenance['prerelease']) is not bool or not re.fullmatch(r'[1-9][0-9]*', run_id)):
        raise ValueError('Invalid build provenance.')
    subprocess.run([
        'gh', 'workflow', 'run', 'publish.yml', '--repo', SOURCE_REPOSITORY, '--ref', 'main',
        '-f', 'target=publish', '-f', f'tag={provenance["tag"]}',
        '-f', f'prerelease={str(provenance["prerelease"]).lower()}',
        '-f', 'build_repository=focale-editor/get-focale', '-f', f'build_run_id={run_id}',
    ], check=True)


def main():
    """Expose source validation and the successful-build callback to Actions."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('validate-inputs', 'record', 'notify'))
    parser.add_argument('--source', type=Path)
    parser.add_argument('--file', type=Path)
    arguments = parser.parse_args()
    if arguments.command == 'notify':
        if not arguments.file:
            parser.error('notify requires --file')
        notify(json.loads(arguments.file.read_text()), os.environ['BUILD_RUN_ID'])
        return
    tag, source_sha = os.environ['SOURCE_TAG'], os.environ['SOURCE_SHA']
    validate_inputs(tag, source_sha)
    if arguments.command == 'record':
        if not arguments.source:
            parser.error('record requires --source')
        prerelease = os.environ['IS_PRERELEASE']
        if prerelease not in ('true', 'false'):
            raise ValueError('Invalid prerelease flag.')
        provenance = record(arguments.source, tag, source_sha, prerelease == 'true')
        Path('build-provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
        with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as output:
            output.write(f'tag={tag}\nsha={source_sha}\n')


if __name__ == '__main__':
    main()
