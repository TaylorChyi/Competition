"""Official rule edge cases needed for adversarial policy comparisons."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT/'CoreGeek/src')]
from agent.protocol import Pos
from lab.arena import Arena, Piece, TEAMS
from tools.run_league import half_winner, fixture_winner, score


class PairedScoring(unittest.TestCase):
    def test_survival_score_excludes_day_base_was_destroyed(self):
        result={'nightHp':[200,0,0], 'killPoints':17}
        self.assertEqual(score(result),27)

    def test_destruction_order_beats_kills_but_survivors_use_score_not_hp(self):
        early={'baseDeathRound':100,'killPoints':100,'nightHp':[0,0]}
        later={'baseDeathRound':200,'killPoints':0,'nightHp':[10,0]}
        self.assertEqual(half_winner(early,later),-1)
        left={'baseDeathRound':None,'killPoints':10,'nightHp':[100,100]}
        right={'baseDeathRound':None,'killPoints':11,'nightHp':[1,1]}
        self.assertEqual(half_winner(left,right),-1)
        right['killPoints']=10
        self.assertEqual(half_winner(left,right),0)

    def test_split_halves_use_total_scores_and_draw_stays_draw(self):
        halves=[{'outcome':1,'scores':[30,10]}, {'outcome':-1,'scores':[10,20]}]
        self.assertEqual(fixture_winner(halves),1)
        halves[1]['scores']=[0,20]
        self.assertEqual(fixture_winner(halves),0)
        halves[1]['outcome']=1
        self.assertEqual(fixture_winner(halves),1)


class AdversarialRules(unittest.TestCase):
    def test_following_a_departing_character_succeeds_but_swap_fails(self):
        for swap in (False,True):
            with self.subTest(swap=swap):
                game=Arena(1);game.number=10;game.mines={}
                workers=[p for p in game.pieces if p.uid in (10010,10012)]
                workers[0].pos=Pos(10,10);workers[1].pos=Pos(11,10)
                game.settle({'challenger':{
                    '10010':{'action':'move','targetPos':[{'x':11,'y':10}]},
                    '10012':{'action':'move','targetPos':[{'x':10 if swap else 12,'y':10}]}
                },'defender':{}})
                self.assertEqual([p.pos.x for p in workers],[10,11] if swap else [11,12])

    def test_summon_cost_limit_and_extra_wave_target(self):
        game = Arena(6, commerce=True)
        worker = next(p for p in game.pieces if p.uid == 10010)
        worker.pos = Pos(24,20)
        game.gold['challenger'] = 1100
        game.number = 1
        game.settle({'challenger':{'10010':{'action':'buy','name':'LargeRobotSummonOrder','num':11}},'defender':{}})
        self.assertEqual(game.gold['challenger'],0)
        command = {'challenger':{'10010':{'action':'use','name':'LargeRobotSummonOrder'}},'defender':{}}
        for number in range(2,12):
            game.number=number
            game.settle(command)
            self.assertTrue(game.results['challenger']['10010'])
        game.number=12
        game.settle(command)
        self.assertFalse(game.results['challenger']['10010'])
        self.assertEqual(worker.backpack,['LargeRobotSummonOrder'])
        game.spawn(0)
        counts={t:sum(p.kind=='largeRobot' and p.team==t for p in game.pieces) for t in TEAMS}
        self.assertEqual(counts,{'challenger':0,'defender':10})

    def test_night_summon_waits_until_next_night(self):
        game=Arena(7,commerce=True)
        worker=next(p for p in game.pieces if p.uid==10010)
        worker.backpack=['SmallRobotSummonOrder']
        game.number=80
        game.settle({'challenger':{'10010':{'action':'use','name':'SmallRobotSummonOrder'}},'defender':{}})
        self.assertEqual(game.pending_summons[(1,'defender')]['smallRobot'],1)
        self.assertFalse(game.pending_summons.get((0,'defender')))

    def test_bomb_damage_is_simultaneous_and_dizzy_last_five_rounds(self):
        for item in ('Bomb','DizzyWeapon'):
            with self.subTest(item=item):
                game=Arena(1,commerce=True)
                game.pieces=[Piece(10013,'station',Pos(5,5),1500,'challenger'),
                             Piece(20013,'station',Pos(35,5),1500,'defender'),
                             Piece(10010,'worker',Pos(0,0),220,'challenger',backpack=[item]),
                             Piece(30000,'smallRobot',Pos(8,5),40,'challenger')]
                game.number=71
                game.settle({'challenger':{'10010':{'action':'use','name':item,'targetPos':[{'x':8,'y':5}]}},'defender':{}})
                if item=='Bomb':
                    self.assertEqual(game.pieces[-1].hp,0)
                    self.assertEqual(game.base('challenger').hp,1495)
                    self.assertEqual(game.metrics['challenger']['killPoints'],1)
                else:
                    for number in range(72,76):
                        game.number=number
                        game.settle(dict.fromkeys(TEAMS,{}))
                    self.assertEqual(game.base('challenger').hp,1500)
                    game.number=76
                    game.settle(dict.fromkeys(TEAMS,{}))
                    self.assertEqual(game.base('challenger').hp,1495)

    def test_operator_cannot_move_and_fire_in_same_turn(self):
        game=Arena(1)
        game.pieces.extend([Piece(40000,'railgun',Pos(4,23),1000,'challenger'),
                            Piece(30000,'smallRobot',Pos(2,23),40,'challenger')])
        game.number=71
        game.settle({'challenger':{'10010':{'action':'move','targetPos':[{'x':5,'y':22}]},
                                  '40000':{'action':'attack','controllerId':'10010','targetPos':[{'x':2,'y':23}]}},'defender':{}})
        self.assertFalse(game.results['challenger']['40000'])
        self.assertEqual(game.metrics['challenger']['shots'],0)

    def test_wall_repair_restores_existing_level(self):
        game=Arena(1,commerce=True);game.number=20
        worker=next(p for p in game.pieces if p.uid==10010)
        worker.pos=Pos(4,22);worker.backpack=['WallFixer']
        wall=Piece(40000,'wall',Pos(3,22),50,'challenger',2)
        game.pieces.append(wall)
        game.settle({'challenger':{'10010':{'action':'use','name':'WallFixer','targetPos':[wall.pos.dump()]}},'defender':{}})
        self.assertEqual((wall.hp,wall.level),(1500,2))


if __name__=='__main__':
    unittest.main()
