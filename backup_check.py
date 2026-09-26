"""Create and verify portable SHA-256 manifests without changing source files."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import sys


def scan(root):
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError('Source must be an existing directory, not a symbolic link')
    files = {}
    def fail(error):
        raise error
    for folder, dirs, names in os.walk(root, onerror=fail):
        for name in dirs + names:
            if (Path(folder) / name).is_symlink():
                raise ValueError('Symbolic links are not supported: ' + name)
        for name in sorted(names):
            path = Path(folder) / name
            if not path.is_file():
                raise ValueError('Only regular files are supported: ' + str(path))
            digest = hashlib.sha256()
            # Stream large backups instead of loading entire files into memory.
            with path.open('rb') as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b''):
                    digest.update(block)
            files[path.relative_to(root).as_posix()] = digest.hexdigest()
    return dict(sorted(files.items()))


def load_manifest(path):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(data, dict) or data.get('version') != 1 or data.get('algorithm') != 'sha256':
        raise ValueError('Unsupported manifest format')
    files = data.get('files')
    if not isinstance(files, dict):
        raise ValueError('Manifest files must be an object')
    for name, digest in files.items():
        relative = PurePosixPath(name)
        if (not name or relative.is_absolute() or '..' in relative.parts
                or relative.as_posix() != name or name == '.' or '\\' in name):
            raise ValueError('Invalid manifest path: ' + name)
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
            raise ValueError('Invalid SHA-256 digest: ' + name)
    return files


def compare(expected, actual):
    return {
        'missing': sorted(expected.keys() - actual.keys()),
        'unexpected': sorted(actual.keys() - expected.keys()),
        'changed': sorted(name for name in expected.keys() & actual.keys() if expected[name] != actual[name]),
        'unchanged': sum(expected[name] == actual[name] for name in expected.keys() & actual.keys()),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['snapshot', 'verify'])
    parser.add_argument('directory', type=Path)
    parser.add_argument('manifest', type=Path)
    args = parser.parse_args(argv)
    try:
        root, manifest = args.directory.resolve(), args.manifest.resolve()
        if root == manifest or root in manifest.parents:
            raise ValueError('Keep the manifest outside the source directory')
        if args.command == 'snapshot':
            data = {'version': 1, 'algorithm': 'sha256', 'files': scan(args.directory)}
            # Exclusive creation protects an earlier baseline from accidental replacement.
            with args.manifest.open('x', encoding='utf-8') as stream:
                json.dump(data, stream, indent=2, sort_keys=True)
                stream.write('\n')
            print('Recorded {} files'.format(len(data['files'])))
            return 0
        report = compare(load_manifest(args.manifest), scan(args.directory))
        print(json.dumps(report, indent=2))
        return int(any(report[key] for key in ('missing', 'unexpected', 'changed')))
    except (OSError, ValueError) as error:
        print('Error: ' + str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
