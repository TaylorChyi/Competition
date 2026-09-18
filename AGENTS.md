# 交付约定

用户要求每次修改后的参赛包发布到 GitHub Releases，接收者直接下载上传，无需编译或打包。只保留最新比赛包版本。

- 源码和文档纳入 Git；参赛压缩包不提交到源码树。固定本地输出是 `dist/CoreGeek.tar.gz`，该目录被忽略。
- 源码使用 `CoreGeek/main3.py` 和 `CoreGeek/src/agent/`，与官方命名及发布包一致；不再维护另一套 `bot/` 目录。
- 修改算法、启动入口、策略配置、包内样例或交付说明后，运行 `python3 tools/package_bot.py`，再运行 `python3 -m unittest discover -s tests -p test_package.py -v`。
- 包内只有官方 `CoreGeek/` 一个顶层目录，显式记录目录、`CoreGeek/main3.py` 和 `CoreGeek/src/agent/`；不得在归档根部增加并列入口。
- 父目录解压和去掉顶层目录后解压到 CoreGeek，验证固定入口；平台额外套目录时，验证 Release 中的预检启动命令。该命令先打印实际路径，再按当前包的完整清单哈希定位唯一入口；不能随意选中旧版本。
- 启动和包结构变更需在一次性 Linux / Python 3.11 容器中发真实 HTTP 请求，覆盖固定路径 `/home/docker/CoreGeek/main3.py` 和上述预检命令，不能只以 macOS 临时目录检查代替。平台未实际运行成功前，只能报告本地验证结果。
- 提交并推送源码后，为该完整提交 SHA 创建带 `bot-` 前缀的新 Release 标签，上传刚才验证过的 `CoreGeek.tar.gz` 并标记 Latest。当前交付的 agent 应完成实际发布，不只停在打包或写说明。
- Release 说明记录源码 SHA、包的 SHA-256、启动方式和本次检查；使用 `python3 tools/platform_start.py` 从待发布包生成可复制的预检启动命令。不要把本地通过写成正式比赛验收。
- 从 Release 重新下载附件，核对哈希和入口；验证新版本可用后，再删除旧的比赛包 Release 及其资产。不要清理其他用途的 Release 或改写 Git 历史。
- 下载入口固定为 `https://github.com/TaylorChyi/Competition/releases/latest/download/CoreGeek.tar.gz`，最终给用户这个链接或 Latest Release 页面。
- 不再生成 ZIP、多个带版本号的本地输出目录或原始 Demo 包的并列下载入口。
- 具体发布与复核步骤见 `docs/发布流程.md`。接收方首页只说明下载、上传和运行，开发者命令放到维护部分。
- 当前使用平台已有 Python >=3.11，包内没有解释器；无需编译不等于没有运行时。
