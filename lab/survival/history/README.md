# 历史生存实验入口

旧 `tools/run_survival.py` 与根目录 `lab/survival.json` 是前一阶段研究工具，保持原文件，当前任务不要用它启动自我对抗。新的前置生存验收使用 `tools/run_survival_gate.py` 和本目录上一级 `plan.json`。

- `plan-v1.json`：用户确认最近目标规则以前的压力计划。保留advance/operators失败，不把这些假设继续当成已确认机制。
- `gate-runner-v2.py`：当前根父本8场记录所用的脚本精确副本，原始运行位置为 `tools/run_survival.py`。后来为避免覆盖旧研究工具，单独命名为 `tools/run_survival_gate.py`。运行逻辑未变，文件路径导致源码哈希变化；不改写原结果哈希。
- `iteration01/combined/runner-v1.py`：修正重复场景误放行前的脚本快照。其六场真实运行记录互不重复，实际结果4/6未通过。合成负测只用于校验门槛，不属于战场成绩。

历史脚本仅保存审计字节，不承诺在当前子目录直接执行。新候选必须使用当前入口和计划重新完整验收。
