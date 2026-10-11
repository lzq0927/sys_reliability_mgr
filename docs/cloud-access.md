# 云端使用入口

## 浏览器开发与测试

[打开或恢复本项目的 Codespace](https://codespaces.new/lzq0927/sys_reliability_mgr?quickstart=1)

登录 GitHub 后，该入口会恢复你已有的环境；没有环境时进入创建页。它是开发环境入口，不是已经运行的聊天网站。首次创建由 GitHub 显示账户可用配置、额度和计费信息。

仓库的 .devcontainer/devcontainer.json 定义 Python 3.12 环境。首次创建自动执行 tools/bootstrap_workspace.py：安装四角色文件并初始化空白工作记忆；重复执行不会覆盖已有记忆、配置或本地修改的 Skill。

打开后可在终端执行：

```sh
python -m unittest discover -s tests -v
python -m unittest discover -s kit/evals/checkpoint-demo -p test_model.py -v
python tools/verify_release.py
```

也可从 VS Code 的 Terminal → Run Task 选择 Assistant 测试/打包任务。文件、终端和 Git 均在 Codespace 内运行；不依赖本电脑保持开机。

四角色文件安装不等于模型已登录。要与助手对话，仍需在所选客户端配置可用模型或使用已登录的 Codex。当前 Codespaces 配置没有代为创建模型账号、配置密钥或启动聊天服务。

教练工作区位于当前检出的 .local/coach，实现演示位于 .local/build-demo。二者不是现有 ReMAP。个人记忆和路径配置保留在当前环境，不随代码推送；删除环境前应另行备份必要数据。

## 云端自动测试与下载

[测试与下载入口](https://github.com/lzq0927/sys_reliability_mgr/actions/workflows/validate.yml)

每次推送 main 或提交 PR 后，GitHub Actions 运行初始化保护测试、模型测试、独立安装/升级与迁移包校验。也可在页面选择 Run workflow 手工启动。

打开具体运行记录查看结果；成功后在 Artifacts 区下载 sr-assistant-kit-提交号，包含 ZIP、文件摘要和验证报告。构建产物保留 30 天，过期后可重跑；下载可能要求登录 GitHub。

## 网页应用入口的边界

当前系统的运行入口是具有模型能力的客户端加 Skill 文件，尚无 Web 聊天后端。因此没有可直接与四角色对话的常驻 HTTPS 地址。

若建设浏览器应用，应增加聊天界面、服务端模型调用、身份认证、持久存储及角色资料权限，再部署到支持这些能力的平台。开发预览与正式服务分别保留地址，并通过 CI 验证版本；不要把当前执行容器的 localhost 当作用户可访问地址。

业界参考：

- [GitHub 官方快捷 Codespaces 入口](https://docs.github.com/en/codespaces/setting-up-your-project-for-codespaces/setting-up-your-repository/facilitating-quick-creation-and-resumption-of-codespaces)：仓库级创建与恢复链接。
- [GitHub 官方端口转发](https://docs.github.com/en/codespaces/developing-in-a-codespace/forwarding-ports-in-your-codespace)：应用启动后通过转发端口提供浏览器测试地址；私有与公开访问范围独立配置。
- [Vercel 部署环境](https://vercel.com/docs/deployments)：应用的预览和正式部署使用各自的访问地址。

当前验证范围：初始化与 9 个行为测试、打包校验已在当前云端执行。Codespaces 实例尚未创建；实际首次容器启动及模型登录需在账户中完成。Actions 状态以运行页面为准，不将本地通过视为 GitHub 已通过。
