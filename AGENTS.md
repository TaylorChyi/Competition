# 交付约定

用户要求下载仓库即可取得可上传的最新产物，不让接收者编译或打包。

- 唯一参赛包是仓库根目录 `CoreGeek.tar.gz`，必须纳入 Git 并随交付推送到私有 GitHub 仓库。
- 不生成 ZIP 或带版本号的产物目录，不保留旧参赛包、旧 Demo 压缩包等并列下载入口。
- 包内必须保持 `CoreGeek/main3.py`、`CoreGeek/src/agent/`，兼容平台固定路径 `/home/docker/CoreGeek/main3.py`。
- 修改算法、启动入口、策略配置、包内样例或交付说明后，运行 `python3 tools/package_bot.py` 更新同名包。
- 提交前运行 `python3 -m unittest discover -s tests -p test_package.py -v`。该检查直接使用根目录交付包，核对源码一致性、独立解压、两种启动入口和真实 HTTP 指令。
- 源码、交付说明和最新包放在同一个提交中；提交并推送后，给用户 GitHub 上的最新包链接。
- 接收方入口只写下载、上传和运行；开发者构建与测试说明放在 README 的维护部分。
- 无需编译不等于没有运行时：当前使用平台已有 Python >=3.11，不声称包内包含 Python 解释器或已完成正式平台验收。
