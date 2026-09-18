"""Conservative operator exposure: buildings are not assumed to absorb shots."""
from .protocol import Pos, distance
from .fire_control import POWER


def exposure(turn, pos, *, approaching=True):
    """Potential incoming damage, not a claim about undocumented target choice."""
    return sum(POWER.get(r.kind,5)*(1 if distance(pos,r.pos)<=3 else .35)
               for r in turn.incoming_robots()
               if distance(pos,r.pos)<= (4 if approaching else 3))



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
    # Movement cannot be assumed to cancel already scheduled damage. Retreat
    # one turn before lethal accumulation, and assess the remaining health.
    remaining=role.health-immediate
    if immediate>0 and remaining>0 and role.health<=2*immediate:
        survivable=[p for p in escape_options if exposure(turn,p,approaching=False)<remaining]
        if survivable:
            return min(survivable,key=lambda p:(distance(p,tower.pos)>1,exposure(turn,p),p.x,p.y))
    # Potential damage is an upper bound, not confirmed targeting. Even when
    # it exceeds health, retain the inherited best-effort escape fallback.
    if immediate>=role.health:
        survivable=[p for p in escape_options if exposure(turn,p,approaching=False)<role.health]
        if survivable:
            return min(survivable,key=lambda p:(distance(p,tower.pos)>1,exposure(turn,p),p.x,p.y))
    if improved<=current*.6 and current-improved>=5:
        return best
    return None


def joint_positions(turn, pairs, claimed):
    """Coordinate emergency one-step operator positions, including vacating chains.

    No planning while everyone is healthy. Distinct destinations and no swaps
    enforce the documented simultaneous movement collision rules.
    """
    from itertools import product, permutations
    roles=tuple(role for role,_ in pairs)
    if not roles or len(roles)>3:
        return None
    towers=turn.weapons()
    if any(not any(distance(role.pos,t.pos)<=1 for t in towers) for role in roles):
        return None
    def high(role,pos):
        return role.health<=max(2*exposure(turn,pos,approaching=False),3*exposure(turn,pos))
    if not any(high(role,role.pos) for role in roles):
        return None
    if any(exposure(turn,r.pos,approaching=False)>=r.health for r in roles):
        return None
    old={role.pos for role in roles}
    blocked=(set(turn.blocked(roles[0]))|{roles[0].pos}|set(claimed))-old
    options=[]
    for role in roles:
        cells=[Pos(role.pos.x+dx,role.pos.y+dy) for dx in (-1,0,1) for dy in (-1,0,1)]
        options.append([p for p in cells if turn.land(p) and p not in blocked
                        and any(distance(p,t.pos)<=1 for t in towers)])
    remaining={r.unit_id:max(1,r.health-exposure(turn,r.pos,approaching=False)) for r in roles}
    risk={p:(exposure(turn,p,approaching=False),exposure(turn,p)) for cells in options for p in cells}
    ready={t.unit_id:t.cooldown==0 and any(distance(t.pos,r.pos)<=t.range_of_attack()
                                          for r in turn.incoming_robots()) for t in towers}
    best=None
    for positions in product(*options):
        if len(set(positions))!=len(positions):
            continue
        if any(positions[i]==roles[j].pos and positions[j]==roles[i].pos
               for i in range(len(roles)) for j in range(i+1,len(roles))):
            continue
        fatal=sum(risk[p][0]>=remaining[r.unit_id] for r,p in zip(roles,positions))
        exposed=sum(r.health<=max(2*risk[p][0],3*risk[p][1]) for r,p in zip(roles,positions))
        moved=tuple(p!=r.pos for r,p in zip(roles,positions))
        for assignment in permutations(towers,len(roles)):
            if any(distance(p,t.pos)>1 for p,t in zip(positions,assignment)):
                continue
            firing=sum((10*t.level if t.kind!='rocket' else 5*t.level)
                       for move,t in zip(moved,assignment) if not move and ready[t.unit_id])
            cost=(fatal,exposed,-firing,sum(risk[p][1]/max(1,r.health) for r,p in zip(roles,positions)),
                  sum(moved),tuple((p.x,p.y,t.unit_id) for p,t in zip(positions,assignment)))
            if best is None or cost<best[0]:
                best=(cost,positions,assignment)
    if best is None:
        return None
    current_fatal=sum(exposure(turn,r.pos,approaching=False)>=remaining[r.unit_id] for r in roles)
    current_high=sum(high(r,r.pos) for r in roles)
    if best[0][:2]>=(current_fatal,current_high):
        return None
    _,positions,assignment=best
    # Independent moves already have a dedicated guard. Intervene only when
    # a useful plan actually requires another operator to vacate a cell.
    if not any(p!=r.pos and p in old for r,p in zip(roles,positions)):
        return None
    return tuple(zip(roles,assignment)),{r.unit_id:p for r,p in zip(roles,positions) if p!=r.pos}


def retreat_step(turn, role, claimed):
    """Continue an emergency retreat after leaving a gun, without forced re-entry."""
    current=exposure(turn,role.pos)
    immediate=exposure(turn,role.pos,approaching=False)
    if current<=0 or role.health>max(2*immediate,3*current):
        return None
    blocked=turn.blocked(role)|claimed
    options=[Pos(role.pos.x+dx,role.pos.y+dy) for dx in (-1,0,1) for dy in (-1,0,1) if dx or dy]
    options=[p for p in options if turn.land(p) and p not in blocked]
    if not options:
        return None
    best=min(options,key=lambda p:(exposure(turn,p),p.x,p.y))
    return best if exposure(turn,best)<current*.6 else None


def shot_relieves_threat(turn, role, reserved, preview):
    """Only this gun's predicted kills count; current enemy damage still applies."""
    remaining=role.health-exposure(turn,role.pos,approaching=False)
    if remaining<=0:
        return False
    killed={r.robot_id for r in turn.incoming_robots()
            if preview.get(r.robot_id,0)-reserved.get(r.robot_id,0)>=r.health}
    if not killed:
        return False
    near=sum(POWER.get(r.kind,5) for r in turn.incoming_robots()
             if r.robot_id not in killed and distance(role.pos,r.pos)<=3)
    approach=sum(POWER.get(r.kind,5)*(1 if distance(role.pos,r.pos)<=3 else .35)
                 for r in turn.incoming_robots() if r.robot_id not in killed
                 and distance(role.pos,r.pos)<=4)
    return remaining>max(2*near,3*approach)
