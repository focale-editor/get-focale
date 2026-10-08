#!/usr/bin/env bash
# Downloads the latest Focale Linux ZIP and runs its bundled install.sh.
#
#   curl -fsSL https://get.focale-editor.app/install.sh | bash
#
# Everything lives in a function called on the last line, so a truncated
# download never runs a partial script.
set -Eeuo pipefail

main() {
  local catalog_url='https://get.focale-editor.app/downloads.json'
  local release_prefix='https://github.com/focale-editor/get-focale/releases/download/'

  fail() { printf 'focale: %s\n' "$1" >&2; exit 1; }

  [[ "$(uname -s)" == 'Linux' ]] || fail 'this installer only supports Linux. Visit https://focale-editor.app/#downloads.'
  [[ "$(uname -m)" == 'x86_64' ]] || fail 'Focale is only published for x86_64 Linux for now.'
  [[ "${EUID:-$(id -u)}" -ne 0 ]] || fail 'run this installer as your own user, not as root: Focale installs in your home folder.'
  local tool
  for tool in curl unzip; do
    command -v "${tool}" >/dev/null || fail "install ${tool} first."
  done

  # The catalog lists the newest release first; take its first linux-x64 URL.
  local catalog url
  catalog="$(curl -fsSL "${catalog_url}" | tr -d '\n\r\t ')" || fail 'could not read the download catalog.'
  url="$(printf '%s' "${catalog}" | grep -o '"linux-x64":{[^}]*}' | head -n 1 | grep -o '"url":"[^"]*"' | cut -d '"' -f 4 || true)"
  [[ -n "${url}" ]] || fail 'no Linux release is available yet.'
  [[ "${url}" == "${release_prefix}"* ]] || fail "unexpected download address: ${url}"

  # Global, so the EXIT trap can still read it after main returns.
  work_dir="$(mktemp -d)"
  trap 'rm -rf -- "${work_dir}"' EXIT

  printf 'Downloading %s\n' "${url##*/}"
  curl -fL --progress-bar -o "${work_dir}/focale.zip" "${url}" || fail 'the download failed.'
  unzip -q "${work_dir}/focale.zip" -d "${work_dir}/focale" || fail 'the archive could not be extracted.'

  # Accept archives with or without a top-level folder.
  local installer
  installer="$(find "${work_dir}/focale" -maxdepth 2 -type f -name install.sh | head -n 1)"
  [[ -n "${installer}" ]] || fail 'the archive does not contain install.sh.'
  bash "${installer}"
}

main "$@"
