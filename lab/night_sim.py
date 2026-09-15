"""Assumption-labelled, rocket-only 60-turn PvE sandbox, not the official engine.

The two views in the demo are independent counterfactual runs of one scenario.
They do not attack each other. The engine owns truth; policy receives only the
positions/HP available in the competition interface, never future movement.
"""
from collections import Counter, defaultdict
from dataclasses import dataclass
import random

from agent.protocol import Pos, Robot, distance
from agent.targeting import rocket_targets, splash_damage

WIDTH, HEIGHT = 41, 32
ROBOT_STATS = {
    'smallRobot': (40, 5, 1), 'middleRobot': (60, 10, 2),
    'largeRobot': (500, 20, 4), 'bossRobot': (800, 40, 10),
}
PROFILES = {
    'deferred_nearest': {
        'label': '回合末扣血 · 攻击最近单位',
        'lethalRobotsAct': True, 'targetPriority': 'nearest', 'rocketPeriod': 4,
    },
    'deferred_base': {
        'label': '回合末扣血 · 优先基地',
        'lethalRobotsAct': True, 'targetPriority': 'base', 'rocketPeriod': 4,
    },
}


@dataclass
class Entity:
    uid: int
    kind: str
    pos: Pos
    hp: int
    max_hp: int
    level: int = 1
    ready: int = 0
    controller: int = 0

    def cells(self):
        if self.kind == 'station':
            return (self.pos, Pos(self.pos.x + 1, self.pos.y),
                    Pos(self.pos.x, self.pos.y - 1), Pos(self.pos.x + 1, self.pos.y - 1))
        return (self.pos,)

    def dump(self):
        return {'id': self.uid, 'kind': self.kind, 'x': self.pos.x, 'y': self.pos.y,
                'hp': self.hp, 'maxHp': self.max_hp, 'level': self.level}


def separation(point, entity):
    return min(distance(point, p) for p in entity.cells())


def make_scenario(seed: int, mirror: bool = False):
    rng = random.Random(seed)
    entities = [Entity(10013, 'station', Pos(7, 16), 1500, 1500)]
    for i, y in enumerate((12, 16, 20)):
        entities += [Entity(10040 + i, 'rocket', Pos(10, y), 1500, 1500,
                            level=2, controller=10010 + i),
                     Entity(10010 + i, 'pioneer' if i == 1 else 'worker',
                            Pos(9, y), 200 if i == 1 else 220,
                            200 if i == 1 else 220),
                     Entity(40000 + i, 'wall', Pos(13, y), 1000, 1000)]
    # Entire wave exists on turn one; the seed is a synthetic scenario, not day N.
    spawn_cells = [Pos(x, y) for x in range(21, 35) for y in range(7, 25)]
    rng.shuffle(spawn_cells)
    kinds = ['smallRobot'] * 20 + ['middleRobot'] * 12 + ['largeRobot'] * 3 + ['bossRobot']
    rng.shuffle(kinds)
    for i, kind in enumerate(kinds):
        hp, _, _ = ROBOT_STATS[kind]
        entities.append(Entity(30000 + i, kind, spawn_cells[i], hp, hp))
    if mirror:
        for entity in entities:
            # Horizontal reflection of the complete footprint, not just anchor.
            entity.pos = Pos(WIDTH - (2 if entity.kind == 'station' else 1) - entity.pos.x,
                             entity.pos.y)
    return entities


def resolve_moves(proposals, entities):
    """Conservative simultaneous movement: start-occupied cells stay blocked.

    Vacated-cell chains are intentionally unsupported in this prototype and
    explicitly listed for confirmation. Same-target contests stop everyone.
    """
    occupied = {p for entity in entities if entity.hp > 0 for p in entity.cells()}
    counts = Counter(proposals.values())
    return {uid: pos for uid, pos in proposals.items()
            if pos not in occupied and counts[pos] == 1}


class Night:
    def __init__(self, seed, profile='deferred_nearest', mirror=False):
        self.entities = make_scenario(seed, mirror)
        self.profile = dict(PROFILES[profile])
        self.seed, self.profile_name, self.mirror = seed, profile, mirror
        self.round = 0
        self.kills = 0
        self.kill_points = 0
        self.shots = 0
        self.effective_damage = 0
        self.base_destroyed_at = None
        self.frames = []

    def snapshot(self, shots=()):
        base = next(e for e in self.entities if e.kind == 'station')
        return {'round': self.round, 'baseHp': max(0, base.hp), 'kills': self.kills,
                'killPoints': self.kill_points,
                'entities': [e.dump() for e in self.entities if e.hp > 0],
                'shots': list(shots)}

    def step(self, policy):
        self.round += 1
        living = [e for e in self.entities if e.hp > 0]
        robots = [e for e in living if e.kind in ROBOT_STATS]
        defenders = [e for e in living if e.kind not in ROBOT_STATS]
        by_id = {e.uid: e for e in living}
        base = next(e for e in self.entities if e.kind == 'station')
        damage = defaultdict(int)
        reserved = {}
        shots = []
        observations = tuple(Robot(e.uid, e.pos, e.hp) for e in robots)
        for tower in sorted((e for e in defenders if e.kind == 'rocket'), key=lambda e: e.uid):
            operator = by_id.get(tower.controller)
            if (self.round < tower.ready or operator is None
                    or distance(tower.pos, operator.pos) > 1):
                continue
            reach = (10, 15, 10000)[tower.level - 1]
            targets = rocket_targets(tower.pos, reach, tower.level, observations,
                                     base.pos, policy, reserved, WIDTH, HEIGHT)
            if not targets:
                continue
            if len(targets) != tower.level or any(distance(tower.pos, p) > reach for p in targets):
                raise ValueError('Simulator received illegal rocket command')
            tower.ready = self.round + self.profile['rocketPeriod']
            self.shots += len(targets)
            for center in targets:
                shots.append({'from': [tower.pos.x, tower.pos.y], 'to': [center.x, center.y]})
                for robot in robots:
                    damage[robot.uid] += splash_damage(center, robot.pos)
        robot_damage = dict(damage)
        occupied = {p for e in living for p in e.cells()}
        proposals = {}
        for robot in robots:
            if not self.profile['lethalRobotsAct'] and damage[robot.uid] >= robot.hp:
                continue
            eligible = [e for e in defenders if separation(robot.pos, e) <= 3]
            if eligible:
                def target_key(e):
                    first = 0 if self.profile['targetPriority'] == 'base' and e.kind == 'station' else 1
                    return first, separation(robot.pos, e), e.uid
                target = min(eligible, key=target_key)
                damage[target.uid] += ROBOT_STATS[robot.kind][1]
                continue
            options = [Pos(robot.pos.x + dx, robot.pos.y + dy)
                       for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy]
            options = [p for p in options if 0 <= p.x < WIDTH and 0 <= p.y < HEIGHT
                       and p not in occupied and separation(p, base) <= separation(robot.pos, base)]
            if options:
                # Deterministic tie-break; unknown official pathfinding is NOT inferred.
                def move_key(p):
                    forward = -p.x if self.mirror else p.x
                    return separation(p, base), abs(p.y - base.pos.y), forward, p.y
                proposals[robot.uid] = min(options, key=move_key)
        moves = resolve_moves(proposals, living)
        for uid, pos in moves.items():
            by_id[uid].pos = pos
        for e in living:
            old_hp = e.hp
            e.hp = max(0, e.hp - damage[e.uid])
            if e.kind in ROBOT_STATS:
                self.effective_damage += min(old_hp, robot_damage.get(e.uid, 0))
                if e.hp == 0:
                    self.kills += 1
                    self.kill_points += ROBOT_STATS[e.kind][2]
        if base.hp == 0 and self.base_destroyed_at is None:
            self.base_destroyed_at = self.round
        return shots

    def run(self, policy, record=False):
        if record:
            self.frames.append(self.snapshot())
        for _ in range(60):
            shots = self.step(policy)
            if record:
                self.frames.append(self.snapshot(shots))
            if self.base_destroyed_at is not None:
                break
        base = next(e for e in self.entities if e.kind == 'station')
        return {'seed': self.seed, 'profile': self.profile_name, 'mirror': self.mirror,
                'survived': base.hp > 0, 'baseHp': max(0, base.hp),
                'baseDestroyedAt': self.base_destroyed_at, 'kills': self.kills,
                'killPoints': self.kill_points, 'missiles': self.shots,
                'effectiveDamage': self.effective_damage, 'rounds': self.round}
