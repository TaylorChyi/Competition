# Competition · 未来战争

面向《未来战争》编程比赛的私有开发仓库。先用小步实验得到可用结果，再按真实对局改进。

## 当前进度

已下载原仓库，保留完整历史、任务书、接口文档与 Demo 压缩包，并将 Demo 展开为可编辑的 `bot/`。

已有基础程序：

- `bash run.sh <port>` 启动 HTTP 服务，监听 `0.0.0.0`。
- 修复工人共享金币重复分配、炮台总数上限和可见敌方单位避障问题。
- 可选保存每回合请求、响应、决策耗时与异常，支持离线重新生成动作。
- 已扩展为 22 项本地检查，包含真实 HTTP 请求与异常恢复、局部夜战关键结算。

### 新增：可运行的夜战 Demo

下载仓库后双击 [`night-demo/index.html`](night-demo/index.html)，可播放同一波机器人下“最近目标”和“训练选定策略”的对比，支持逐回合、拖动、换边、浅色/深色/跟随系统。GitHub 文件页显示源码；本地打开 HTML 才能播放。

- [实验结果与运行方法](docs/夜战Demo结果.md)：72 场有效局部模拟，另 72 场诊断结果已排除。范围选参相对最近目标平均击杀积分 +18.9%，基地平均少 325 HP；未达到替换默认策略的标准。
- [明天对齐用的机制问题](docs/待确认机制.md)：前 6 项优先，含具体例子、当前假设、待填答复和可直接转发短版。
- [原始结果](night-demo/results.json) · [实验配置](lab/experiment.json) · [可试用策略](night-demo/selected-policy.json)。

这是固定装备的单夜火箭防守模拟；未训练神经网络，也未进行玩家间自博弈。当前范围策略保持可选启用。

完整参赛程序目前仍是基础防守程序。没有完整判题器、真实任务样本或对局回放，尚未验证存活天数与胜率；尚未实现任务解题、新闻决策、宝藏和升级策略。这里的“80 分”是先做够用版本的工作方式，不是实测比赛分数。

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

见 [执行方案](docs/执行方案.md)、[自博弈路线](docs/自博弈方案.md)和[本轮结果](docs/夜战Demo结果.md)。先核对机制清单、获取正式试跑或连续回放，再决定下一轮；任务样本按后续实际需要索取。

## 仓库

- 私有远端：[TaylorChyi/Competition](https://github.com/TaylorChyi/Competition)（`origin`）。
- `upstream` 保留原作者仓库，方便后续读取规则更新。

## 来源和边界

- 上游：[Tymonxiong/Competition](https://github.com/Tymonxiong/Competition)
- 本次下载版本：`7e629424c87f3f194d071696d3ee59a8dc2c0a75`。
- `docs/任务书.md`、`docs/接口文档.md`、两个 `.txt` 示例和 `Demo/CoreGeek.tar.gz` 保持原样。
- `bot/` 基于该 Demo 展开；本仓库后续改动由 Git 单独记录。上游未提供许可证，本仓库不额外声明其材料的授权范围。
- 官方文本的推断与本地验证分开记录，具体疑点见执行方案。
