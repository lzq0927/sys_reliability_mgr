# Codex 安装与使用（包版本 0.1.0）

## 文件与源
纯 Markdown 角色可手工复制；可选安装器只需要 Python 3.9+ 标准库，不调用网络或模型。
kit/contracts 与 kit/templates 是共用文件唯一编辑源；skills/*/references/common 与 assets/templates 是组装副本，不直接修改。
发布前从共用源刷新上述副本，检查全部相对链接。角色的整个目录必须一起复制，不能只复制 SKILL.md。

## 安装
在已解压的 kit 目录运行以下命令，将 TARGET 替换为实际工作区路径；同一项目可安装多个角色。

```sh
python tools/install.py --target TARGET --role sr-chief --role sr-research
python tools/install.py --target CODE_PROJECT --role sr-build
python tools/install.py --target COACH_PROJECT --role sr-coach
```

安装器只写目标的 .agents/skills/<role>；不会创建宿主项目、聊天、AGENTS.md、模型配置或工作记忆，也不改变权限。首次手工安装的目录需先自行备份，安装器不会覆盖无 manifest 的目录。
每个安装目录附 install-manifest.json，记录 kitVersion 与文件摘要。升级前会校验本地文件，有变更或额外文件就停止，先保存内部修订。单写者执行，不支持并发更新或中断原子回滚；升级前备份安装目录。
回退使用已保留的旧包与匹配环境版本；不回退或覆盖业务记忆。

## 初始化工作区
根据模板创建 context、index、项目与承诺台账，未知状态标未知。AGENTS.md 指向角色、短记忆及按需读取规则。
教练放独立目录，private 不进入主助手索引；仅用户选定的行动摘要进入 outbox。操作系统账户与工具权限才是实际隔离，同账户目录不构成安全边界。

## 启动验证
新聊天明确要求读取 .agents/skills/<role>/SKILL.md，再报告路径、0.1.0、工作目录及资料范围。若自动发现不可用，显式读取文件仍可使用流程；不要声称已验证宿主发现。
执行 evals/public-cases.md 对应角色用例两次，保存实际输出和人工判定。安装器成功不证明行为验收通过。
主助手与研究角色从主工作区启动；实现角色在实际代码项目读取任务书及原有指令；教练只读本次选择的材料。
