# Focale releases

The public distribution repository for **Focale**, an image editor for macOS,
Windows and Linux.

**[Visit the Focale website](https://focale-editor.app/#downloads)** to find
downloads and learn more about the application.

## Downloads

Published versions, release notes and downloadable files are collected in
[GitHub Releases](https://github.com/focale-editor/releases/releases).
Choose the package that matches your operating system and processor:

| Platform | Processor             | Installation package            |
|----------|-----------------------|---------------------------------|
| macOS    | Apple Silicon (ARM64) | DMG                             |
| macOS    | Intel (x64)           | DMG                             |
| Windows  | x64                   | Setup executable                |
| Linux    | x64                   | ZIP with an `install.sh` script |

Application ZIP archives are also attached to each release. Consult its notes
for installation details, system requirements and preview status.

## Updates

Focale's desktop distribution checks signed update metadata and offers a link
to download the new installation package. Save your work and close Focale before
installing an update.

The metadata is served from `get.focale-editor.app` through GitHub Pages:

- `downloads.json` supplies the download catalog used by the main website.
- Each platform and processor has its own signed `app-archive.json` update index.
- Versioned `release.json` descriptors identify the application archives and
  record their size and SHA-256 checksum.

This repository contains distribution files and metadata.
