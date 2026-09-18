"""Operator exposure under confirmed nearest-target selection."""
from .protocol import Pos, distance
from .fire_control import POWER


def exposure(turn, pos, *, approaching=True):
    """Nearest-target risk; ties remain unsafe and only fixed live cover counts."""
    buildings=[u for u in turn.ours if u.health>0 and
               u.kind in ('station','wall','railgun','rocket','gatling')]
    result=0
    for robot in turn.incoming_robots():
        d=distance(pos,robot.pos)
        if d>(4 if approaching else 3):
            continue
        nearest=min((distance(robot.pos,p) for u in buildings
                     for p in turn.footprint(u)),default=100)
        # Simultaneous damage: even a 1-HP wall exists for this attack.
        # For a distance-four operator, an in-range building stops movement.
        if nearest<=3 and nearest<d:
            continue
        result+=POWER.get(robot.kind,5)*(1 if d<=3 else .35)
    return result



def station_side_rank(turn, pos, anchor):
    """Exposure first, then station proximity and an orientation-aware rear tie."""
    base=turn.station()
    if base is None:
        return (exposure(turn,pos),0,0,0)
    footprint=turn.footprint(base)
    bx=sum(p.x for p in footprint)/len(footprint)
    by=sum(p.y for p in footprint)/len(footprint)
    # Away from map center breaks equal footprint-distance ties symmetrically;
    # the station-from-gun projection provides a local fallback.
    dx,dy=pos.x-anchor.x,pos.y-anchor.y
    rear=dx*(bx-(turn.width-1)/2)+dy*(by-(turn.height-1)/2)
    local=dx*(bx-anchor.x)+dy*(by-anchor.y)
    return (exposure(turn,pos),min(distance(pos,p) for p in footprint),-rear,-local)


def safer_step(turn, role, tower, claimed, *, preparing=False):
    blocked = turn.blocked(role) | claimed
    options = [Pos(role.pos.x+dx,role.pos.y+dy) for dx in (-1,0,1) for dy in (-1,0,1)
               if dx or dy]
    escape_options = [p for p in options if turn.land(p) and p not in blocked]
    options = [p for p in escape_options if distance(p,tower.pos)<=1]
    if not options:
        options = [role.pos]
    def behind(pos):
        return station_side_rank(turn,pos,tower.pos)
    if preparing:
        best=min(options,key=lambda p:(behind(p),p.x,p.y))
        return best if behind(best)<behind(role.pos) else None
    current=exposure(turn,role.pos)
    immediate=exposure(turn,role.pos,approaching=False)
    if current<=0:
        return None
    best=min(options,key=lambda p:(exposure(turn,p),behind(p),p.x,p.y))
    improved=exposure(turn,best)
    # A substantial two-turn mortality risk warrants giving up a shot. Small
    # variations in hypothetical target selection do not: repeated sidesteps
    # can silence all three guns while robots continue attacking the station.
    if role.health > max(2*immediate,3*current):
        return None
    if immediate>=role.health:
        survivable=[p for p in escape_options if exposure(turn,p,approaching=False)<role.health]
        if survivable:
            return min(survivable,key=lambda p:(distance(p,tower.pos)>1,exposure(turn,p),p.x,p.y))
    if improved<=current*.6 and current-improved>=5:
        return best
    return None
