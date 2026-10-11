#!/usr/bin/env python3
"""Initialize generic cloud workspace files without overwriting personal memory."""
import json
from pathlib import Path
import subprocess
import sys


def create_once(path, content):
    for parent in (path, *path.parents):
        if parent.is_symlink():
            raise ValueError(f'Symlink workspace path is not supported: {parent}')
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open('x', encoding='utf-8') as stream:
            stream.write(content)
    except FileExistsError:
        if not path.is_file():
            raise ValueError(f'Expected a file: {path}')


def bootstrap(root):
    root = Path(root).resolve()
    coach = root / '.local/coach'
    demo = root / '.local/build-demo'
    installer = root / 'kit/tools/install.py'
    for target, roles in ((root, ('sr-chief', 'sr-research')),
                          (coach, ('sr-coach',)), (demo, ('sr-build',))):
        args = [sys.executable, str(installer), '--target', str(target)]
        for role in roles:
            args += ['--role', role]
        subprocess.run(args, check=True)
    create_once(root / 'workspace/context.md', '# 当前工作摘要\n\nrevision：1\nscope：private\n\n这是新初始化的工作区。尚未录入个人背景、目标、承诺或项目状态。请由用户提供必要资料，不从模板推定已有事实。\n')
    create_once(root / 'workspace/index.md', '# 工作资料索引\n\n[当前摘要](context.md)\n\n按需建立项目、承诺和决策记录；不索引教练私人材料。\n')
    for name in ('projects', 'decisions', 'handoffs', 'evidence', 'inbox', 'reviews'):
        create_once(root / 'workspace' / name / '.gitkeep', '')
    create_once(root / 'workspace.local.json', json.dumps({
        'schemaVersion': 1, 'environment': 'external', 'role': 'chief',
        'workspaceRoot': str(root / 'workspace'), 'remapRoot': None,
        'coachRoot': str(coach), 'kitVersion': (root / 'kit/VERSION').read_text().strip(),
    }, indent=2) + '\n')
    create_once(coach / 'AGENTS.md', '# 管理教练\n\n读取 .agents/skills/sr-coach/SKILL.md 和 private/context.md。只读取本次授权材料。私人记录保存在 private/，只有用户选定的行动摘要可写 outbox/。目录不隔离同一执行账户。\n')
    create_once(coach / 'private/context.md', '# 私人工作摘要\n\nrevision：1\nscope：private\n\n尚未录入沟通对象或个人记录。由用户提供本次必要材料。\n')
    create_once(coach / 'private/commitments.md', '# 沟通承诺\n\n尚无已确认承诺。\n')
    create_once(coach / 'outbox/.gitkeep', '')
    create_once(demo / 'AGENTS.md', '# 实现角色演示目录\n\n读取 .agents/skills/sr-build/SKILL.md。这里只用于合成任务，不是实际 ReMAP 工程。\n')
    coach.chmod(0o700)
    (coach / 'private').chmod(0o700)
    print('Workspace ready. Read README.md; existing memory was preserved.')
    print(f'Coach workspace: {coach}')
    print(f'Build demo (not ReMAP): {demo}')


if __name__ == '__main__':
    bootstrap(Path(__file__).resolve().parents[1])
