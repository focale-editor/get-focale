# Notarized runtime probe

`runtime-probe.yml` is an isolated macOS arm64 experiment. It uses the existing
`private-source` environment on `main` and the existing Apple credential setup
from the pinned Focale 0.0.19 source. It neither publishes a release nor invokes
the private publication callback.

The script verifies the official Microsoft ONNX Runtime 1.32.0 archive and
library SHA-256 digests, signs the library and test application with the same
Developer ID, then requires Apple's notarization to succeed. The application
keeps the App Sandbox, hardened runtime and library validation enabled. It does
not remove quarantine attributes. The HTTP exception is limited to this test
application's transport configuration; the loopback server lets the sandbox
create the destination file itself.

The job compares bundled loading, downloading into Application Support, and
loading that cached download in a second process. `results.json` preserves each
exit code, quarantine attribute and loader error. A failing downloaded case is
a useful result: do not switch production to optional native code until both
CI and a real Mac can load it. The cached test does not disable network access
and therefore does not prove first use without Apple's ticket service.

The seven-day `macos-runtime-probe` artifact contains the notarized payload and
diagnostics, including Microsoft license notices. To repeat on another Apple
Silicon Mac, extract `runtime-probe.zip` so that an output directory contains
`payload/`, then run the script from the same commit:

```sh
python3 tool/ci/runtime_probe.py --replay --output /absolute/path/to/output
```

This replay needs no Apple signing credentials. It verifies actual loading but
does not stand in for launching a downloaded Focale release via Finder.

Before merging changes, run:

```sh
python3 -m unittest tool.ci.build_identity_test tool.ci.runtime_probe_test
actionlint .github/workflows/runtime-probe.yml
clang -Wall -Wextra -Werror -fobjc-arc -framework Foundation \
  tool/ci/runtime_probe.m -o /tmp/runtime-probe-compile-check
git diff --check
```
