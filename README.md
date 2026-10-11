# 个人负责人助手系统

用四个按需角色支持业务交付、技术竞争力和团队建设。通用包版本 0.1.0。

## 立即使用

当前云端项目安装了主助手、可靠性技术助手。新聊天先打开本项目，再给出以下启动语；宿主没有自动发现 Skill 时直接指定文件。

| 角色 | 启动语 |
|---|---|
| 主助手 | 读取 .agents/skills/sr-chief/SKILL.md、workspace/context.md 和 workspace/index.md，做本周重点检查；区分已确认事实、建议和缺失信息，更新已确认的行动。 |
| 可靠性技术助手 | 读取 .agents/skills/sr-research/SKILL.md，围绕我提供的设计问题，明确指标、边界、证据和假设，交付方法比较与验证方案。 |
| 研发实现助手 | 在实际代码项目读取 sr-build/SKILL.md、项目指令和指定任务书，核查可改范围与输入后实施，交付实际验证证据。 |
| 管理教练 | 在独立教练工作区读取 sr-coach/SKILL.md 和本次提供的资料，帮助我准备沟通与反馈；只分享我选定的行动摘要。 |

四个角色由 Skill 定义，不要求四条永久聊天。新聊天加载是否成功，必须报告实际 Skill 路径、版本、工作目录及资料范围。文件存在只代表安装完成。

## 目录和维护

- [kit](kit/)：通用源；Skill、协议、模板、合成用例和适配说明。
- [实施记录](docs/implementation/2026-10-12-status.md)：实际检查、部署限制和下一步。
- [原始方案](docs/superpowers/plans/2026-10-11-personal-assistant-system-plan.md)：角色设计与验收门槛。
- workspace/：本机工作记忆，未跟踪到 Git；不要作为通用包发布。
- workspace.local.json：本机自定义路径，路径不存在时相应接入待完成。
- session-backups/：历史会话副本，不作为日常启动上下文。
- releases/：本机发布产物；生成过程见 [安装说明](kit/adapters/codex.md)。

编辑 kit 后按适配说明重新组装完整角色目录，不直接修改安装副本。升级先比较安装文件是否被本地修改，再备份和替换；不覆盖工作记忆。发布仅打包 kit，附 SHA-256 文件清单。

修改共用协议/模板后，在项目根目录刷新组装副本，再验证与打包：

```sh
python - <<'PY'
from pathlib import Path
import shutil
kit = Path('kit')
for role in ('sr-chief', 'sr-research', 'sr-build', 'sr-coach'):
    skill = kit / 'skills' / role
    shutil.copytree(kit / 'contracts', skill / 'references/common', dirs_exist_ok=True)
    shutil.copytree(kit / 'templates', skill / 'assets/templates', dirs_exist_ok=True)
PY
python tools/verify_release.py
python kit/tools/install.py --target . --role sr-chief --role sr-research
```

以上 shell 示例用于当前云端。Windows 可把 Python 段保存成临时脚本运行；安装器本身不依赖 shell。

当前没有绑定定时任务或自主跨聊天调度。没有接入真实内网模型。ReMAP 是否已安装、角色行为是否已验收，以实施记录为准。
