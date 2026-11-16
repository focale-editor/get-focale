"""Build, notarize and exercise an optional runtime without changing quarantine."""

import argparse
import functools
import hashlib
import http.server
import json
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import tarfile
import threading
import urllib.request

VERSION = "1.32.0"
ARCHIVE_URL = (
    "https://github.com/microsoft/onnxruntime/releases/download/"
    f"v{VERSION}/onnxruntime-osx-arm64-{VERSION}.tgz"
)
ARCHIVE_SHA256 = "8ddca23f532b9d4fbb279ba9b08dab6c0ac94fdc9aec2eb44a1db7049216c043"
LIBRARY_SHA256 = "51c5a25a3dfafd74f62f403e6e0dc7881d97c0e627c703a4d9548c5677abc8fd"


def run(*arguments, **kwargs):
    """Run a bounded command and propagate failures."""
    return subprocess.run(arguments, check=True, timeout=120, **kwargs)


def digest(path):
    """Hash a file without loading the entire archive into memory."""
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def prepare(output, identity, profile):
    """Verify Microsoft bytes and produce the signed, notarized test payload."""
    output.mkdir(parents=True, exist_ok=False)
    archive = output / "upstream.tgz"
    with urllib.request.urlopen(ARCHIVE_URL, timeout=120) as response:
        with archive.open("wb") as destination:
            shutil.copyfileobj(response, destination)
    if digest(archive) != ARCHIVE_SHA256:
        raise ValueError("Microsoft archive checksum mismatch")
    payload = output / "payload"
    payload.mkdir()
    library = payload / "libonnxruntime.dylib"
    with tarfile.open(archive) as upstream:
        prefix = f"onnxruntime-osx-arm64-{VERSION}/"
        for member_name, destination in (
            (f"lib/libonnxruntime.{VERSION}.dylib", library),
            ("LICENSE", payload / "LICENSE"),
            ("ThirdPartyNotices.txt", payload / "ThirdPartyNotices.txt"),
        ):
            member = upstream.getmember(prefix + member_name)
            if not member.isfile():
                raise ValueError(f"Expected a regular archive member: {member_name}")
            with upstream.extractfile(member) as source:
                with destination.open("wb") as target:
                    shutil.copyfileobj(source, target)
    if digest(library) != LIBRARY_SHA256:
        raise ValueError("Microsoft runtime checksum mismatch")
    run("codesign", "--remove-signature", str(library))
    run("codesign", "--sign", identity, "--options", "runtime", "--timestamp", str(library))
    application = payload / "RuntimeDownloadProbe.app"
    contents = application / "Contents"
    (contents / "MacOS").mkdir(parents=True)
    (contents / "Frameworks").mkdir()
    shutil.copyfile(library, contents / "Frameworks/libonnxruntime.dylib")
    info = {
        "CFBundleIdentifier": "app.focaleeditor.runtime-download-probe",
        "CFBundleExecutable": "RuntimeDownloadProbe",
        "CFBundleName": "RuntimeDownloadProbe",
        "CFBundlePackageType": "APPL",
        "CFBundleVersion": "1",
        "NSAppTransportSecurity": {"NSAllowsLocalNetworking": True, "NSAllowsArbitraryLoads": True},
    }
    (contents / "Info.plist").write_bytes(plistlib.dumps(info))
    entitlements = output / "probe.entitlements"
    entitlements.write_bytes(plistlib.dumps({
        "com.apple.security.app-sandbox": True,
        "com.apple.security.network.client": True,
    }))
    run("clang", "-Wall", "-Wextra", "-Werror", "-fobjc-arc", "-framework", "Foundation",
        str(Path(__file__).with_suffix(".m")), "-o", str(contents / "MacOS/RuntimeDownloadProbe"))
    run("codesign", "--sign", identity, "--options", "runtime", "--timestamp",
        "--entitlements", str(entitlements), str(application))
    run("codesign", "--verify", "--deep", "--strict", str(application))
    submission = output / "submission.zip"
    run("ditto", "-c", "-k", "--keepParent", str(payload), str(submission))
    # Credentials stay in the CI keychain; neither logs nor artifacts contain them.
    result = subprocess.run(
        ["xcrun", "notarytool", "submit", str(submission), "--keychain-profile", profile,
         "--wait", "--timeout", "20m", "--output-format", "json"],
        check=False, capture_output=True, text=True, timeout=1260,
    )
    (output / "notarization.json").write_text(result.stdout)
    result.check_returncode()
    notarization = json.loads(result.stdout)
    if notarization.get("status") != "Accepted":
        raise ValueError(f"Notarization failed: {notarization.get('status')}")
    run("codesign", "--verify", "--strict", "--check-notarization", "-R=notarized", str(library))
    run("xcrun", "stapler", "staple", str(application))
    run("xcrun", "stapler", "validate", str(application))
    run("spctl", "--assess", "--type", "execute", "--verbose", str(application))
    (payload / "runtime.json").write_text(json.dumps({
        "version": VERSION, "upstreamUrl": ARCHIVE_URL,
        "upstreamSha256": ARCHIVE_SHA256, "sha256": digest(library),
        "size": library.stat().st_size,
    }, indent=2) + "\n")
    run("ditto", "-c", "-k", "--keepParent", str(payload), str(output / "runtime-probe.zip"))


def exercise(output):
    """Compare bundled, sandbox-downloaded and already-downloaded loading."""
    payload = output / "payload"
    binary = payload / "RuntimeDownloadProbe.app/Contents/MacOS/RuntimeDownloadProbe"
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(
        http.server.SimpleHTTPRequestHandler, directory=str(payload)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    results = {}
    try:
        for name, argument in (
            ("bundled", "bundled"),
            ("downloaded", f"http://127.0.0.1:{server.server_port}/libonnxruntime.dylib"),
            ("cached", "offline"),
        ):
            result = subprocess.run([str(binary), argument], capture_output=True,
                                    text=True, timeout=90)
            results[name] = {"exitCode": result.returncode,
                             "stdout": result.stdout, "stderr": result.stderr}
            print(name, json.dumps(results[name]), flush=True)
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
        (output / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    return all(result["exitCode"] == 0 and f"loaded={VERSION}" in result["stdout"]
               for result in results.values()) and len(results) == 3


def main():
    """Prepare on CI or replay its signed payload on another Mac."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--replay", action="store_true")
    parser.add_argument("--profile", default="focale-notary")
    arguments = parser.parse_args()
    output = arguments.output.resolve()
    if not arguments.replay:
        prepare(output, os.environ["FOCALE_MACOS_IDENTITY"], arguments.profile)
    return 0 if exercise(output) else 1


if __name__ == "__main__":
    raise SystemExit(main())
