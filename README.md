# Competition · 未来战争

面向《未来战争》编程比赛的私有开发仓库。先用小步实验得到可用结果，再按真实对局改进。

## 直接下载并上传比赛平台

**[下载最新参赛包（文件名含版本号）](https://github.com/TaylorChyi/Competition/releases/latest)**

参赛包统一放在 [GitHub Releases](https://github.com/TaylorChyi/Competition/releases/latest)。下载 Assets 中的 `CoreGeek-v日期-提交号.tar.gz` 后直接上传，无需编译、安装依赖或重新打包。只保留最新的比赛包 Release，以上入口始终指向最新 Release。文件名示例：`CoreGeek-v2026.09.18-ffc174b.tar.gz`。

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
- 同回合联合分配最多三座电磁炮，只有伤害不降且预计多击杀时才调整原顺序；操作员高死亡风险时避险；日落前调整后排站位，缺员时优先使用能开火的强炮。
- 三炮建好后，一名工人维护12块关键方向围墙，减少后侧施工并保留出路，另一名工人继续采矿。先补缺口，再维护残墙；金币留给基地急救和炮台升级，不常规采购墙升级券。
- 两名工人分开采矿，按请求中的当前价格卖矿；开拓者购买并运送升级券。可升级基地低于75%满血时优先升级回血，轻伤时允许先提升炮台火力；已有基地券送达即用。
- 按实际路线提前回防，购物留出完整往返时间；基地券送达即用。交易入口碰撞后改走其他邻格，并记录基地等级、背包和炮台未开火状态。

### 最新：12墙三电磁，第9轮95%胜率

用户已确认机器人每回合只能移动或攻击，目标为最近或挡路单位。本版删去部分后侧墙，保留关键承伤方向和出入路径：开发8/8、独立验证20/20全部活到第1300回合；第9轮同条件换边赛19胜1负，40/40半场活满十晚，零非法动作。对18墙为10胜0负，对14墙为9胜1负；没有把95%写成100%。

同8场开发中，收入由18墙方案的3140升至3633，首炮升级平均由286.6提前至256.1回合。墙花石料，炮券花金币，减少施工工时可改善火力成长；仍需保留主要防线。12墙加后排火箭的全新生存验证仅19/20，未发布。完整实验及风险见[十晚生存门槛](docs/十晚生存门槛.md)。以上是本地模型结果，正式平台仍需复测。

### 三 Agent 锦标赛与实战修复

用户提供了正式第二晚失败的复盘。此前已修复操作员保护、入夜站位、采购与用券，以及卖矿入口持续碰撞。旧模拟首夜只有21只机器人/队，现按实战摘要加入35/36首两夜的压力场景；完整后续波次、等距目标和角色移动时序仍有假设。

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

检查直接使用已生成的产物；包内代码落后于源码时检查失败。然后提交、推送源码，为该提交发布 Release，将同一份包加上版本号后上传，归档字节保持一致。验证新附件可以下载且内容一致后，再清理旧比赛包 Release。具体步骤见 [发布流程](docs/发布流程.md)和 [AGENTS.md](AGENTS.md)。

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

当前先通过十晚生存门槛，再恢复三Agent对抗。固定开发集和独立验证集见 [生存验收](docs/十晚生存门槛.md)：

```bash
python3 tools/run_survival_gate.py --candidate lab/survival/iteration03/beta/full_ring_exits --stage development --output lab/survival/iteration03/beta/full_ring_exits/gate-development.json
python3 tools/run_survival_gate.py --candidate lab/survival/iteration03/beta/full_ring_exits --stage validation --development-report lab/survival/iteration03/beta/full_ring_exits/gate-development.json --output lab/survival/iteration03/beta/full_ring_exits/gate-validation.json
```

验证阶段要求同一候选先通过全部开发场景；脚本核对源码哈希、场景与阵营的完整序列，失败不得累计成通过。只衡量自身生存，另一方使用固定背景策略。接收参赛包的人无需运行研究工具。旧 `tools/run_survival.py` 保留作历史研究入口，当前不要用它提前启动自对抗。

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
