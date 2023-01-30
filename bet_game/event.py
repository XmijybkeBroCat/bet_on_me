from .player import PlayerManager
from .quest import QuestPool
from .utils import GameplayError
import random

class RandomEvent:
    def __init__(
        self,
        pm:PlayerManager,
        game_type='arcaea'
    ):
        self.pm = pm
        self.event = [
            # 若无特殊说明，event效果只在一个turn内生效
            self.absolute_advantage,
            # 绝对优势：所有玩家分数取绝对值（立即生效）
            self.bonus_time,
            # 福利时间：下注成功的玩家可以获得双倍奖励
            self.risk_aversion,
            # 风险规避：下注失败的玩家不会扣除积分
            self.winner_takes_all,
            # 赢家通吃：游玩阶段仅第一名玩家可以获得ceil(n/2)积分，其余为0积分
            self.normal_distribution,
            # 正态分布：游玩阶段最靠中间的玩家获得floor(n/2积分)，此后每向外一名获得积分少1
            self.poverty_relief,
            # 精准扶贫：所有分数最低的玩家立刻获得n积分
            self.no_need_to_hesitate,
            # 不必犹豫：成为下注目标的玩家不会被扣除积分
            self.traffic_collision,
            # 交通事故：结束阶段，若x个人同时下注到了同一个玩家，则每个玩家扣x-1分
            self.popular_player,
            # 人气选手：结束阶段，被下注次数最多的玩家获得2*x分，x为被下注次数
            self.see_you_next_time,
            # 下次一定：下个回合抽取两个事件
            self.be_patient,
            # 你先别急：结束阶段，所有分数最低的玩家获得n积分
            self.sing_along,
            # 跟着歌唱：游玩时玩家需唱打
            self.nothing_happend
            # 无事发生：真的无事发生
        ]

        self.arc_event = [
            self.the_slower_the_simpler,
            # 越慢越水：游玩时玩家需在2.0以下流速进行游玩
            self.rush_hour
            # 极速时刻：游玩时玩家需使用最高速进行游玩
        ]

        self.phi_event = [
            self.upside_down,
            # 天翻地覆：游玩时玩家需旋转设备180°进行游玩
            self.accurate_hit
        ]
        self.double_event = False

        if game_type == 'arcaea':
            self.event.extend(self.arc_event)
        elif game_type == 'phigros':
            self.event.extend(self.phi_event)
        else:
            raise GameplayError("Currently Only Support arcaea and phigros")

    def draw_event(self):
        if self.double_event:
            self.double_event = False
            event_list = random.sample(self.event, 2)
            for event in event_list:
                event()
        else:
            event = random.choice(self.event)
            event()

    def absolute_advantage(self):
        print("-----------------------------------------------")
        print("Event: \'absolute\' advantage")
        print("All player scores are taken as absolute values (immediately)")
        print("-----------------------------------------------")
        for player in self.pm.player_list:
            player.score = abs(player.score)

    def bonus_time(self):
        print("-----------------------------------------------")
        print("Event: bonus time")
        print("Players who bet successfully can get double rewards")
        print("-----------------------------------------------")
        self.pm.double_reward = True

    def risk_aversion(self):
        print("-----------------------------------------------")
        print("Event: risk aversion")
        print("Players who lose bets will not be deducted points")
        print("-----------------------------------------------")
        self.pm.bet_failed_decrease = False

    def winner_takes_all(self):
        print("-----------------------------------------------")
        print("Event: winner takes all")
        print("Only the first player in the game stage can get ceil(n/2) points")
        print("        and the rest get 0 points")
        print("-----------------------------------------------")
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
        print("-----------------------------------------------")
        print("Event: normal distribution")
        print("The player who is closest to the middle of the playing stage gets floor(n/2 points)")
        print("        after that, every player outside gets 1 less points")
        print("-----------------------------------------------")
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
        print("-----------------------------------------------")
        print("Event: poverty relief")
        print("All players with the lowest score get n points immediately")
        print("-----------------------------------------------")
        min_score = None
        for player in self.pm.player_list:
            if min_score is None or player.score < min_score:
                min_score = player.score
        for player in self.pm.player_list:
            if player.score == min_score:
                player.score += self.pm.player_num

    def no_need_to_hesitate(self):
        print("-----------------------------------------------")
        print("Event: no need to hesitate")
        print("Players who become the target of betting will not be deducted points")
        print("-----------------------------------------------")
        self.pm.betted_decrease = False

    def traffic_collision(self):
        print("-----------------------------------------------")
        print("Event: traffic collsion")
        print("At the end of the turn, if x players bet on the same player")
        print("        each player will deduct x-1 points")
        print("-----------------------------------------------")
        self.pm.collision = True
    
    def popular_player(self):
        print("-----------------------------------------------")
        print("Event: popular player")
        print("At the end of the turn, the player with the most bets targets gets 2*x points")
        print("        where x is the number of bets targets")
        print("-----------------------------------------------")
        self.pm.popular = True

    def see_you_next_time(self):
        print("-----------------------------------------------")
        print("Event: see you next time")
        print("Draw two events for the next round")
        print("-----------------------------------------------")
        self.double_event = True

    def be_patient(self):
        print("-----------------------------------------------")
        print("Event: be patient")
        print("All players with the lowest score get n points at end of the turn")
        print("-----------------------------------------------")
        self.pm.patient = True

    def sing_along(self):
        print("-----------------------------------------------")
        print("Event: sing along")
        print("Player should sing to the song while playing the game")
        print("-----------------------------------------------")

    def nothing_happend(self):
        print("-----------------------------------------------")
        print("Event: nothing happened")
        print("Literally nothing happened")
        print("-----------------------------------------------")

    def the_slower_the_simpler(self):
        print("-----------------------------------------------")
        print("Event: the slower, the simpler")
        print("Players should play game in speed restriction less than 2")
        print("-----------------------------------------------")

    def rush_hour(self):
        print("-----------------------------------------------")
        print("Event: rush hour")
        print("Players should play game in max speed")
        print("-----------------------------------------------")

    def upside_down(self):
        print("-----------------------------------------------")
        print("Event: upside down")
        print("Player should play game while the device is upside down")
        print("-----------------------------------------------")

    def accurate_hit(self):
        print("-----------------------------------------------")
        print("Event: accurate hit")
        print("Player should upload the accuracy instead of the score")
        print("-----------------------------------------------")