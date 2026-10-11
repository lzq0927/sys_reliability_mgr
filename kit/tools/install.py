#!/usr/bin/env python3
"""Install reviewed role files only; preserve workspace memory and local edits."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROLES = ('sr-chief', 'sr-research', 'sr-build', 'sr-coach')
MANIFEST = 'install-manifest.json'


def hashes(root):
    result = {}
    for p in sorted(root.rglob('*')):
        if p.is_symlink():
            raise ValueError(f'Symlink is not supported: {p}')
        if p.is_file() and p.relative_to(root).as_posix() != MANIFEST:
            result[p.relative_to(root).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    return result


def install(target, roles, host):
    kit = Path(__file__).resolve().parents[1]
    version = (kit / 'VERSION').read_text().strip()
    target = Path(target).absolute()
    folder = '.agents' if host == 'codex' else '.opencode'
    destination = target / folder / 'skills'
    # Reject symlink components before resolving: do not redirect writes elsewhere.
    for p in (destination, *destination.parents):
        if p.is_symlink():
            raise ValueError(f'Symlink target is not supported: {p}')
    prepared = []
    for role in roles:
        source = kit / 'skills' / role
        source_hashes = hashes(source)
        if 'SKILL.md' not in source_hashes:
            raise ValueError(f'Incomplete role: {role}')
        dest = destination / role
        if dest.is_symlink():
            raise ValueError(f'Symlink role is not supported: {dest}')
        if dest.exists():
            manifest = dest / MANIFEST
            if not manifest.is_file() or manifest.is_symlink():
                raise ValueError(f'Unmanaged installation: {dest}. Back it up before replacing.')
            previous = json.loads(manifest.read_text())
            if previous.get('role') != role or hashes(dest) != previous.get('files'):
                raise ValueError(f'Local edits detected: {dest}. Preserve and reconcile them first.')
        prepared.append((role, source, dest, source_hashes))
    # Preflight all roles before any mutation. Memory paths are never written.
    for role, source, dest, source_hashes in prepared:
        dest.mkdir(parents=True, exist_ok=True)
        # Remove only obsolete files of the verified, managed previous installation.
        old_files = hashes(dest)
        for name in old_files.keys() - source_hashes.keys():
            (dest / name).unlink()
        shutil.copytree(source, dest, dirs_exist_ok=True)
        if hashes(dest) != source_hashes:
            raise ValueError(f'Copy verification failed: {dest}')
        (dest / MANIFEST).write_text(json.dumps({
            'schemaVersion': 1, 'role': role, 'kitVersion': version,
            'files': source_hashes,
        }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(f'Installed {role} {version}: {dest}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', required=True, type=Path)
    parser.add_argument('--role', action='append', choices=ROLES, required=True)
    parser.add_argument('--host', choices=('codex', 'opencode'), default='codex')
    args = parser.parse_args()
    try:
        install(args.target, list(dict.fromkeys(args.role)), args.host)
    except (ValueError, OSError) as exc:
        parser.exit(1, f'Installation stopped: {exc}\n')


if __name__ == '__main__':
    main()
