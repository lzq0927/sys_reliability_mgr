#!/usr/bin/env python3
"""Check kit references, install/upgrade behavior and build an explicit allowlist archive."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT / 'kit'
ROLES = ('sr-chief', 'sr-research', 'sr-build', 'sr-coach')
CONTRACTS = ('record', 'handoff', 'memory-update')
TEMPLATES = ('project', 'decision', 'handoff', 'result', 'meeting', 'workspace-context')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(args, success=True):
    p = subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True)
    if (p.returncode == 0) != success:
        raise AssertionError(p.stdout + p.stderr)
    return p


def main():
    version = (KIT / 'VERSION').read_text().strip()
    expected = {'VERSION', 'tools/install.py', 'adapters/codex.md', 'adapters/opencode.md',
                'evals/public-cases.md'}
    expected.update(f'contracts/{n}.md' for n in CONTRACTS)
    expected.update(f'templates/{n}.md' for n in TEMPLATES)
    expected.update(f'evals/checkpoint-demo/{n}' for n in ('README.md', 'input.json', 'run.py', 'test_model.py'))
    for role in ROLES:
        prefix = f'skills/{role}'
        expected.update(f'{prefix}/{n}' for n in ('SKILL.md', 'references/workflows.md', 'assets/output.md'))
        expected.update(f'{prefix}/references/common/{n}.md' for n in CONTRACTS)
        expected.update(f'{prefix}/assets/templates/{n}.md' for n in TEMPLATES)
        body = (KIT / prefix / 'SKILL.md').read_text()
        assert body.startswith(f'---\nname: {role}\ndescription: '), role
        assert f'kitVersion: {version}' in body, role
        for name in CONTRACTS:
            assert (KIT / f'{prefix}/references/common/{name}.md').read_bytes() == (KIT / f'contracts/{name}.md').read_bytes()
        for name in TEMPLATES:
            assert (KIT / f'{prefix}/assets/templates/{name}.md').read_bytes() == (KIT / f'templates/{name}.md').read_bytes()
    actual = {p.relative_to(KIT).as_posix() for p in KIT.rglob('*')
              if p.is_file() and '__pycache__' not in p.parts}
    assert actual == expected, {'missing': sorted(expected - actual), 'unexpected': sorted(actual - expected)}
    for name in expected:
        p = KIT / name
        assert not p.is_symlink(), name
        if p.suffix == '.md':
            body = p.read_text()
            assert '/workspace/' not in body and 'D:/code/' not in body, name
            for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)', body):
                if '://' in link or link.startswith('#'):
                    continue
                target = (p.parent / link.split('#')[0]).resolve()
                assert target.is_relative_to(KIT.resolve()) and target.exists(), (name, link)
    before = {n: sha(KIT / n) for n in expected}
    with tempfile.TemporaryDirectory(prefix='sr-kit-eval-') as temp:
        tmp = Path(temp)
        clean = tmp / 'clean'
        cmd = [KIT / 'tools/install.py', '--target', clean]
        for role in ROLES:
            cmd += ['--role', role]
        run(cmd)
        for role in ROLES:
            manifest = json.loads((clean / '.agents/skills' / role / 'install-manifest.json').read_text())
            assert manifest['kitVersion'] == version
            for name, digest in manifest['files'].items():
                assert sha(clean / '.agents/skills' / role / name) == digest
        memory = clean / 'workspace/context.md'
        memory.parent.mkdir()
        memory.write_text('E08_INTERNAL_ONLY_83b2a6a9\n')
        original_memory = memory.read_bytes()
        candidate = tmp / 'next-kit'
        shutil.copytree(KIT, candidate, ignore=shutil.ignore_patterns('__pycache__'))
        next_version = version + '-upgrade-test'
        (candidate / 'VERSION').write_text(next_version + '\n')
        for role in ROLES:
            p = candidate / 'skills' / role / 'SKILL.md'
            p.write_text(p.read_text().replace(f'kitVersion: {version}', f'kitVersion: {next_version}'))
        upgraded = [candidate / 'tools/install.py', '--target', clean, '--role', 'sr-chief']
        run(upgraded)
        assert memory.read_bytes() == original_memory
        m = json.loads((clean / '.agents/skills/sr-chief/install-manifest.json').read_text())
        assert m['kitVersion'] == next_version
        edited = clean / '.agents/skills/sr-chief/SKILL.md'
        edited.write_text(edited.read_text() + '\nLocal internal adaptation.\n')
        edited_bytes = edited.read_bytes()
        failure = run(upgraded, success=False)
        assert 'Local edits detected' in failure.stderr
        assert edited.read_bytes() == edited_bytes
        assert memory.read_bytes() == original_memory
        run([KIT / 'tools/install.py', '--target', tmp / 'oc', '--role', 'sr-coach', '--host', 'opencode'])
        assert (tmp / 'oc/.opencode/skills/sr-coach/SKILL.md').exists()
        unmanaged = tmp / 'unmanaged/.agents/skills/sr-chief'
        unmanaged.mkdir(parents=True)
        (unmanaged / 'SKILL.md').write_text('preserve me')
        run([KIT / 'tools/install.py', '--target', tmp / 'unmanaged', '--role', 'sr-chief'], success=False)
        assert (unmanaged / 'SKILL.md').read_text() == 'preserve me'
        # An invalid JSON input must fail without producing a fabricated result.
        bad = tmp / 'bad.json'
        bad.write_text('{invalid input')
        run([KIT / 'evals/checkpoint-demo/run.py', '--input', bad, '--output', tmp / 'bad-result.json'], success=False)
        assert bad.read_text() == '{invalid input' and not (tmp / 'bad-result.json').exists()
    assert before == {n: sha(KIT / n) for n in expected}, 'Installation mutated the source kit'
    release = ROOT / 'releases'
    release.mkdir(exist_ok=True)
    manifest = {'kitVersion': version, 'algorithm': 'sha256', 'files': {'kit/' + n: before[n] for n in sorted(expected)}}
    archive = release / f'sr-assistant-kit-{version}.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for name in sorted(expected):
            z.write(KIT / name, 'kit/' + name)
        z.writestr('SHA256SUMS.json', json.dumps(manifest, indent=2) + '\n')
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert set(z.namelist()) == set(manifest['files']) | {'SHA256SUMS.json'}
        for name, digest in manifest['files'].items():
            assert hashlib.sha256(z.read(name)).hexdigest() == digest
        assert all(b'E08_INTERNAL_ONLY_83b2a6a9' not in z.read(n) for n in z.namelist())
        with tempfile.TemporaryDirectory(prefix='sr-release-install-') as temp:
            unpacked = Path(temp) / 'unpacked'
            z.extractall(unpacked)
            args = [unpacked / 'kit/tools/install.py', '--target', Path(temp) / 'workspace']
            for role in ROLES:
                args += ['--role', role]
            run(args)
    (release / 'SHA256SUMS.json').write_text(json.dumps(manifest, indent=2) + '\n')
    report = {
        'kitVersion': version, 'files': len(expected), 'archive': archive.name, 'archiveSha256': sha(archive),
        'passed': ['relative links and metadata', 'common-source consistency', 'fresh install of four roles',
                   'upgrade preserves memory', 'local edits rejected and preserved', 'unmanaged install preserved',
                   'OpenCode file layout only', 'source kit unchanged', 'invalid JSON fails without output',
                   'release allowlist and hashes', 'all roles installed from extracted archive'],
        'notVerified': ['new-chat discovery and behavior', 'real ReMAP integration',
                        'target OpenCode runtime', 'internal models and permissions'],
    }
    (release / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
