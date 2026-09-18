"""Keep an operator behind healthier buildings while retaining tower access."""
from .protocol import Pos, distance
from .fire_control import POWER


def safer_step(turn, role, tower, claimed):
    incoming = turn.incoming_robots()
    buildings = [u for u in turn.ours if u.health>0 and u.kind in
                 ('station','wall','gatling','railgun','rocket')]
    def risk(pos):
        total = 0.0
        for robot in incoming:
            d = distance(pos,robot.pos)
            if d>4:
                continue
            # A building strictly closer can absorb attacks. Equal distances
            # are unsafe because the judge's target tie-break is not known.
            shelter = any(min(distance(robot.pos,p) for p in turn.footprint(b))<d
                          and b.health>POWER.get(robot.kind,5)*3 for b in buildings)
            total += POWER.get(robot.kind,5)*(1 if d<=3 else .3)*(.1 if shelter else 1)
        return total
    current = risk(role.pos)
    if current<3:
        return None
    blocked = turn.blocked(role) | claimed
    options = [Pos(role.pos.x+dx,role.pos.y+dy) for dx in (-1,0,1) for dy in (-1,0,1)
               if dx or dy]
    options = [p for p in options if turn.land(p) and p not in blocked
               and distance(p,tower.pos)<=1]
    if not options:
        return None
    best = min(options,key=lambda p:(risk(p),p.x,p.y))
    return best if risk(best)<current*.65 and current-risk(best)>=3 else None
