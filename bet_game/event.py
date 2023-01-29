from .player import PlayerManager
from .quest import QuestPool
from .utils import GameplayError
import random

class RandomEvent:
    def __init__(
        self,
        pm:PlayerManager,
        game_type='arcaea',
        random_p=0.5
    ):
        self.pm = pm
        self.event = [
            # 若无特殊说明，event效果只在一个turn内生效
            self.absolute_advantage,
            # 绝对优势：所有玩家分数取绝对值（立即生效）
            self.bonus_time,
            # 福利时间：bet成功的玩家可以获得双倍奖励
            self.risk_aversion,
            # 风险规避：bet失败的玩家不会扣除积分
            self.winner_takes_all,
            # 赢家通吃：游玩阶段仅第一名玩家可以获得ceil(n/2)积分，其余为0积分
            self.normal_distribution,
            # 正态分布：游玩阶段最靠中间的玩家获得floor(n/2积分)，此后每向外一名获得积分少1
            self.poverty_relief,
            # 精准扶贫：所有分数最低的玩家立刻获得n积分
            self.no_need_to_hesitate,
            # 不必犹豫：成为bet目标的玩家不会被扣除积分
            self.sing_along
            # 跟着歌唱：游玩时玩家需唱打
        ]

        self.arc_event = [
            self.the_slower_the_simpler,
            # 越慢越水：游玩时玩家需在2.0以下流速进行游玩
            self.rush_hour
            # 尖峰时刻：游玩时玩家需使用最高速进行游玩
        ]

        self.phi_event = [
            self.upside_down
            # 天翻地覆：游玩时玩家需旋转设备180°进行游玩
        ]

        self.random_p = random_p

        if game_type == 'arcaea':
            self.event.extend(self.arc_event)
        elif game_type == 'phigros':
            self.event.extend(self.phi_event)
        else:
            raise GameplayError("Currently Only Support arcaea and phigros")

    def draw_event(self):
        if random.random() < self.random_p:
            event = random.choice(self.event)
            event()
        else:
            print("No event in this turn")

    def absolute_advantage(self):
        print("Event: \'absolute\' advantage")
        print("Every Player's score will immediately get the absolute value")
        for player in self.pm.player_list:
            player.score = abs(player.score)

    def bonus_time(self):
        print("Event: bonus time")
        print("Player who bet successfully will get double reward (1 turn)")
        self.pm.double_reward = True

    def risk_aversion(self):
        print("Event: risk aversion")
        print("Player who fails the bet will not get score decresed (1 turn)")
        self.pm.bet_failed_decrease = False

    def winner_takes_all(self):
        print("Event: winner takes all")
        print("Only the top 1 player in game will get upper(n+1)/2 score")
        def winner_takes_all_rank_to_score(member):
            pt = (len(member)+1)//2
            for i, player in enumerate(member):
                player.rank = i
                player.cur_pt = pt
                player.score += pt
                if pt > 0:
                    pt = 0
        self.pm.rank_to_score = winner_takes_all_rank_to_score

    def normal_distribution(self):
        print("Event: normal distribution")
        print("Player at the middle will get the highest score")
        def normal_distribution_rank_to_score(member):
            n = self.pm.player_num
            if n % 2 == 0:
                max_posi = [n//2, n//2-1]
                for i, player in enumerate(member):
                    pt = n//2 - min(abs(i-max_posi[0]), abs(i-max_posi[1]))
                    player.rank = i
                    player.cur_pt = pt
                    player.score += pt
            else:
                max_posi = n // 2
                for i, player in enumerate(member):
                    pt = n//2 - abs(i-max_posi)
                    player.rank = i
                    player.cur_pt = pt
                    player.score += pt
        self.pm.rank_to_score = normal_distribution_rank_to_score

    def poverty_relief(self):
        print("Event: poverty relief")
        print("Player who gets the least score will get bonus n score")
        min_score = None
        for player in self.pm.player_list:
            if min_score is None or player.score < min_score:
                min_score = player.score
        for player in self.pm.player_list:
            if player.score == min_score:
                player.score += self.pm.player_num

    def no_need_to_hesitate(self):
        print("Event: no need to hesitate")
        print("Player who got bet will not decrease the score")
        self.pm.betted_decrease = False

    def sing_along(self):
        print("Event: sing along")
        print("Player should sing to the song while playing the game")

    def the_slower_the_simpler(self):
        print("Event: the slower, the simpler")
        print("Players should play game in speed restriction less than 2")

    def rush_hour(self):
        print("Event: rush hour")
        print("Players should play game in max speed")

    def upside_down(self):
        print("Event: upside down")
        print("Player should playe the game while the device is upside down")
