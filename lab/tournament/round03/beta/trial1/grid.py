from heapq import heappop, heappush
from itertools import count

from .protocol import Pos, Turn, Unit, distance

_STEPS = (
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1), (0, 1),
    (1, -1), (1, 0), (1, 1),
)


def next_step(turn: Turn, moving: Unit, goal: Pos) -> Pos | None:
    path = shortest_path(turn, moving, goal)
    return path[0] if path else None


def shortest_path(turn: Turn, moving: Unit, goal: Pos,
                  avoid: set[Pos] | None = None, *, reroute: bool = True) -> tuple[Pos, ...] | None:
    blocked = turn.blocked(moving) | (avoid or set())
    order = count()
    frontier: list[tuple[int, int, int, int, Pos]] = [
        (distance(moving.pos, goal), 0, 0, next(order), moving.pos)
    ]
    came_from: dict[Pos, Pos] = {}
    best = {moving.pos: 0}
    seen: set[Pos] = set()

    while frontier:
        _, _, cost, _, current = heappop(frontier)
        if current in seen:
            continue
        if current == goal:
            path = _path(came_from, moving.pos, goal)
            if path and reroute and moving.unit_id in turn.failed_actions:
                alternative = shortest_path(turn,moving,goal,(avoid or set())|{path[0]},reroute=False)
                if alternative is not None:
                    return alternative
            return path
        seen.add(current)
        for dx, dy in _STEPS:
            step = Pos(current.x + dx, current.y + dy)
            if step in blocked or not turn.land(step):
                continue
            new_cost = cost + 1
            if new_cost >= best.get(step, new_cost + 1):
                continue
            best[step] = new_cost
            came_from[step] = current
            heappush(
                frontier,
                (
                    new_cost + distance(step, goal),
                    (step.x-goal.x)**2+(step.y-goal.y)**2,
                    new_cost,
                    next(order),
                    step,
                ),
            )
    return None


def _path(came_from: dict[Pos, Pos], start: Pos, goal: Pos) -> tuple[Pos, ...]:
    current = goal
    steps = []
    while current != start:
        steps.append(current)
        current = came_from[current]
    return tuple(reversed(steps))
