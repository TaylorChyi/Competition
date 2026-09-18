"""Bounded shared-map bot-vs-bot simulator, NOT the official judge.

Both policies receive the documented observations and issue actual decide()
commands. Start from 75 gold, build level-one towers, carry damage across days.
Wave sizes, movement ties, targeting priority and build rings are hypotheses.
Commerce mode uses the official sample ore prices, upgrades and consumables.
No task rewards, news or direct player attacks. This remains a partial model.
"""
from collections import Counter, defaultdict
from dataclasses import dataclass, field
import random
from time import perf_counter

from agent.protocol import Pos, TOWER_RANGE_BY_LEVEL, distance, station_footprint
from agent.targeting import splash_damage
from lab.night_sim import ROBOT_STATS

WIDTH, HEIGHT = 41, 32
TEAMS = ('challenger', 'defender')
WAVES = {
    'moderate': ((10, 4, 0, 0), (16, 8, 1, 0), (20, 12, 2, 1)),
    'heavy': ((14, 6, 1, 0), (20, 10, 2, 0), (24, 14, 3, 1)),
}
PRICES = {'stone':1, 'iron':3, 'copper':5}
SHOP = {'WeaponUpgradeVoucher1':100, 'WeaponUpgradeVoucher2':150,
        'StationUpgradeVoucher1':100, 'StationUpgradeVoucher2':150,
        'WallUpgradeVoucher1':20, 'WallUpgradeVoucher2':30,
        'Medicine':10, 'WallFixer':10, 'Bomb':100, 'DizzyWeapon':100,
        'SmallRobotSummonOrder':20, 'MiddleRobotSummonOrder':30,
        'LargeRobotSummonOrder':100, 'BossRobotSummonOrder':200}
SUMMONS = {'SmallRobotSummonOrder':'smallRobot', 'MiddleRobotSummonOrder':'middleRobot',
           'LargeRobotSummonOrder':'largeRobot', 'BossRobotSummonOrder':'bossRobot'}


def wave_counts(profile, day):
    if day<3:
        return WAVES[profile][day]
    # Fixed before strategy search: retain the original first three waves,
    # extend to ten nights without tuning the schedule to a winning policy.
    small, middle, large, boss = WAVES[profile][-1]
    extra = day-2
    return small+4*extra, middle+2*extra, large+extra//3, boss+extra//4


@dataclass
class Piece:
    uid: int
    kind: str
    pos: Pos
    hp: int
    team: str
    level: int = 1
    ready: int = 0
    backpack: list[str] = field(default_factory=list)
    stunned_until: int = 0

    def cells(self):
        return station_footprint(self.pos) if self.kind == 'station' else (self.pos,)

    def dump(self, number):
        result = {'id': self.uid, 'roleType': self.kind, 'pos': self.pos.dump(),
                  'health': self.hp, 'level': self.level, 'backpack': list(self.backpack),
                  'backPackCapability': 40 if self.kind == 'pioneer' else 100,
                  'cooldown': max(0, self.ready-number)}
        if self.kind in ROBOT_STATS:
            result.update(targetTeam=self.team, abnormalState='dizzy' if number < self.stunned_until else '')
        return result


def separation(pos, unit):
    return min(distance(pos, cell) for cell in unit.cells())


def mirror(pos, station=False):
    return Pos(WIDTH - (2 if station else 1) - pos.x,
               HEIGHT - (0 if station else 1) - pos.y)


def ray_hits(origin, target, robots):
    """Intersect center-to-center segment with each robot's square cell.

    Cell-boundary tie handling is a local convention, not judge-proven behavior.
    """
    hits = []
    for robot in robots:
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
            hits.append((lower, robot.uid, robot))
    return [entry[2] for entry in sorted(hits)]


class Arena:
    def __init__(self, seed, wave='moderate', priority='nearest', nights=3, commerce=False):
        self.seed, self.wave, self.priority, self.nights = seed, wave, priority, nights
        self.rng = random.Random(seed)
        self.number = 0
        self.commerce = commerce
        self.markets = {Pos(20,16):'vendor',Pos(25,20):'weaponShop'} if commerce else {}
        self.pieces = []
        self.gold = dict.fromkeys(TEAMS, 75)
        self.results = {team: {} for team in TEAMS}
        self.metrics = {team: {'baseDeathRound': None, 'nightHp': [], 'nightOperators': [],
                              'kills': 0, 'killPoints': 0, 'shots': 0, 'foreignOnlyShots': 0,
                              'invalidCommands': 0, 'movesBlocked': 0, 'decisionMs': [],
                              'income':0, 'upgrades':[], 'nightEquipment':[], 'resourceConflicts':0}
                        for team in TEAMS}
        self.next_build = {'challenger': 40000, 'defender': 41000}
        self.next_robot = 30000
        self.pending_summons = defaultdict(Counter)
        self.summons_used = Counter()
        self.mines = {}
        for team in TEAMS:
            reflected = team == 'defender'
            offset = 10000 if reflected else 0
            for uid, kind, pos, hp in (
                (10013, 'station', Pos(7, 24), 1500),
                (10010, 'worker', Pos(5, 23), 220),
                (10011, 'pioneer', Pos(7, 25), 200),
                (10012, 'worker', Pos(5, 25), 220),
            ):
                self.pieces.append(Piece(uid+offset, kind,
                    mirror(pos, kind == 'station') if reflected else pos, hp, team))
            for pos in (Pos(12, 23), Pos(11, 19), Pos(4, 19)):
                self.mines[mirror(pos) if reflected else pos] = 10
        self.mine_kinds = dict.fromkeys(self.mines,'stone')
        if commerce:
            # Six ore locations, prices and neutral shops from request.txt.
            self.mine_kinds = {Pos(4,24):'stone',Pos(14,3):'stone',
                               Pos(25,10):'iron',Pos(8,28):'iron',
                               Pos(22,26):'copper',Pos(7,2):'copper'}
            self.mines = dict.fromkeys(self.mine_kinds,10)

    def base(self, team):
        return next(p for p in self.pieces if p.team == team and p.kind == 'station')

    def living(self):
        return [p for p in self.pieces if p.hp > 0]

    def observation(self, team):
        living = self.living()
        ours = [p for p in self.pieces if p.team == team and p.kind not in ROBOT_STATS]
        visible = [p for p in living if p.team != team and p.kind not in ROBOT_STATS
                   and (p.kind in ('station', 'wall') or any(
                       separation(p.pos, own) <= 4 for own in ours if own.hp > 0))]
        return {'roundNo': self.number,
                'mapInfo': {'width': WIDTH, 'height': HEIGHT, 'zones': [
                    {'pos': pos.dump(), 'neutralType': self.mine_kinds.get(pos,'stone')} for pos in self.mines]
                    + [{'pos':p.dump(),'neutralType':k} for p,k in self.markets.items()]},
                'teamOur': {'type': team, 'goldNum': self.gold[team],
                            'roles': [p.dump(self.number) for p in ours]},
                'teamEnemy': {'roles': [p.dump(self.number) for p in visible]},
                'robot': {'roles': [p.dump(self.number) for p in living if p.kind in ROBOT_STATS]},
                'lastRoundRoleActionResults': dict(self.results[team]),
                'vendorShopList': [{'name':k,'price':v} for k,v in PRICES.items()] if self.commerce else [],
                'weaponShopList': [{'name':k,'price':v} for k,v in SHOP.items()] if self.commerce else []}

    def begin(self):
        self.number += 1
        phase = (self.number-1) % 130
        if phase == 0:
            self.pieces = [p for p in self.pieces if p.kind not in ROBOT_STATS]
        if phase == 20 and self.number > 130:
            for piece in self.pieces:
                if piece.kind not in ('worker', 'pioneer') or piece.hp > 0 or self.base(piece.team).hp <= 0:
                    continue
                base = self.base(piece.team)
                occupied = {pos for p in self.living() for pos in p.cells()} | set(self.mines) | set(self.markets)
                options = [Pos(x, y) for x in range(WIDTH) for y in range(HEIGHT)
                           if Pos(x, y) not in occupied]
                piece.pos = min(options, key=lambda p: (separation(p, base), p.x, p.y))
                piece.hp = 200 if piece.kind == 'pioneer' else 220
        if phase == 70:
            self.spawn((self.number-1)//130)

    def spawn(self, day):
        occupied = {pos for p in self.living() for pos in p.cells()} | set(self.mines) | set(self.markets)
        # Equal kind counts for both camps, seeded central spawn. Both waves
        # remain visible to both policies, including bots heading to the rival.
        cells = [Pos(x, y) for x in range(14, 27) for y in range(4, 28)]
        wave_rng = random.Random(self.seed*1009 + day*7919)
        wave_rng.shuffle(cells)
        kinds = [kind for kind, count in zip(ROBOT_STATS, wave_counts(self.wave,day)) for _ in range(count)]
        wave_rng.shuffle(kinds)
        for kind in kinds:
            for team in TEAMS:
                pos = cells.pop()
                while pos in occupied:
                    pos = cells.pop()
                self.pieces.append(Piece(self.next_robot, kind, pos, ROBOT_STATS[kind][0], team))
                self.next_robot += 1
                occupied.add(pos)
        for team in TEAMS:
            for kind, count in sorted(self.pending_summons.pop((day, team), {}).items()):
                for _ in range(count):
                    pos = cells.pop()
                    while pos in occupied:
                        pos = cells.pop()
                    self.pieces.append(Piece(self.next_robot, kind, pos, ROBOT_STATS[kind][0], team))
                    self.next_robot += 1
                    occupied.add(pos)

    def settle(self, commands):
        living = self.living()
        robots = [p for p in living if p.kind in ROBOT_STATS]
        by_id = {p.uid: p for p in living}
        occupied = {pos for p in living for pos in p.cells()} | set(self.mines) | set(self.markets)
        damage = defaultdict(int)
        shooter_damage = defaultdict(lambda: defaultdict(int))
        proposals, move_owners = {}, {}
        self.results = {team: {} for team in TEAMS}
        is_day = (self.number-1) % 130 < 70
        starting_mines = dict(self.mines)
        for team in TEAMS:
            used = set()
            for uid, command in sorted(commands[team].items(), key=lambda item: int(item[0])):
                actor = by_id.get(int(uid))
                targets = [Pos.load(pos) for pos in command.get('targetPos', [])]
                action = command.get('action')
                valid = bool(actor and actor.team == team and actor.kind not in ROBOT_STATS)
                if valid and action == 'attack':
                    operator = by_id.get(int(command.get('controllerId', 0)))
                    valid = (not is_day and actor.kind in TOWER_RANGE_BY_LEVEL
                             and actor.ready <= self.number and operator is not None
                             and operator.team == team and operator.kind in ('worker', 'pioneer')
                             and operator.uid not in used and str(operator.uid) not in commands[team]
                             and operator.uid not in commands[team]
                             and distance(actor.pos, operator.pos) <= 1)
                    if valid:
                        reach = TOWER_RANGE_BY_LEVEL[actor.kind][actor.level-1]
                        count = actor.level if actor.kind in ('gatling', 'rocket') else 1
                        valid = len(targets) == count and all(0 <= p.x < WIDTH and 0 <= p.y < HEIGHT
                                     and distance(actor.pos, p) <= reach for p in targets)
                    if valid and actor.kind == 'gatling':
                        vectors = [(p.x-actor.pos.x, p.y-actor.pos.y) for p in targets]
                        valid = all(a*c+b*d >= 0 for a,b in vectors for c,d in vectors)
                    if valid:
                        used.add(operator.uid)
                        if actor.kind == 'rocket':
                            actor.ready = self.number + 4
                        for target in targets:
                            self.metrics[team]['shots'] += 1
                            if actor.kind == 'rocket':
                                hits = [(r, splash_damage(target, r.pos)) for r in robots]
                            else:
                                line = ray_hits(actor.pos, target, robots)
                                if actor.kind == 'gatling':
                                    hits = [(r, 10) for r in line[:1]]
                                else:
                                    hits, energy = [], 10*actor.level
                                    for robot in line:
                                        hit = min(energy, robot.hp)
                                        hits.append((robot, hit))
                                        energy -= hit
                                        if not energy:
                                            break
                            self.metrics[team]['foreignOnlyShots'] += (any(hit > 0 and r.team != team for r,hit in hits)
                                and not any(hit > 0 and r.team == team for r,hit in hits))
                            for robot, hit in hits:
                                damage[robot.uid] += hit
                                shooter_damage[robot.uid][team] += hit
                elif valid and action in ('buy','sell','use'):
                    name, count = command.get('name',''), command.get('num',1)
                    valid = self.commerce and actor.kind in ('worker','pioneer') and isinstance(count,int) and count>0
                    if valid and action=='sell':
                        valid = (name in PRICES and actor.backpack.count(name)>=count and
                                 any(kind=='vendor' and distance(actor.pos,p)<=1 for p,kind in self.markets.items()))
                        if valid:
                            self.gold[team] += PRICES[name]*count
                            self.metrics[team]['income'] += PRICES[name]*count
                            for _ in range(count):
                                actor.backpack.remove(name)
                    elif valid and action=='buy':
                        valid = (name in SHOP and self.gold[team]>=SHOP[name]*count
                                 and len(actor.backpack)+count<=(40 if actor.kind=='pioneer' else 100)
                                 and any(kind=='weaponShop' and distance(actor.pos,p)<=1 for p,kind in self.markets.items()))
                        if valid:
                            self.gold[team] -= SHOP[name]*count
                            actor.backpack.extend([name]*count)
                    elif valid:
                        valid = name in actor.backpack
                        if valid and name=='Medicine':
                            actor.hp = 200 if actor.kind=='pioneer' else 220
                        elif valid and 'UpgradeVoucher' in name:
                            unit = next((p for p in living if len(targets)==1 and p.pos==targets[0] and p.team==team),None)
                            kinds = (('station',) if name.startswith('Station') else
                                     ('wall',) if name.startswith('Wall') else ('gatling','railgun','rocket'))
                            valid = (unit is not None and unit.kind in kinds and name[-1]==str(unit.level)
                                     and unit.level<3 and distance(actor.pos,unit.pos)<=1)
                            if valid:
                                unit.level += 1
                                unit.hp = 1500*unit.level if unit.kind=='station' else 500+500*unit.level
                                self.metrics[team]['upgrades'].append([self.number,unit.kind,unit.level])
                        elif valid and name=='WallFixer':
                            wall = next((p for p in living if len(targets)==1 and p.pos==targets[0]
                                         and p.kind=='wall' and p.team==team),None)
                            valid = wall is not None and distance(actor.pos,wall.pos)<=1
                            if valid:
                                wall.hp = 500+500*wall.level
                        elif valid and name in ('Bomb','DizzyWeapon'):
                            valid = len(targets)==1 and 0<=targets[0].x<WIDTH and 0<=targets[0].y<HEIGHT
                            if valid:
                                for robot in robots:
                                    if distance(robot.pos,targets[0])<=1:
                                        if name=='Bomb':
                                            damage[robot.uid] += 100
                                            shooter_damage[robot.uid][team] += 100
                                        else:
                                            robot.stunned_until = max(robot.stunned_until,self.number+5)
                        elif valid and name in SUMMONS:
                            day=(self.number-1)//130
                            valid = self.summons_used[(day,team)]<10
                            if valid:
                                target_team=TEAMS[1-TEAMS.index(team)]
                                night=day+(not is_day)
                                self.pending_summons[(night,target_team)][SUMMONS[name]] += 1
                                self.summons_used[(day,team)] += 1
                                self.metrics[team].setdefault('summons',[]).append([self.number,name,night+1])
                        else:
                            valid = False
                        if valid:
                            actor.backpack.remove(name)
                elif valid and action == 'move':
                    valid = actor.kind in ('worker', 'pioneer') and len(targets) == 1
                    if valid:
                        p = targets[0]
                        valid = distance(actor.pos, p) == 1 and 0 <= p.x < WIDTH and 0 <= p.y < HEIGHT
                        if valid:
                            proposals[actor.uid], move_owners[actor.uid] = p, team
                elif valid and action in ('build', 'collect'):
                    valid = (actor.kind == 'worker' and len(targets) == 1
                             and distance(actor.pos, targets[0]) == 1 and (is_day or action=='collect'))
                    if valid and action == 'collect':
                        p = targets[0]
                        # Official rule: every simultaneous collector receives
                        # one ore even when fewer units remain than collectors.
                        valid = starting_mines.get(p,0)>0 and len(actor.backpack) < 100
                        if valid:
                            actor.backpack.append(self.mine_kinds.get(p,'stone'))
                            self.mines[p] -= 1
                    elif valid:
                        p, kind = targets[0], command.get('name')
                        tower = kind in TOWER_RANGE_BY_LEVEL
                        previous = next((q for q in living if q.team==team and q.pos==p
                                         and (q.kind in TOWER_RANGE_BY_LEVEL if tower else q.kind=='wall')),None)
                        valid = ((p not in occupied or previous is not None) and 0 <= p.x < WIDTH and 0 <= p.y < HEIGHT
                                 and separation(p, self.base(team)) == (1 if tower else 2))
                        if tower:
                            valid = valid and self.gold[team] >= 25 and (previous is not None or sum(
                                q.team == team and q.kind in TOWER_RANGE_BY_LEVEL for q in self.living()) < 3)
                        else:
                            valid = valid and kind == 'wall' and 'stone' in actor.backpack
                        if valid:
                            if previous is not None:
                                previous.hp=0
                            if tower:
                                self.gold[team] -= 25
                            else:
                                actor.backpack.remove('stone')
                            self.pieces.append(Piece(self.next_build[team], kind, p, 1000, team))
                            self.next_build[team] += 1
                            occupied.add(p)
                else:
                    valid = False
                self.results[team][str(uid)] = bool(valid)
                self.metrics[team]['invalidCommands'] += not valid
        # Robots act from the same observed state, even when lethally hit this turn.
        if not is_day:
            for robot in robots:
                if self.number < robot.stunned_until:
                    continue
                base = self.base(robot.team)
                defenders = [p for p in living if p.team == robot.team and p.kind not in ROBOT_STATS]
                eligible = [p for p in defenders if separation(robot.pos, p) <= 3]
                if eligible and (self.priority != 'advance' or separation(robot.pos, base) <= 3):
                    victim = min(eligible, key=lambda p: (
                        0 if self.priority in ('base', 'advance') and p.kind == 'station' else 1,
                        separation(robot.pos, p), p.uid))
                    damage[victim.uid] += ROBOT_STATS[robot.kind][1]
                    continue
                options = [Pos(robot.pos.x+dx, robot.pos.y+dy)
                           for dx in (-1,0,1) for dy in (-1,0,1) if dx or dy]
                options = [p for p in options if 0 <= p.x < WIDTH and 0 <= p.y < HEIGHT
                           and p not in occupied and separation(p, base) <= separation(robot.pos, base)]
                if options:
                    def key(p):
                        tie = (robot.uid*73856093 ^ self.number*19349663 ^ p.x*83492791
                               ^ p.y*2654435761 ^ self.seed) & 0xffffffff
                        return separation(p, base), tie
                    proposals[robot.uid] = min(options, key=key)
                elif eligible:
                    victim = min(eligible, key=lambda p: (separation(robot.pos, p), p.uid))
                    damage[victim.uid] += ROBOT_STATS[robot.kind][1]
        counts = Counter(proposals.values())
        # Occupied destinations are usable when their occupant also completes
        # a move. Cancel contests and swaps, then propagate blocked chains.
        owners = {cell:p.uid for p in living for cell in p.cells()}
        fixed = set(self.mines) | set(self.markets)
        accepted = {uid:pos for uid,pos in proposals.items() if pos not in fixed and counts[pos]==1}
        swaps = {uid for uid,pos in accepted.items() if owners.get(pos) in accepted
                 and accepted[owners[pos]]==by_id[uid].pos}
        accepted = {uid:pos for uid,pos in accepted.items() if uid not in swaps}
        while True:
            blocked = {uid for uid,pos in accepted.items() if pos in owners and owners[pos] not in accepted}
            if not blocked:
                break
            accepted = {uid:pos for uid,pos in accepted.items() if uid not in blocked}
        for uid, pos in proposals.items():
            if uid in accepted:
                by_id[uid].pos = pos
            elif uid in move_owners:
                team = move_owners[uid]
                self.results[team][str(uid)] = False
                self.metrics[team]['movesBlocked'] += 1
        for piece in living:
            piece.hp = max(0, piece.hp-damage[piece.uid])
            if piece.kind in ROBOT_STATS and piece.hp == 0 and shooter_damage[piece.uid]:
                credit = max(shooter_damage[piece.uid], key=shooter_damage[piece.uid].get)
                self.metrics[credit]['kills'] += 1
                self.metrics[credit]['killPoints'] += ROBOT_STATS[piece.kind][2]
        for pos, amount in list(self.mines.items()):
            if amount > 0:
                continue
            del self.mines[pos]
            kind = self.mine_kinds.pop(pos,'stone')
            occupied = {cell for unit in self.living() for cell in unit.cells()} | set(self.mines) | set(self.markets)
            free = [Pos(x, y) for x in range(WIDTH) for y in range(HEIGHT)
                    if Pos(x,y) not in occupied and all(separation(Pos(x,y), self.base(t)) > 2 for t in TEAMS)]
            if free:
                replacement = self.rng.choice(free)
                self.mines[replacement] = 10
                self.mine_kinds[replacement] = kind
        for team in TEAMS:
            metric = self.metrics[team]
            if self.base(team).hp == 0 and metric['baseDeathRound'] is None:
                metric['baseDeathRound'] = self.number
            if self.number % 130 == 0:
                metric['nightHp'].append(self.base(team).hp)
                metric['nightEquipment'].append({p.kind+'_'+str(p.uid):[p.level,p.hp]
                    for p in self.pieces if p.team==team and p.kind in ('station','gatling','railgun','rocket')})
                metric['nightOperators'].append(sum(p.hp > 0 and p.team == team
                        and p.kind in ('worker', 'pioneer') for p in self.pieces))

    def run(self, policies):
        for _ in range(130*self.nights):
            self.begin()
            observations = {team: self.observation(team) for team in TEAMS}
            commands = {}
            for team in TEAMS:
                started = perf_counter()
                commands[team] = policies[team](observations[team]) if self.base(team).hp > 0 else {}
                self.metrics[team]['decisionMs'].append((perf_counter()-started)*1000)
            self.settle(commands)
        for team in TEAMS:
            values = self.metrics[team].pop('decisionMs')
            self.metrics[team]['p95DecisionMs'] = round(sorted(values)[int(len(values)*.95)], 3)
            self.metrics[team]['survivedTwoNights'] = self.metrics[team]['nightHp'][1] > 0
            self.metrics[team]['survivedNights'] = sum(hp > 0 for hp in self.metrics[team]['nightHp'])
            self.metrics[team]['survivalRounds'] = self.metrics[team]['baseDeathRound'] or self.nights*130
        return self.metrics
