import os
from itertools import combinations, permutations
from typing import Any

from .targeting import load_policy, rocket_targets
from .grid import next_step, shortest_path
from .protocol import (
    PIONEER,
    DAY_ROUNDS,
    ROUNDS_PER_DAY,
    Pos,
    Turn,
    Unit,
    WALL,
    WALL_MATERIAL,
    WEAPON_BUILD_COST,
    attack_command,
    build_command,
    collect_command,
    distance,
    move_command,
    station_footprint,
)

TOWER_LOADOUT = ("gatling", "railgun", "rocket")
STONE_BATCH = 6
RETURN_BUFFER = 2
_NEIGHBOUR_STEPS = (
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1), (0, 1),
    (1, -1), (1, 0), (1, 1),
)


def decide(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    turn = Turn.load(payload)
    commands: dict[int, dict[str, Any]] = {}
    if turn.is_day:
        _day(turn, commands)
    else:
        _night(turn, commands)
    return {str(key): value for key, value in commands.items()}


def _day(turn: Turn, commands: dict[int, dict[str, Any]]) -> None:
    sites = _tower_sites(turn)
    order = _wall_order(turn)
    standing_towers = {unit.pos for unit in turn.weapons()}
    standing_walls = {unit.pos for unit in turn.walls()}
    occupied = turn.occupied_cells()
    towers_missing = [pos for pos in sites if pos not in standing_towers]
    walls_missing = [pos for pos in order if pos not in standing_walls]
    free_towers = [pos for pos in towers_missing if pos not in occupied]
    free_walls = [pos for pos in walls_missing if pos not in occupied]

    claimed: set[Pos] = set()
    returning: set[int] = set()
    daylight_left = DAY_ROUNDS - (turn.round_no - 1) % ROUNDS_PER_DAY
    for role, tower in _tower_pairs(turn):
        if role.kind == PIONEER and role.pos in walls_missing:
            # Leave planned wall cells available to the builders.
            step = _step_toward(turn, role, tower.pos, claimed, inside_only=True)
            if step is not None:
                commands[role.unit_id] = move_command(step)
            continue
        route = _return_route(turn, role, tower, claimed)
        if route is None:
            continue
        # Stop working in time to walk home, with two turns for congestion.
        if role.kind == PIONEER or daylight_left <= len(route) + RETURN_BUFFER:
            returning.add(role.unit_id)
            if route:
                commands[role.unit_id] = move_command(route[0])
                claimed.add(route[0])
    for role in turn.workers():
        if role.unit_id in returning:
            continue
        _worker_day(
            turn, role, sites, free_towers, free_walls, claimed, commands,
        )


def _worker_day(
    turn: Turn,
    role: Unit,
    sites: tuple[Pos, ...],
    towers_missing: list[Pos],
    walls_missing: list[Pos],
    claimed: set[Pos],
    commands: dict[int, dict[str, Any]],
) -> None:
    # Workers spend the same team wallet; reserve only builds issued this turn.
    planned = sum(
        cmd.get("action") == "build" and cmd.get("name") in TOWER_LOADOUT
        for cmd in commands.values()
    )
    if (towers_missing and len(turn.weapons()) + planned < 3
            and turn.gold - planned * WEAPON_BUILD_COST >= WEAPON_BUILD_COST):
        for index, site in enumerate(sites):
            if site in towers_missing and site not in claimed:
                _build_or_walk(
                    turn, role, site, TOWER_LOADOUT[index], claimed, commands,
                )
                return
    if not walls_missing:
        return

    stones = role.backpack.count(WALL_MATERIAL)
    mine = _adjacent_mine(turn, role)
    if mine is not None and stones < STONE_BATCH:
        commands[role.unit_id] = collect_command(mine)
        claimed.add(mine)
        return
    if stones:
        for site in walls_missing:
            if site not in claimed:
                _build_or_walk(turn, role, site, WALL, claimed, commands)
                return
        return
    _mine(turn, role, claimed, commands)


def _adjacent_mine(turn: Turn, role: Unit) -> Pos | None:
    mines = sorted(
        (
            mine for mine in turn.stone_mines()
            if role.pos != mine and distance(role.pos, mine) <= 1
        ),
        key=lambda pos: (distance(role.pos, pos), pos.x, pos.y),
    )
    return mines[0] if mines else None


def _night(turn: Turn, commands: dict[int, dict[str, Any]]) -> None:
    claimed: set[Pos] = set()
    reserved: dict[int, int] = {}
    policy_path = os.environ.get("COMPETITION_ROCKET_POLICY")
    policy = load_policy(policy_path) if policy_path else None
    for role, tower in _tower_pairs(turn):
        if distance(role.pos, tower.pos) <= 1:
            if tower.cooldown > 0:
                continue
            if tower.kind == "rocket" and policy is not None:
                station = turn.station()
                targets = rocket_targets(
                    tower.pos, tower.range_of_attack(), max(1, tower.level),
                    turn.robots, station.pos if station else tower.pos,
                    policy, reserved, turn.width, turn.height,
                )
            else:
                target = _attack_target(turn, tower)
                count = max(1, tower.level) if tower.kind in ("rocket", "gatling") else 1
                targets = [target] * count if target is not None else []
            if targets:
                command = attack_command(role.unit_id, targets[0])
                command["targetPos"] = [pos.dump() for pos in targets]
                commands[tower.unit_id] = command
            continue
        route = _return_route(turn, role, tower, claimed)
        if route:
            commands[role.unit_id] = move_command(route[0])
            claimed.add(route[0])


def _tower_pairs(turn: Turn) -> tuple[tuple[Unit, Unit], ...]:
    roles, towers = turn.controllable(), turn.weapons()
    count = min(len(roles), len(towers))
    if not count:
        return ()
    ready = {tower.unit_id: not turn.is_day and tower.cooldown == 0
             and _attack_target(turn, tower) is not None for tower in towers}

    def cost(pairs):
        adjacent = [distance(role.pos, tower.pos) <= 1 for role, tower in pairs]
        return (
            -sum(near and ready[tower.unit_id] for near, (_, tower) in zip(adjacent, pairs)),
            -sum(adjacent),
            sum(max(0, distance(role.pos, tower.pos) - 1) for role, tower in pairs),
            -sum(tower.range_of_attack() for _, tower in pairs),
            tuple((role.unit_id, tower.unit_id) for role, tower in pairs),
        )

    # There are at most three operators and three towers: at most six pairings.
    # Re-evaluate observed survivors instead of shifting every assignment by ID.
    candidates = (tuple(zip(selected, ordered))
                  for selected in combinations(roles, count)
                  for ordered in permutations(towers, count))
    return min(candidates, key=cost)


def _return_route(turn: Turn, role: Unit, tower: Unit,
                  claimed: set[Pos]) -> tuple[Pos, ...] | None:
    if distance(role.pos, tower.pos) <= 1:
        return ()
    routes = [path for stand in _stand_cells(turn, role, tower.pos, claimed)
              if (path := shortest_path(turn, role, stand, claimed)) is not None]
    # _stand_cells orders ties toward the base; shortest travel takes priority.
    return min(routes, key=len) if routes else None


def _attack_target(turn: Turn, tower: Unit) -> Pos | None:
    reach = tower.range_of_attack()
    targets = [
        robot for robot in turn.robots
        if robot.health > 0 and distance(tower.pos, robot.pos) <= reach
    ]
    if not targets:
        return None
    nearest = min(
        targets,
        key=lambda robot: (distance(tower.pos, robot.pos), robot.robot_id),
    )
    return nearest.pos


def _build_or_walk(
    turn: Turn,
    role: Unit,
    target: Pos,
    name: str,
    claimed: set[Pos],
    commands: dict[int, dict[str, Any]],
) -> None:
    if role.pos != target and distance(role.pos, target) <= 1:
        commands[role.unit_id] = build_command(target, name)
        claimed.add(target)
        return
    step = _step_toward(turn, role, target, claimed)
    if step is not None:
        commands[role.unit_id] = move_command(step)


def _mine(
    turn: Turn,
    role: Unit,
    claimed: set[Pos],
    commands: dict[int, dict[str, Any]],
) -> bool:
    if role.backpack_full:
        return False
    mines = sorted(
        (pos for pos in turn.stone_mines() if pos not in claimed),
        key=lambda pos: (distance(role.pos, pos), pos.x, pos.y),
    )
    for mine in mines:
        if role.pos != mine and distance(role.pos, mine) <= 1:
            commands[role.unit_id] = collect_command(mine)
            claimed.add(mine)
            return True
        step = _step_toward(turn, role, mine, claimed)
        if step is not None:
            commands[role.unit_id] = move_command(step)
            return True
    return False


def _step_toward(
    turn: Turn,
    role: Unit,
    target: Pos,
    claimed: set[Pos],
    *,
    inside_only: bool = False,
) -> Pos | None:
    for stand in _stand_cells(turn, role, target, claimed, inside_only):
        if stand == role.pos:
            return None
        step = next_step(turn, role, stand)
        if step is None or step in claimed:
            continue
        claimed.add(step)
        return step
    return None


def _stand_cells(
    turn: Turn,
    role: Unit,
    target: Pos,
    claimed: set[Pos],
    inside_only: bool = False,
) -> list[Pos]:
    station = turn.station()
    footprint = station_footprint(station.pos) if station else ()
    blocked = turn.blocked(role)
    cells = [
        pos for pos in _neighbours(target)
        if turn.land(pos)
        and pos not in blocked
        and (pos == role.pos or pos not in claimed)
        and (
            not inside_only
            or _footprint_distance(pos, footprint) <= 1
        )
    ]
    cells.sort(key=lambda pos: (_footprint_distance(pos, footprint), pos.x, pos.y))
    return cells


def _tower_sites(turn: Turn) -> tuple[Pos, ...]:
    station = turn.station()
    if station is None:
        return ()
    footprint = station_footprint(station.pos)
    cells = [
        pos for pos in _cells_at_distance(station.pos, 1) if turn.land(pos)
    ]
    cells.sort(key=lambda pos: (_footprint_distance(pos, footprint), pos.x, pos.y))
    return tuple(cells[:3])


def _wall_order(turn: Turn) -> tuple[Pos, ...]:
    station = turn.station()
    if station is None:
        return ()
    footprint = station_footprint(station.pos)
    xs = [pos.x for pos in footprint]
    ys = [pos.y for pos in footprint]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    order = [
        *(Pos(x, ymin - 2) for x in range(xmax + 2, xmin - 3, -1)),
        *(Pos(xmin - 2, y) for y in range(ymin - 1, ymax + 2)),
        *(Pos(x, ymax + 2) for x in range(xmin - 2, xmax + 3)),
        *(Pos(xmax + 2, y) for y in range(ymax + 1, ymin - 2, -1)),
    ]
    entrance = Pos(xmax + 2, ymin - 1)
    return tuple(
        pos for pos in order if pos != entrance and turn.land(pos)
    )


def _cells_at_distance(station_pos: Pos, radius: int) -> tuple[Pos, ...]:
    footprint = station_footprint(station_pos)
    xs = [pos.x for pos in footprint]
    ys = [pos.y for pos in footprint]
    cells = []
    for x in range(min(xs) - radius, max(xs) + radius + 1):
        for y in range(min(ys) - radius, max(ys) + radius + 1):
            pos = Pos(x, y)
            if pos in footprint:
                continue
            if _footprint_distance(pos, footprint) == radius:
                cells.append(pos)
    return tuple(cells)


def _footprint_distance(pos: Pos, footprint: tuple[Pos, ...]) -> int:
    if not footprint:
        return 0
    return min(distance(pos, cell) for cell in footprint)


def _neighbours(pos: Pos) -> tuple[Pos, ...]:
    return tuple(
        Pos(pos.x + dx, pos.y + dy) for dx, dy in _NEIGHBOUR_STEPS
    )
