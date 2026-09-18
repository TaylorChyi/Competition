import os
from itertools import combinations, permutations
from typing import Any

from .targeting import load_policy, rocket_targets
from .grid import next_step, shortest_path
from .fire_control import targets as defense_targets
from .economy import develop, use_carried, urgent_refit
from .guard import safer_step, exposure, station_side_rank
from .protocol import (
    PIONEER,
    DAY_ROUNDS,
    ROUNDS_PER_DAY,
    Pos,
    Turn,
    Unit,
    TOWER_TYPES,
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

TOWER_LOADOUT = ("railgun", "railgun", "railgun")
DEFAULT_ROCKET_POLICY = None
DEFAULT_COVER = True
STONE_BATCH = 6
RETURN_BUFFER = 2
_NEIGHBOUR_STEPS = (
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1), (0, 1),
    (1, -1), (1, 0), (1, 1),
)


def decide(payload: dict[str, Any], *, loadout: tuple[str, ...] | None = None,
           rocket_policy: dict | None = None, cover: bool | None = None,
           smart: bool = True, economy: bool = True, fortify: int = 4) -> dict[str, dict[str, Any]]:
    turn = Turn.load(payload)
    commands: dict[int, dict[str, Any]] = {}
    if turn.is_day:
        _day(turn, commands, loadout if loadout is not None else TOWER_LOADOUT,
             DEFAULT_COVER if cover is None else cover, economy, fortify)
    else:
        _night(turn, commands, rocket_policy, smart)
    return {str(key): value for key, value in commands.items()}


def _day(turn: Turn, commands: dict[int, dict[str, Any]], loadout: tuple[str, ...], cover: bool,
         economy: bool, fortify: int) -> None:
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
    if economy:
        for role in turn.controllable():
            use_carried(turn,role,claimed,commands)
    for role, tower in _tower_pairs(turn):
        if role.unit_id in commands:
            continue
        if economy and urgent_refit(turn,role,claimed,commands):
            returning.add(role.unit_id)
            continue
        if role.kind == PIONEER and role.pos in walls_missing and not (economy and turn.shop_prices):
            # Leave planned wall cells available to the builders.
            step = _step_toward(turn, role, tower.pos, claimed, inside_only=True)
            if step is not None:
                commands[role.unit_id] = move_command(step)
            continue
        route = _return_route(turn, role, tower, claimed, inside_only=cover)
        if route is None:
            continue
        # Stop working in time to walk home, with two turns for congestion.
        if daylight_left <= max(len(route) + RETURN_BUFFER,6) or (role.kind == PIONEER and
                not (economy and turn.shop_prices)):
            returning.add(role.unit_id)
            if route:
                commands[role.unit_id] = move_command(route[0])
                claimed.add(route[0])
            elif daylight_left<=6:
                step=safer_step(turn,role,tower,claimed,preparing=True)
                if step is not None:
                    commands[role.unit_id]=move_command(step)
                    claimed.add(step)
    for role in turn.workers():
        if role.unit_id in returning or role.unit_id in commands:
            continue
        _worker_day(
            turn, role, sites, free_towers, free_walls, claimed, commands, loadout, economy, fortify,
        )
    if economy:
        for role in turn.controllable():
            if role.kind==PIONEER and role.unit_id not in commands and role.unit_id not in returning:
                develop(turn,role,claimed,commands)


def _worker_day(
    turn: Turn,
    role: Unit,
    sites: tuple[Pos, ...],
    towers_missing: list[Pos],
    walls_missing: list[Pos],
    claimed: set[Pos],
    commands: dict[int, dict[str, Any]],
    loadout: tuple[str, ...],
    economy: bool,
    fortify: int,
) -> None:
    # Workers spend the same team wallet; reserve only builds issued this turn.
    planned = sum(
        cmd.get("action") == "build" and cmd.get("name") in TOWER_TYPES
        for cmd in commands.values()
    )
    purchases=sum(turn.shop_prices.get(c.get('name'),0)*c.get('num',1)
                  for c in commands.values() if c.get('action')=='buy')
    if (towers_missing and len(turn.weapons()) + planned < 3
            and turn.gold - purchases - planned * WEAPON_BUILD_COST >= WEAPON_BUILD_COST):
        for index, site in enumerate(sites):
            if site in towers_missing and site not in claimed:
                _build_or_walk(
                    turn, role, site, loadout[index], claimed, commands,
                )
                return
    if economy and turn.shop_prices:
        carried = {n for u in turn.controllable() for n in u.backpack}
        damaged = [t for t in turn.weapons() if t.health<250 and t.pos not in claimed
                   and 'WeaponUpgradeVoucher'+str(t.level) not in carried]
        if damaged and turn.gold-purchases-planned*WEAPON_BUILD_COST>=WEAPON_BUILD_COST:
            tower = min(damaged,key=lambda t:(t.health,distance(role.pos,t.pos)))
            _build_or_walk(turn,role,tower.pos,tower.kind,claimed,commands)
            return
        # One builder maintains a small forward screen, then rejoins mining.
        # A stone buys 1000 wall HP; this does not rely on walls blocking shots.
        base=turn.station()
        base_under_fire = base and base.health<.8*1500*base.level
        distant_opening_stone=(turn.round_no<=70 and not role.backpack.count('stone')
            and min((distance(base.pos,p) for p in turn.stone_mines()),default=100)>8) if base else False
        if (fortify and base and not base_under_fire and not distant_opening_stone
                and role.unit_id==turn.workers()[0].unit_id):
            cx,cy=(turn.width-1)/2,(turn.height-1)/2
            front=sorted(_wall_order(turn),key=lambda p:((p.x-cx)**2+(p.y-cy)**2,p.x,p.y))[:fortify]
            walls={w.pos:w for w in turn.walls()}
            needed=[p for p in front if p not in claimed and
                    (p in walls or p not in turn.occupied_cells()) and
                    (p not in walls or walls[p].health<500)]
            if needed:
                mine=_adjacent_mine(turn,role,claimed)
                if mine is not None and role.backpack.count('stone')<min(4,len(needed)):
                    commands[role.unit_id]=collect_command(mine)
                    claimed.add(mine)
                    return
                if 'stone' in role.backpack:
                    _build_or_walk(turn,role,needed[0],'wall',claimed,commands)
                    return
                if _mine(turn,role,claimed,commands):
                    return
    if economy and develop(turn,role,claimed,commands):
        return
    if not walls_missing:
        return

    stones = role.backpack.count(WALL_MATERIAL)
    mine = _adjacent_mine(turn, role, claimed)
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


def _adjacent_mine(turn: Turn, role: Unit, claimed=frozenset()) -> Pos | None:
    mines = sorted(
        (
            mine for mine in turn.stone_mines()
            if role.pos != mine and distance(role.pos, mine) <= 1 and mine not in claimed
        ),
        key=lambda pos: (distance(role.pos, pos), pos.x, pos.y),
    )
    return mines[0] if mines else None


def _night(turn: Turn, commands: dict[int, dict[str, Any]], policy: dict | None = None,
           smart: bool = True) -> None:
    claimed: set[Pos] = set()
    reserved: dict[int, int] = {}
    policy_path = os.environ.get("COMPETITION_ROCKET_POLICY")
    if policy is None:
        policy = load_policy(policy_path) if policy_path else DEFAULT_ROCKET_POLICY
    for role in turn.controllable():
        if not use_carried(turn,role,claimed,commands,night=True):
            urgent_refit(turn,role,claimed,commands)
    for role, tower in sorted(_tower_pairs(turn, excluded=set(commands)), key=lambda pair: pair[1].range_of_attack()):
        if role.unit_id in commands:
            continue
        if distance(role.pos, tower.pos) <= 1:
            step = safer_step(turn,role,tower,claimed)
            if step is not None:
                commands[role.unit_id] = move_command(step)
                claimed.add(step)
                continue
            if tower.cooldown > 0:
                continue
            if tower.kind == "rocket" and policy is not None:
                station = turn.station()
                targets = rocket_targets(
                    tower.pos, tower.range_of_attack(), max(1, tower.level),
                    turn.incoming_robots(), station.pos if station else tower.pos,
                    policy, reserved, turn.width, turn.height,
                )
            elif smart:
                targets = defense_targets(turn, tower, reserved)
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
        if route and not (exposure(turn,route[0],approaching=False)>=role.health
                          and exposure(turn,role.pos,approaching=False)<role.health):
            commands[role.unit_id] = move_command(route[0])
            claimed.add(route[0])


def _tower_pairs(turn: Turn, excluded=frozenset()) -> tuple[tuple[Unit, Unit], ...]:
    roles, towers = tuple(r for r in turn.controllable() if r.unit_id not in excluded), turn.weapons()
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
            -sum((10*tower.level if tower.kind!='rocket' else 5*tower.level)
                 for near,(_,tower) in zip(adjacent,pairs) if near and ready[tower.unit_id]),
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
                  claimed: set[Pos], *, inside_only: bool = False) -> tuple[Pos, ...] | None:
    station = turn.station()
    covered = station is None or _footprint_distance(role.pos, station_footprint(station.pos)) <= 1
    if distance(role.pos, tower.pos) <= 1 and (not inside_only or covered):
        return ()
    routes = [path for stand in _stand_cells(turn, role, tower.pos, claimed, inside_only)
              if (path := shortest_path(turn, role, stand, claimed)) is not None]
    if not routes and inside_only:
        return _return_route(turn, role, tower, claimed)
    # _stand_cells orders ties toward the base; shortest travel takes priority.
    return min(routes, key=len) if routes else None


def _attack_target(turn: Turn, tower: Unit) -> Pos | None:
    reach = tower.range_of_attack()
    targets = [
        robot for robot in turn.incoming_robots()
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
            claimed.add(mine)
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
    cells.sort(key=lambda pos: (station_side_rank(turn,pos,target),pos.x,pos.y))
    return cells


def _tower_sites(turn: Turn) -> tuple[Pos, ...]:
    station = turn.station()
    if station is None:
        return ()
    footprint = station_footprint(station.pos)
    cells = [
        pos for pos in _cells_at_distance(station.pos, 1) if turn.land(pos)
    ]
    cx, cy = (turn.width-1)/2, (turn.height-1)/2
    cells.sort(key=lambda p: ((p.x-cx)**2+(p.y-cy)**2,
                             p.x if station.pos.x<cx else -p.x,
                             p.y if station.pos.y<cy else -p.y))
    spaced = []
    for cell in cells:
        if all(distance(cell,other)>=2 for other in spaced):
            spaced.append(cell)
        if len(spaced)==3:
            return tuple(spaced)
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
