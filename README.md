# Backup Integrity Checker

A personal portfolio utility that answers a practical question: did the files in a copied folder keep the same contents?

It records SHA-256 fingerprints, then reports changed, missing, unexpected, and unchanged files. No third-party packages, network access, or real patient data are needed.

## Run

Requires Python 3.9 or newer. Run these commands from this project's folder:

```sh
python3 backup_check.py snapshot sample baseline.json
python3 backup_check.py verify sample baseline.json
python3 -m unittest discover -s tests -v
```

The first command creates a baseline. The second prints a JSON report with one unchanged file and empty difference lists. Copy `sample` to a temporary folder, edit its CSV, then verify that folder with the same baseline to see a changed file reported.

Exit codes: `0` means success or no differences, `1` means differences found, and `2` means input or filesystem errors. Existing baselines cannot be overwritten. Store the manifest outside the folder being checked.

## Readable report

For an interview demonstration or a quick check, use:

```sh
python3 backup_check.py verify sample baseline.json --format text
```

This prints category counts and quoted filenames. JSON remains the default for scripts. Both formats use the same exit codes.

## IntelliJ IDEA

Open this folder as a project. Use its terminal to run the commands above. A Python editor integration is optional; the program and tests run with the system Python interpreter.

## Design and limits

* Hashes are streamed in 1 MiB chunks to avoid loading large files into memory.
* Relative paths let a baseline verify a copy in another location.
* Symbolic links and nonregular files cause an error instead of silently leaving gaps.
* Empty directories, permissions, ownership, and timestamps are not compared.
* Use a stable directory or filesystem snapshot. Concurrent changes during scanning are not supported.
* Protect your baseline separately. This tool detects content differences; it does not prove that a baseline is authentic or that a backup can restore an application.
* The tool never repairs or deletes source files.

## Portfolio talking points

Implemented a Python command-line utility that compares SHA-256 manifests and produces machine-readable backup verification reports. Added ten automated tests for content changes, malformed manifests, nested Unicode paths, symlinks, and accidental baseline replacement.

Interview demo: create a baseline, verify an unchanged copy, edit a file, and explain why a mismatch signals investigation rather than proving malicious activity. Discuss streaming versus reading entire files and why a trusted baseline matters.

## Next improvements

* Atomic baseline writes for resilience to interrupted writes.
* Stable snapshot integration and detection of files modified during scanning.

This is an independent personal portfolio project, separate from school and team repositories.
