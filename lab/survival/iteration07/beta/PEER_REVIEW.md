# iteration07 同行只读审查

仅审当前运行模块，无新种子结果读取；不修改对方模块。

## Gamma：guard.py 提前邻炮移位

未发现把墙当作弹道挡板。nearest_risk 依据用户已确认最近目标规则：只认静态、活着的己方建筑且严格更近，等距保留风险；基地按完整footprint距离。

目的格 future=True 要求保护建筑HP严格大于所有当前3格内incoming火力之和。因此本轮可能死的墙不能作为新增提前移动的安全依据。距4也检查，有当前近建筑则机器人可攻击该建筑而不移动；不作移动与攻击同回合假设。

同回合占位：safer_step 的候选排除 turn.blocked(role)|claimed，brain选中移动后立即claimed.add(step)，use动作角色从配炮排除但其真实身体仍阻挡。不允许新分支走入正在用药角色位置或两个角色同目标。

具体限制已复现：当前格判断 future=False 不要求建筑存活整轮。两个smallRobot位于(5,5)/(5,6)，墙(6,5)仅1HP，角色(7,5)：nearest_risk(current)=0，future=True=10。若顺序结算首怪破墙、第二怪重选最近单位，新提前预移不会触发；父本exposure紧急逻辑仍在。这是漏触发，不是目的格错误认可。已发送Gamma，不要求增加变体。

## Alpha：economy.py 至少一座rail>=2才提前买rocket3券

Owner确认顶层iteration07/alpha为待冻结路径，仅第三炮rocket与该采购条件增量。

新增条件没有绕过既有保护：
- 基地<75%时基地券仍是goals首项，不足钱会break，不转买火炮券。
- use_carried在采购前，已有库存stock从需求扣除。
- buy分支仍检查满包，数量受room约束。
- cash_available扣除同回合已购/建炮；purchase_route检查白天返程可达。

保留的具体策略限制：一座rail达到2级不代表其健康；若该炮残血且另一前炮仍1级，150金买rocket3耗尽钱包仍可能缺25重建金。此条件消除全前炮1级时先买rocket3，不能承诺消除所有现金断流。另满包pioneer的店旁等待是继承逻辑，不是本次新增。未发现此次条件破坏基地急救、已有券使用或包容量合法性。

结论：无新增明确合法性阻断；Gamma漏触发与Alpha资金限制均已发owner。仍需根独立资格，不能以只读审查替代生存实测。

## iteration08 Alpha 最后用券排序复核

相对07仅WeaponUpgradeVoucher1目标改railgun优先，其余券仍rocket优先。采购的一rail>=2条件不变。test_front_voucher覆盖第一/第二前炮、无rail1后rocket、二阶券仍rocket；test_one_front覆盖采购基地优先，test_field_regressions覆盖基地夜间立即用券。三组25测试本次实际全部通过。

额外内存构造验证两项：夜间远rail1但相邻rocket1，会先经邻接过滤后给rocket用券；夜间所有炮均远，不移动送武器券。均通过。夜间过滤发生在新排序之前，基地券不受该过滤且原先Station排序优先保持。

边界：白天候选先按种类/血量排序，才尝试walk；不按路径可达性重选，选中rail1入口暂堵时不会同轮回退相邻rocket。健康rail1也会优先于更危急rocket1，可能推迟后者升级回血；这是明确策略代价，不能称所有炮都不会饥饿。无法行走时不发非法移动，原有用券路径也有同类不回退机制。未见新增基地券/夜间合法性阻断，具体限制已发Alpha。未查看独立资格或未来种子。
