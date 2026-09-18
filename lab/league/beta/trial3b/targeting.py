"""Small, inspectable rocket policy; no network or learned model dependency."""
import json
from functools import lru_cache
from pathlib import Path

from .protocol import Pos, Robot, distance

BASELINE = {"name": "nearest", "mode": "nearest", "threatWeight": 0,
            "killBonus": 0, "reserveDamage": False}


@lru_cache(maxsize=8)
def load_policy(path: str) -> dict:
    policy = json.loads(Path(path).read_text())
    if policy.get("mode") not in {"nearest", "splash"}:
        raise ValueError("Unsupported rocket policy mode")
    for key in ("threatWeight", "killBonus"):
        if not isinstance(policy.get(key), (int, float)) or not 0 <= policy[key] <= 100:
            raise ValueError("Invalid " + key)
    if not isinstance(policy.get("reserveDamage"), bool):
        raise ValueError("Invalid reserveDamage")
    return policy


def splash_damage(center: Pos, position: Pos) -> int:
    separation = distance(center, position)
    return 20 if separation == 0 else 10 if separation == 1 else 0


def rocket_targets(origin: Pos, reach: int, level: int, robots: tuple[Robot, ...],
                   base: Pos, policy: dict, reserved: dict[int, int],
                   width: int = 41, height: int = 32) -> list[Pos]:
    """Exactly level positions when a useful shot exists; all within map/range.

    reserved only influences planning, never mutates observed HP. A dead robot
    may still act this turn under the simulator's end-of-round assumption.
    """
    living = [r for r in robots if r.health > 0]
    if not living:
        return []
    if policy["mode"] == "nearest":
        eligible = [r for r in living if distance(origin, r.pos) <= reach]
        if not eligible:
            return []
        target = min(eligible, key=lambda r: (distance(origin, r.pos), r.robot_id))
        return [target.pos] * level
    # Empty cells can be better splash centers than occupied cells.
    centers = {
        Pos(r.pos.x + dx, r.pos.y + dy)
        for r in living for dx in (-1, 0, 1) for dy in (-1, 0, 1)
        if 0 <= r.pos.x + dx < width and 0 <= r.pos.y + dy < height
        and distance(origin, Pos(r.pos.x + dx, r.pos.y + dy)) <= reach
    }
    if not centers:
        return []
    centers = sorted(centers, key=lambda p: (p.x, p.y))
    # Compute geometric coverage once; re-score remaining HP per missile.
    coverage = [(p, [(r, splash_damage(p, r.pos)) for r in living
                     if distance(p, r.pos) <= 1]) for p in centers]
    targets = []
    for _ in range(level):
        best = None
        best_score = -1.0
        for p, victims in coverage:
            score = 0.0
            for robot, damage in victims:
                hp = max(0, robot.health - reserved.get(robot.robot_id, 0)) if policy['reserveDamage'] else robot.health
                if not hp:
                    continue
                proximity = max(0, 1 - distance(base, robot.pos) / 20)
                score += min(hp, damage) * (1 + policy['threatWeight'] * proximity)
                if damage >= hp:
                    score += policy['killBonus']
            if score > best_score:
                best_score, best = score, (p, victims)
        if best is None or (best_score <= 0 and not targets):
            return []
        if best_score <= 0:
            # Protocol requires level targets; preserve cardinality even when
            # earlier missiles already account for every visible HP point.
            targets.append(targets[-1])
            continue
        target, victims = best
        targets.append(target)
        if policy['reserveDamage']:
            for robot, damage in victims:
                reserved[robot.robot_id] = reserved.get(robot.robot_id, 0) + damage
    return targets
