import importlib.util
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('bootstrap', ROOT / 'tools/bootstrap_workspace.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(ROOT / 'kit', self.root / 'kit', ignore=shutil.ignore_patterns('__pycache__'))

    def test_fresh_workspace_and_rerun_preserve_memory(self):
        MODULE.bootstrap(self.root)
        memory = self.root / 'workspace/context.md'
        config = self.root / 'workspace.local.json'
        private = self.root / '.local/coach/private/context.md'
        memory.write_text('my confirmed decisions\n')
        private.write_text('private notes\n')
        config.write_text('{"custom": true}\n')
        MODULE.bootstrap(self.root)
        self.assertEqual(memory.read_text(), 'my confirmed decisions\n')
        self.assertEqual(private.read_text(), 'private notes\n')
        self.assertEqual(config.read_text(), '{"custom": true}\n')
        self.assertTrue((self.root / '.local/build-demo/.agents/skills/sr-build/SKILL.md').is_file())

    def test_modified_skill_is_not_overwritten(self):
        MODULE.bootstrap(self.root)
        skill = self.root / '.agents/skills/sr-chief/SKILL.md'
        skill.write_text('local adaptation\n')
        with self.assertRaises(subprocess.CalledProcessError):
            MODULE.bootstrap(self.root)
        self.assertEqual(skill.read_text(), 'local adaptation\n')

    def test_seed_refuses_symlink(self):
        original = self.root / 'original.txt'
        original.write_text('keep')
        linked = self.root / 'linked.txt'
        linked.symlink_to(original)
        with self.assertRaises(ValueError):
            MODULE.create_once(linked, 'overwrite')
        self.assertEqual(original.read_text(), 'keep')


if __name__ == '__main__':
    unittest.main()
