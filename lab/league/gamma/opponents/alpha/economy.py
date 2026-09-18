"""Observed-price mining, trade and building upgrades; no assumed free income."""
from collections import Counter
from .grid import shortest_path
from .protocol import Pos, distance, move_command, collect_command, station_footprint

ORE = ('stone','iron','copper')


def route(turn, role, locations, claimed):
    blocked = turn.blocked(role) | claimed
    goals = {Pos(p.x+dx,p.y+dy) for p in locations for dx in (-1,0,1) for dy in (-1,0,1)
             if dx or dy}
    goals = [p for p in goals if turn.land(p) and (p == role.pos or p not in blocked)]
    for goal in sorted(goals, key=lambda p:(distance(role.pos,p),p.x,p.y)):
        path = shortest_path(turn,role,goal,claimed)
        if path is not None:
            return path
    return None


def walk(turn, role, locations, claimed, commands):
    path = route(turn,role,locations,claimed)
    if path:
        commands[role.unit_id] = move_command(path[0])
        claimed.add(path[0])
    return path is not None


def upgrade_targets(turn, name):
    if name.startswith('WeaponUpgradeVoucher'):
        units = turn.weapons()
    elif name.startswith('StationUpgradeVoucher'):
        units = [turn.station()] if turn.station() and turn.station().health>0 else []
    else:
        return []
    return [u for u in units if name[-1] == str(u.level) and u.level<3]


def use_carried(turn, role, claimed, commands, night=False):
    max_hp = 200 if role.kind=='pioneer' else 220
    medicine = next((n for n in role.backpack if n.lower()=='medicine'), None)
    if medicine and role.health < max_hp*.65:
        commands[role.unit_id] = {'action':'use','name':medicine}
        return True
    applied = {Pos.load(cmd['targetPos'][0]) for cmd in commands.values()
               if cmd.get('action')=='use' and cmd.get('targetPos')}
    for name in sorted(role.backpack, key=lambda n:(not n.startswith('Station'),n)):
        units = [u for u in upgrade_targets(turn,name) if u.pos not in applied]
        if night and not name.startswith('StationUpgradeVoucher'):
            units=[u for u in units if distance(role.pos,u.pos)<=1]
        if not units:
            continue
        unit = min(units, key=lambda u:(u.kind!='rocket',u.health/(1500*u.level if u.kind=='station' else 500+500*u.level),
                                       distance(role.pos,u.pos),u.unit_id))
        if unit.kind=='station':
            # Movement and consumption have different deadlines: begin the
            # return while the observed assault can still be outrun.
            footprint = station_footprint(unit.pos)
            power = {'smallRobot':5,'middleRobot':10,'largeRobot':20,'bossRobot':40}
            travel = max(0,distance(role.pos,unit.pos)-1)
            dps = sum(power.get(r.kind,5) for r in turn.incoming_robots()
                      if min(distance(r.pos,p) for p in footprint)<=travel+3)
            deadline = max(600*unit.level,dps*(travel+3))
            if unit.health>deadline:
                daylight=70-(turn.round_no-1)%130
                if travel>0 and (night or daylight<=travel+8):
                    return walk(turn,role,[unit.pos],claimed,commands)
                continue
        if distance(role.pos,unit.pos)<=1:
            commands[role.unit_id] = {'action':'use','name':name,'targetPos':[unit.pos.dump()]}
            return True
        if not night or name.startswith('StationUpgradeVoucher'):
            return walk(turn,role,[unit.pos],claimed,commands)
    return False


def urgent_refit(turn,role,claimed,commands):
    """Finish a funded base upgrade purchase even when sunset interrupts work."""
    base=turn.station()
    if role.kind!='pioneer' or not base or base.level>=3 or not (
            base.health<.75*1500*base.level or
            (base.level==1 and turn.round_no>130 and base.health<1500)):
        return False
    name='StationUpgradeVoucher'+str(base.level)
    if any(name in u.backpack for u in turn.controllable()):
        return False
    shops=[p for p,k in turn.zones.items() if k=='weaponShop']
    price=turn.shop_prices.get(name,0)
    if not shops or price<=0:
        return False
    ore_value=sum(turn.sale_prices.get(n,0) for u in turn.workers() for n in u.backpack if n in ORE)
    if turn.gold+(ore_value if turn.is_day else 0)<price:
        return False
    # A late buyer beside the shop can finish and return after sunset. Do not
    # send a stationed operator across the map in the middle of an attack.
    if not turn.is_day and min(distance(role.pos,p) for p in shops)>3:
        return False
    if turn.gold>=price and any(distance(role.pos,p)<=1 for p in shops):
        commands[role.unit_id]={'action':'buy','name':name,'num':1}
        return True
    return walk(turn,role,shops,claimed,commands)


def develop(turn, role, claimed, commands):
    if use_carried(turn,role,claimed,commands):
        return True
    vendors = [p for p,k in turn.zones.items() if k=='vendor']
    shops = [p for p,k in turn.zones.items() if k=='weaponShop']
    if not vendors or not shops or not turn.sale_prices or not turn.shop_prices:
        return False
    builders = turn.workers()
    pioneers = [u for u in turn.controllable() if u.kind=='pioneer']
    courier = pioneers[0] if pioneers else (builders[-1] if builders else role)
    stock = Counter(item for u in turn.controllable() for item in u.backpack)
    spent = sum(25 for c in commands.values() if c.get('action')=='build' and c.get('name')!='wall')
    spent += sum(turn.shop_prices.get(c.get('name'),0)*c.get('num',1)
                 for c in commands.values() if c.get('action')=='buy')
    budget = turn.gold-spent
    if role.health<100 and budget>=turn.shop_prices.get('Medicine',10) and 'Medicine' in turn.shop_prices:
        if any(distance(role.pos,p)<=1 for p in shops):
            commands[role.unit_id] = {'action':'buy','name':'Medicine','num':1}
            return True
        return walk(turn,role,shops,claimed,commands)
    base = turn.station()
    goals = []
    if base and base.level<3 and (base.health<.75*1500*base.level or
                                 (base.level==1 and turn.round_no>130 and base.health<1500)):
        goals.append('StationUpgradeVoucher'+str(base.level))
    if any(t.kind=='rocket' and t.level==2 for t in turn.weapons()):
        goals.append('WeaponUpgradeVoucher2')
    for level in (1,2):
        if any(t.level==level for t in turn.weapons()):
            goals.append('WeaponUpgradeVoucher'+str(level))
    if base and base.level<3:
        goals.insert(0,'StationUpgradeVoucher'+str(base.level))
    if role.unit_id==courier.unit_id:
        for name in goals:
            needed = len(upgrade_targets(turn,name))-stock[name]
            price = turn.shop_prices.get(name,0)
            if needed<=0 or price<=0:
                continue
            if budget>=price and not role.backpack_full:
                if any(distance(role.pos,p)<=1 for p in shops):
                    room = max(0,(role.capacity or 40)-len(role.backpack))
                    commands[role.unit_id] = {'action':'buy','name':name,
                                              'num':min(needed,budget//price,room)}
                    return True
                return walk(turn,role,shops,claimed,commands)
            # Do not spend the repair budget on a cheaper weapon upgrade while
            # the damaged station is waiting for its next voucher.
            break
        # Stand by the shop while miners generate the next upgrade's income.
        if goals and role.kind=='pioneer':
            return walk(turn,role,shops,claimed,commands)
    if role.kind!='worker':
        return False
    inventory = Counter(n for n in role.backpack if n in ORE)
    worth = sum(n*turn.sale_prices.get(k,0) for k,n in inventory.items())
    near_vendor = any(distance(role.pos,p)<=1 for p in vendors)
    adjacent_ore = any(k in ORE and distance(role.pos,p)<=1 for p,k in turn.zones.items())
    daylight = 70-(turn.round_no-1)%130
    sell_trip = min(distance(role.pos,p) for p in vendors)+min(distance(p,base.pos) for p in vendors) if base else 0
    next_price = next((turn.shop_prices.get(n,0) for n in goals
                       if len(upgrade_targets(turn,n))>stock[n]),0)
    unlocks_upgrade = 0<next_price-budget<=worth
    if worth and (near_vendor or worth>=50 or (not adjacent_ore and worth>=15)
                  or (unlocks_upgrade and worth>=25) or role.backpack_full or daylight<=sell_trip+5):
        if near_vendor:
            name = max(inventory,key=lambda k:inventory[k]*turn.sale_prices.get(k,0))
            commands[role.unit_id] = {'action':'sell','name':name,'num':inventory[name]}
            return True
        return walk(turn,role,vendors,claimed,commands)
    def available(p):
        working = [u for u in builders if distance(u.pos,p)==1]
        owner = min(working,key=lambda u:u.unit_id) if working else None
        return distance(role.pos,p)==1 or p not in claimed
    mines = [p for p,k in turn.zones.items() if k in ORE and turn.sale_prices.get(k,0)>0
             and available(p)]
    def income_rate(p):
        travel=max(0,distance(role.pos,p)-1)
        selling=min(distance(p,v) for v in vendors)
        # A visible opposing miner can exhaust a ten-unit deposit before our
        # arrival. Discount the remaining harvest rather than chasing it.
        enemy=min((distance(u.pos,p) for u in turn.enemies
                   if u.kind=='worker' and u.health>0),default=100)
        amount=max(1,min(10,10-max(0,travel-max(0,enemy-1))))
        return amount*turn.sale_prices[turn.zones[p]]/(7+travel+.4*selling)
    mines.sort(key=lambda p:(not (distance(role.pos,p)==1 and turn.zones[p]!='stone'),
                             -income_rate(p),p.x,p.y))
    if not role.backpack_full:
        for mine in mines[:4]:
            if distance(role.pos,mine)==1:
                commands[role.unit_id] = collect_command(mine)
                claimed.add(mine)
                return True
            if walk(turn,role,[mine],claimed,commands):
                claimed.add(mine)
                return True
    if worth:
        return walk(turn,role,vendors,claimed,commands)
    return False
