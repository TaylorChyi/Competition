# Competition · 未来战争

面向《未来战争》编程比赛的私有开发仓库。先用小步实验得到可用结果，再按真实对局改进。

## 当前进度

已下载原仓库，保留完整历史、任务书、接口文档与 Demo 压缩包，并将 Demo 展开为可编辑的 `bot/`。

第一轮已完成：

- `bash run.sh <port>` 启动 HTTP 服务，监听 `0.0.0.0`。
- 修复工人共享金币重复分配、炮台总数上限和可见敌方单位避障问题。
- 可选保存每回合请求、响应、决策耗时与异常，支持离线重新生成动作。
- 10 项本地检查通过，包含真实 HTTP 请求与异常恢复。

目前仍是基础防守程序。没有完整判题器、真实任务样本或对局回放，尚未验证存活天数与胜率；尚未实现任务解题、新闻决策、宝藏和升级策略。这里的“80 分”是先做够用版本的工作方式，不是实测比赛分数。

## 快速使用

需要 Python 3.11 或以上，无第三方运行依赖。进入本仓库后：

```bash
bash run.sh 8080
```

另一个终端发送原始请求样例：

```bash
curl -sS -H 'Content-Type: application/json' \
  --data-binary @docs/request.txt http://127.0.0.1:8080/
```

运行检查与单回合决策：

```bash
python3 -m unittest discover -s tests -v
python3 tools/replay.py docs/request.txt
```

需要记录对局时，使用一条新的记录文件路径启动：

```bash
COMPETITION_TRACE="$PWD/runs/match-001.jsonl" bash run.sh 8080
```

停止服务后可重新计算这批已知状态的动作：

```bash
python3 tools/replay.py runs/match-001.jsonl
```

`replay.py` 只回放输入，不推进游戏，也不产生胜率或积分。`runs/` 被 Git 忽略；真实数据先在本机分析，再决定哪些脱敏样本值得纳入测试。

## 后续路线

见 [执行方案](docs/执行方案.md)。下一步最有价值的信息是判题器/试跑入口、编译运行环境说明，以及一份真实自进化任务与请求响应记录。

## 仓库

- 私有远端：[TaylorChyi/Competition](https://github.com/TaylorChyi/Competition)（`origin`）。
- `upstream` 保留原作者仓库，方便后续读取规则更新。

## 来源和边界

- 上游：[Tymonxiong/Competition](https://github.com/Tymonxiong/Competition)
- 本次下载版本：`7e629424c87f3f194d071696d3ee59a8dc2c0a75`。
- `docs/任务书.md`、`docs/接口文档.md`、两个 `.txt` 示例和 `Demo/CoreGeek.tar.gz` 保持原样。
- `bot/` 基于该 Demo 展开；本仓库后续改动由 Git 单独记录。上游未提供许可证，本仓库不额外声明其材料的授权范围。
- 官方文本的推断与本地验证分开记录，具体疑点见执行方案。
