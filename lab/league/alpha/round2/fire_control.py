"""Allocate observed damage to incoming robots; conserve volleys and clear threats."""
from .protocol import Pos, distance, station_footprint
from .targeting import splash_damage

POWER = {'smallRobot': 5, 'middleRobot': 10, 'largeRobot': 20, 'bossRobot': 40}


def ray_hits(origin, target, robots):
    hits = []
    for robot in robots:
        if not (min(origin.x, target.x)-.5 <= robot.pos.x <= max(origin.x, target.x)+.5
                and min(origin.y, target.y)-.5 <= robot.pos.y <= max(origin.y, target.y)+.5):
            continue
        lower, upper = 0.0, 1.0
        for start, finish, center in ((origin.x, target.x, robot.pos.x),
                                      (origin.y, target.y, robot.pos.y)):
            delta = finish-start
            if delta == 0:
                if abs(start-center) > .5:
                    upper = -1
                    break
            else:
                first, last = sorted(((center-.5-start)/delta, (center+.5-start)/delta))
                lower, upper = max(lower, first), min(upper, last)
        if lower <= upper and upper > 0:
            hits.append((lower, robot.robot_id, robot))
    return [item[2] for item in sorted(hits)]


def targets(turn, tower, reserved):
    incoming = turn.incoming_robots()
    if not incoming:
        return []
    ids = {r.robot_id for r in incoming}
    base = turn.station()
    footprint = station_footprint(base.pos) if base else (tower.pos,)
    urgency = {r.robot_id: POWER.get(r.kind, 5) /
               (1 + max(0, min(distance(r.pos, p) for p in footprint)-3))**2
               for r in incoming}
    reach = tower.range_of_attack()
    if tower.kind == 'rocket':
        cells = {r.pos: r for r in incoming}
        centers = {Pos(r.pos.x+dx, r.pos.y+dy) for r in incoming
                   for dx in (-1,0,1) for dy in (-1,0,1)}
        centers = [p for p in centers if 0 <= p.x < turn.width and 0 <= p.y < turn.height
                   and distance(tower.pos, p) <= reach]
        coverage = {p: [(r, splash_damage(p, r.pos)) for dx in (-1,0,1) for dy in (-1,0,1)
                        if (r := cells.get(Pos(p.x+dx, p.y+dy))) is not None] for p in centers}
    else:
        centers = [r.pos for r in incoming if distance(tower.pos, r.pos) <= reach]
        coverage = {}
        for p in centers:
            line = ray_hits(tower.pos, p, turn.robots)
            if tower.kind == 'gatling':
                coverage[p] = [(r,10) for r in line[:1]]
            else:
                energy, hits = 10*max(1,tower.level), []
                for r in line:
                    hit = min(energy, r.health)
                    hits.append((r,hit))
                    energy -= hit
                    if not energy:
                        break
                coverage[p] = hits
    count = max(1,tower.level) if tower.kind in ('rocket','gatling') else 1
    chosen = []
    for _ in range(count):
        scored = []
        for p, hits in coverage.items():
            if tower.kind == 'gatling' and any((p.x-tower.pos.x)*(q.x-tower.pos.x)+
                    (p.y-tower.pos.y)*(q.y-tower.pos.y) < 0 for q in chosen):
                continue
            value = 0.0
            for r,hit in hits:
                hp = max(0, r.health-reserved.get(r.robot_id,0))
                if hp and r.robot_id in ids:
                    # Kill the small attackers before spending entire nights on
                    # a boss. A nearly finished boss still receives high value.
                    if tower.kind=='rocket':
                        value += (min(hit,hp)+(15 if hit>=hp else 0))*(1+.03*urgency[r.robot_id])
                    else:
                        value += urgency[r.robot_id] * (min(hit,hp)/max(10,hp) + (1 if hit>=hp else 0))
            scored.append((value, -distance(tower.pos,p), -p.x, -p.y, p))
        if not scored or max(scored)[0] <= 0:
            if chosen:
                chosen.extend([chosen[-1]]*(count-len(chosen)))
            break
        p = max(scored)[-1]
        chosen.append(p)
        for r,hit in coverage[p]:
            reserved[r.robot_id] = reserved.get(r.robot_id,0)+hit
    return chosen
