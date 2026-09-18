# Competition · 未来战争

面向《未来战争》编程比赛的私有开发仓库。先用小步实验得到可用结果，再按真实对局改进。

## 直接下载并上传比赛平台

**[下载最新 CoreGeek.tar.gz](https://github.com/TaylorChyi/Competition/releases/latest/download/CoreGeek.tar.gz)**

参赛包统一放在 [GitHub Releases](https://github.com/TaylorChyi/Competition/releases/latest)。下载 Assets 中的 `CoreGeek.tar.gz` 后直接上传，无需编译、安装依赖或重新打包。只保留最新的比赛包 Release，以上下载地址始终指向最新版。

包内只有 `CoreGeek/` 一个顶层目录。平台将它解压到 `/home/docker` 后，启动命令为：

```bash
python3 /home/docker/CoreGeek/main3.py 6666
```

端口由比赛平台指定；本次正常日志使用 `6666`。程序使用平台已有的 Python >=3.11，包内不包含解释器。[平台接收与启动说明](docs/交付说明.md)

用户已确认采用此结构的包能在内网平台运行。遇到新的入口问题时，可查阅 [启动排查与本版预检命令](docs/平台启动排查.md)。

## 当前进度

源码与参赛包统一采用官方名称：`CoreGeek/main3.py` 是入口，算法位于 `CoreGeek/src/agent/`。仓库保存源码与文档，最新参赛包在 Releases 下载。

```text
CoreGeek/
├── main3.py
├── run.sh
├── pyproject.toml
└── src/agent/
```

本版已加入连续多晚需要的采集、卖矿、采购、升级和防线维护：

- 默认三座电磁炮，按基地朝向布置并留出操作位；只给攻击我方的机器人评分，避免炮弹被去对方的机器人挡住后白白消耗。
- 同回合分配炮台火力，优先清掉能快速击杀的威胁，减少重复攻击；操作员高死亡风险时避险；日落前调整后排站位，缺员时优先使用能开火的强炮。
- 一名工人维护四格前排围墙，随后参与采矿；开局石矿过远时先赚钱，基地受损时优先升级；建筑损伤跨天保留，残血炮台必要时花金币重建。
- 两名工人分开采矿，按请求中的当前价格卖矿；开拓者购买并运送升级券。受损基地优先升级回血，其余资金逐步升级武器。
- 按实际路线提前回防，购物留出完整往返时间；基地券送达即用。交易入口碰撞后改走其他邻格，并记录基地等级、背包和炮台未开火状态。

### 最新：三 Agent 锦标赛与实战修复

用户提供了正式第二晚失败的复盘。本轮修复操作员保护、入夜站位、采购与用券，以及卖矿入口持续碰撞。旧模拟首夜只有21只机器人/队，现按实战摘要加入35/36首两夜的压力场景；完整波次和机器人的移动/攻击规则仍有假设。

三个GPT-6 Astra Agent独立改进、互相找弱点。每对先比10组换边赛，最高胜率并列者加赛5组；每轮冠军验证后发布Release，败者从冠军继续迭代。结果与发布记录见[锦标赛进度](docs/锦标赛进度.md)，缺陷与证据边界见[第二晚实战修复](docs/第二晚实战修复.md)。100%只按记录的固定候选比赛计算，不表示正式比赛必胜。

### 历史：完整十晚迭代

以下为 `8a52374` 历史版本的模拟结果，未覆盖本次实战的完整条件。用实际 Bot 指令从 75 金币、零炮台开始，连续运行到第 1300 回合，验证采集、交易、升级、死亡与次日复活。旧版、新版使用同一套模型和波次。

实验包含训练种子选择、独立种子换边对旧版，以及新版与新版争夺资源的自对弈。结果、失效情况和官方规则依据集中在 [十晚生存迭代报告](docs/十晚生存迭代.md)，原始记录在 [实验结果](lab/survival-results.json)，配置在 [实验配置](lab/survival.json)。

新版在独立种子上的 24 个阵营结果全部撑过第二晚；就近攻击假设下 12/12 撑过十晚，隔墙直攻基地假设下为 1/12，仍有第三晚失败。详见报告中的完整分组与失败记录。

这些是本地模拟结果；官方判题器、真实完整波次尚未提供，不能写成正式比赛成绩。前一轮三夜实验保留为 [历史记录](docs/自对弈迭代结果.md)。

### 历史：可运行的单夜 Demo

下载仓库后双击 [`night-demo/index.html`](night-demo/index.html)，可播放同一波机器人下“最近目标”和“训练选定策略”的对比，支持逐回合、拖动、换边、浅色/深色/跟随系统。GitHub 文件页显示源码；本地打开 HTML 才能播放。

- [实验结果与运行方法](docs/夜战Demo结果.md)：72 场有效局部模拟，另 72 场诊断结果已排除。范围选参相对最近目标平均击杀积分 +18.9%，基地平均少 325 HP；未达到替换默认策略的标准。
- [下一次对齐用的机制问题](docs/待确认机制.md)：已按本轮实战反馈更新，含具体例子、当前假设、待填答复和可直接转发短版。
- [原始结果](night-demo/results.json) · [实验配置](lab/experiment.json) · [可试用策略](night-demo/selected-policy.json)。

这个历史 Demo 是固定装备的单夜火箭防守模拟，未训练神经网络，也未进行玩家间自对弈。当前三Agent十晚对比见上节；历史范围策略仍可单独试用。

完整参赛程序目前仍是基础防守程序。已有其他程序的 243 回合动作日志和用户对我方程序的实战反馈，但没有连续输入、结算状态或完整判题器；已实现经济与升级；任务解题、新闻决策和宝藏尚未实现。这里的“80 分”是先做够用版本的工作方式，不是实测比赛分数。

## 开发维护

<details>
<summary>仅修改代码时需要：本地运行、更新产物和检查</summary>

源码更新后，维护者生成 `dist/CoreGeek.tar.gz` 并验证：

```bash
python3 tools/package_bot.py
python3 -m unittest discover -s tests -p test_package.py -v
```

检查直接使用已生成的产物；包内代码落后于源码时检查失败。然后提交、推送源码，为该提交发布 Release 并上传同一份包。验证新附件可以下载且内容一致后，再清理旧比赛包 Release。具体步骤见 [发布流程](docs/发布流程.md)和 [AGENTS.md](AGENTS.md)。

本地开发需要 Python 3.11 或以上，无第三方运行依赖。进入本仓库后：

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

运行一轮完整十晚策略实验（24 场训练比较、12 场换边复核、6 场新版自对弈）：

```bash
python3 tools/run_survival.py
```

该命令需要包含历史提交的 Git 克隆，读取上次发布的 Bot 作为对手。候选先在训练种子中比较，再用独立种子复核；结果写入 `lab/survival-results.json`，不会自动改动线上默认策略。接收参赛包的人无需运行它。

需要记录对局时，使用一条新的记录文件路径启动：

```bash
COMPETITION_TRACE="$PWD/runs/match-001.jsonl" bash run.sh 8080
```

停止服务后可重新计算这批已知状态的动作：

```bash
python3 tools/replay.py runs/match-001.jsonl
```

`replay.py` 只回放输入，不推进游戏，也不产生胜率或积分。`runs/` 被 Git 忽略；真实数据先在本机分析，再决定哪些脱敏样本值得纳入测试。

</details>

## 后续路线

见 [执行方案](docs/执行方案.md)、[自博弈路线](docs/自博弈方案.md)和[本轮结果](docs/自对弈迭代结果.md)。下一步用新版的连续实战状态核对机器人行为和真实波次，按失效点继续迭代；任务样本按实际需要索取。

## 仓库

- 私有远端：[TaylorChyi/Competition](https://github.com/TaylorChyi/Competition)（`origin`）。
- `upstream` 保留原作者仓库，方便后续读取规则更新。

## 来源和边界

- 上游：[Tymonxiong/Competition](https://github.com/Tymonxiong/Competition)
- 本次下载版本：`7e629424c87f3f194d071696d3ee59a8dc2c0a75`。
- `docs/任务书.md`、`docs/接口文档.md` 和两个 `.txt` 示例保持原样；旧 Demo 压缩包已从当前下载内容移除，源码来源可在上游及 Git 历史中追溯。
- `CoreGeek/` 基于该 Demo 展开；本仓库后续改动由 Git 单独记录。上游未提供许可证，本仓库不额外声明其材料的授权范围。
- 官方文本的推断与本地验证分开记录，具体疑点见执行方案。
