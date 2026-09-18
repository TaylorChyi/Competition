"""Conservative operator exposure: buildings are not assumed to absorb shots."""
from .protocol import Pos, distance
from .fire_control import POWER


def exposure(turn, pos, *, approaching=True):
    """Potential incoming damage, not a claim about undocumented target choice."""
    return sum(POWER.get(r.kind,5)*(1 if distance(pos,r.pos)<=3 else .35)
               for r in turn.incoming_robots()
               if distance(pos,r.pos)<= (4 if approaching else 3))



def nearest_risk(turn, pos, *, future=False):
    """Fixed-cover nearest risk, optionally requiring cover to survive this turn."""
    robots=turn.incoming_robots()
    buildings=[u for u in turn.ours if u.health>0 and
               u.kind in ('station','wall','railgun','rocket','gatling')]
    total=0
    for robot in robots:
        d=distance(robot.pos,pos)
        if d>(4 if future else 3):
            continue
        protected=False
        for unit in buildings:
            cells=turn.footprint(unit)
            gap=min(distance(robot.pos,p) for p in cells)
            if gap>=d or gap>3:
                continue
            damage=sum(POWER.get(r.kind,5) for r in robots
                       if min(distance(r.pos,p) for p in cells)<=3)
            if not future or unit.health>damage:
                protected=True
                break
        if not protected:
            total+=POWER.get(robot.kind,5)
    return total


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
    # Spend one move only for a fully protected adjacent operating cell.
    # Moving allies are not shields; equal-distance targets remain unsafe.
    if nearest_risk(turn,role.pos)>0:
        safe=[p for p in options if p!=role.pos and nearest_risk(turn,p,future=True)==0]
        if safe:
            return min(safe,key=lambda p:(behind(p),p.x,p.y))
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
