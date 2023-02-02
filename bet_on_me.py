# Originally contributed by Xmijybke_BroCat
# Used only in 'Bet on Me' game made by Pure Rhythm

"""
写着玩玩，用不用无所谓
还没做测试，可能有bug
以及暂时不建议在酒吧点炒饭

大致流程就是先点击'Add Player'按钮添加玩家，可以一个一个添也可以一次性添几个，然后主界面上填写轮次，游戏开始

每一轮游戏先点击'Event'按钮，会生成这一轮的事件并且执行，同时生成曲目，再点击'Bet'按钮提交下注情况，游玩完成
后点击'Play'按钮提交成绩，最后点击'Result'按钮显示本轮游戏积分情况
（这里我插了几个assert，如果按了没反应就说明顺序按错了

在提交下注情况和游玩成绩时可以利用Spinbox在列表里翻找，也可以直接输入全名（没做文本校验，千万别点炒饭！！！）
游玩成绩支持小数输入（如果使用的是Accuracy的话）

此外，随时可以点击'Song'更换歌曲、点击'Points'更新主界面上的积分情况

曲目的生成权重写在SongData.json里了，默认都是1，可以自己点进去改，也可以用程序批量改，格式一致就行
（哦对了，曲库里忘删Legacy了，回头再说吧[开摆]）

最后：希望没有Bug[合十][合十][合十]
"""

import tkinter as tk
from random import sample
import json
from math import ceil
from typing import Literal


EVENTS = {'绝对优势': '事件抽取阶段结束后，所有玩家分数立刻取绝对值',
          '福利时间': '下注结算阶段，下注成功的玩家可以获得双倍积分',
          '风险规避': '下注结算阶段，下注失败的玩家不会获得积分',
          '赢家通吃': '游玩结算阶段，仅第一名玩家获得ceil(n / 2)积分，其余玩家不会获得积分',
          '正态分布': '游玩结算阶段，排名为中位数玩家获得int(n / 2)积分，此后每向外一名玩家获得积分数量减少1',
          '精准扶贫': '事件抽取阶段结束后，所有分数最低的玩家立刻获得n积分',
          '不必犹豫': '游玩结算阶段，成为下注目标的玩家不会被扣除积分',
          '交通事故': '结束阶段，若x为玩家同时下注到了同一玩家，则此x为玩家每人扣x - 1分',
          '人气选手': '结束阶段，被下注次数最多的玩家获得x * 2分，x为该玩家的被下注次数',
          '下次一定': '下一次事件抽取阶段，抽取两个不在同一时段生效的事件',
          '你先别急': '结束阶段，所有分数最低的玩家获得n积分',
          '跟着歌唱': '游玩阶段，所有玩家需进行唱打',
          '天翻地覆': '游玩阶段，玩家需旋转设备180°游玩',
          '精准打击': '游玩阶段，玩家需上传游玩的Accuracy而非分数'}

SONGS = []
WEIGHTS = []
song_data: dict = json.load(open('SongData.json', 'r', encoding='UTF-8'))
for s_ in song_data.values():
    SONGS.append(s_['difficulty'])
    WEIGHTS.append(s_['weight'])


class Start:
    def __init__(self):
        self.mw = tk.Tk()
        self.mw.title("Bet on Me for Phigros")
        self.mw.geometry('1000x500+250+250')
        self.player_list = []
        self.player_list_show = tk.StringVar(self.mw)
        self.player_list_show.set('Joined Players: \n' + '\n'.join(s for s in self.player_list))

        self.game_name = tk.Label(self.mw, text='Bet on Me', font=("Cambria", 48))
        self.game_name.pack(side='top')
        self.players = tk.Label(self.mw, textvariable=self.player_list_show)
        self.players.pack(side='top')

        self.rs = tk.Frame(self.mw)  # rs = Round set
        self.rs_hint = tk.Label(self.rs, text='Set game rounds')
        self.rs_hint.pack(side='left')
        self.rs_entry = tk.Entry(self.rs)
        self.rs_entry.pack(side='left')
        self.rs.pack(side='top')

        self.btns = tk.Frame(self.mw)  # btns = Buttons
        self.add_button = tk.Button(self.btns, text='Add Player', command=self.add_player_windows)
        self.add_button.pack(side='left')
        self.begin_button = tk.Button(self.btns, text='Start Game', command=self.begin_game)
        self.begin_button.pack(side='right')
        self.btns.pack(side='top')

        self.mw.mainloop()

    def add_player_windows(self):
        hint = "Please entry players' name with sep=', '"
        windows = tk.Tk()
        windows.title("Entry players' name")
        windows.geometry('300x100+400+250')

        entry = tk.Entry(windows)
        hint_label = tk.Label(windows, text=hint)
        hint_label.pack(side='top')
        entry.pack(side='top')

        sure_button = tk.Button(windows, text='Sure', command=lambda: (self.add_player(entry), windows.destroy()))
        sure_button.pack(side='top')

        windows.mainloop()

    def add_player(self, entry):
        players = list(entry.get().split(', '))
        self.player_list += players
        self.player_list_show.set('Joined Players: \n' + '\n'.join(s for s in self.player_list))

    def begin_game(self):
        Game(pl=self.player_list, gr=int(self.rs_entry.get()))


class Game:
    def __init__(self, pl: list, gr: int):
        self.mw = tk.Tk()
        self.mw.title('Bet on Me for Phigros')
        self.mw.geometry('800x500+200+100')
        self.pl = pl  # pl = player list
        self.pn = len(pl)  # pn = player number
        self.gr = gr  # gr = game round
        self.pts = {}
        self.bets = {}
        self.result = {}
        self.report = {}
        self.betted_count = {}
        for s in self.pl:
            self.pts[s] = 0
            self.bets[s] = (None, None)
            self.result[s] = 0.0
            self.report[s] = [0, 0, 0, 0, 0, 0]
            self.betted_count[s] = 0

        self.nre = None  # nre = Next round event
        self.bte = None  # bte = Bet time event
        self.poe = None  # poe = Play over event
        self.ree = None  # ree = Round end event
        self.crt_step: Literal['Event', 'Bet', 'Play', 'Result'] = 'Event'

        self.event_text = tk.StringVar(self.mw)
        self.event_text.set('The event of this round is None!')
        self.event_hint = tk.Label(self.mw, textvariable=self.event_text)
        self.event_hint.pack(side='top')
        self.event_meaning_text = tk.StringVar(self.mw)
        self.event_meaning_text.set('')
        self.event_meaning_hint = tk.Label(self.mw, textvariable=self.event_meaning_text)
        self.event_meaning_hint.pack(side='top')

        self.song_text = tk.StringVar(self.mw)
        self.song_text.set('The song of this round is None!')
        self.song_hint = tk.Label(self.mw, textvariable=self.song_text)
        self.song_hint.pack(side='top')

        self.player_pts_place = tk.Frame(self.mw)
        self.player_pts_show = tk.Frame(self.player_pts_place)
        self.player_pts_show.pack()
        self.player_pts_place.pack(side='top')
        self.show_pts()

        self.btns = tk.Frame(self.mw)
        self.con_btn = tk.Button(self.btns, text='Event', command=self.round_start)
        self.con_btn.pack(side='left')
        self.song_btn = tk.Button(self.btns, text='Song', command=self.song)
        self.song_btn.pack(side='left')
        self.bet_btn = tk.Button(self.btns, text='Bet', command=self.bet)
        self.bet_btn.pack(side='left')
        self.rst_btn = tk.Button(self.btns, text='Play', command=self.play_end)
        self.rst_btn.pack(side='left')
        self.ro_btn = tk.Button(self.btns, text='Result', command=self.round_end)
        self.ro_btn.pack(side='left')
        self.show_btn = tk.Button(self.btns, text='Points', command=self.show_pts)
        self.show_btn.pack(side='left')
        self.btns.pack(side='top')

        self.mw.mainloop()

    @staticmethod
    def raise_error(text: str):
        rs = tk.Tk()
        rs.title("Warning")
        rs.geometry("400x140+520+300")
        rs_label = tk.Label(rs, text=text, width=50, height=4)
        rs_label.pack(side="top")
        rs_btn = tk.Button(rs, text="Sure", width=10, height=1, command=rs.destroy)
        rs_btn.pack(side="top")
        rs.mainloop()

    def show_pts(self):
        self.player_pts_show.destroy()
        self.player_pts_show = tk.Frame(self.player_pts_place)
        for s in self.pl:
            row = tk.Frame(self.player_pts_show)
            name = tk.Label(row, text=s)
            name.pack(side='left')
            pts = tk.Label(row, text=self.pts[s])
            pts.pack(side='right')
            row.pack(side='top')
        self.player_pts_show.pack(side='top')

    def round_start(self):
        assert self.crt_step == 'Event'
        self.crt_step = 'Bet'
        if self.gr > 0:
            self.gr -= 1

            if self.nre == '下次一定':
                self.nre = None
                event1, event2 = sample(sorted(EVENTS), 2)
                while EVENTS[event1][:4] == EVENTS[event2][:4]:
                    event1, event2 = sample(sorted(EVENTS), 2)
                self.event_text.set(f'The event of this round is {event1} & {event2}!')
                self.event_meaning_text.set(f'{event1}：{EVENTS[event1]}\n{event2}：{EVENTS[event2]}')
                self.do_event(event1)
                self.do_event(event2)
            else:
                round_event = sample(sorted(EVENTS), 1)[0]
                self.do_event(round_event)
                self.event_text.set(f'The event of this round is {round_event}!')
                self.event_meaning_text.set(f'{round_event}：{EVENTS[round_event]}')
            self.show_pts()
        else:
            self.game_end()

    def do_event(self, event_name):

        if event_name == '绝对优势':
            for s in self.pl:
                self.pts[s] = abs(self.pts[s])
            self.show_pts()
        elif event_name == '精准扶贫':
            add_list = []
            low_pts = float('inf')
            for s in self.pl:
                if self.pts[s] < low_pts:
                    low_pts = self.pts[s]
                    add_list = [s]
                elif self.pts[s] == low_pts:
                    add_list.append(s)
            for s in add_list:
                self.pts[s] += self.pn
            self.show_pts()
        elif event_name in ['福利时间', '风险规避']:
            self.bte = event_name
        elif event_name in ['赢家通吃', '正态分布', '不必犹豫']:
            self.poe = event_name
        elif event_name in ['交通事故', '人气选手', '你先别急']:
            self.ree = event_name
        elif event_name == '下次一定':
            self.nre = event_name

    def song(self):
        new_song = sample(SONGS, counts=WEIGHTS, k=1)[0]
        self.song_text.set(f'The song of this round is {new_song}!')

    def bet(self):
        assert self.crt_step == 'Bet' or self.crt_step == 'Play'
        self.crt_step = 'Play'
        bw = tk.Tk()
        bw.title('Bet Shift')
        bw.geometry('400x100+400+300')

        subject = tk.Frame(bw)
        subject_name = tk.Label(subject, text='Your name: ')
        subject_name.pack(side='left')
        subject_spinbox = tk.Spinbox(subject, values=self.pl, wrap=True, width=20)
        subject_spinbox.pack(side='left')
        subject.pack(side='top')

        object_ = tk.Frame(bw)
        object_name = tk.Label(object_, text='Bet object: ')
        object_name.pack(side='left')
        object_spinbox = tk.Spinbox(object_, values=(self.pl + ['None']), wrap=True, width=20)
        object_spinbox.pack(side='left')
        object_.pack(side='top')

        values = tk.Frame(bw)
        values_name = tk.Label(values, text='Values')
        values_name.pack(side='left')
        values_spinbox = tk.Spinbox(values, values=list(range(1, self.pn + 1)), wrap=True, width=4)
        values_spinbox.pack(side='left')
        values.pack(side='top')

        sure_btn = tk.Button(bw, text='Sure', command=lambda: self.bet_sure(subject_spinbox, object_spinbox, values_spinbox))
        sure_btn.pack(side='top')

        bw.mainloop()

    def bet_sure(self, ss, os, value):
        sp = ss.get()
        op = os.get()
        value = int(value.get())
        assert sp != op
        self.bets[sp] = (op, value)

    def play_end(self):
        assert self.crt_step == 'Play' or self.crt_step == 'Result'
        self.crt_step = 'Result'
        pw = tk.Tk()
        pw.title('Bet Shift')
        pw.geometry('400x100+400+300')

        player = tk.Frame(pw)
        player_name = tk.Label(player, text='Your name: ')
        player_name.pack(side='left')
        player_spinbox = tk.Spinbox(player, values=self.pl, wrap=True, width=20)
        player_spinbox.pack(side='left')
        player.pack(side='top')

        points = tk.Frame(pw)
        points_name = tk.Label(points, text='Your Score: ')
        points_name.pack(side='left')
        points_entry = tk.Entry(points)
        points_entry.pack(side='left')
        points.pack(side='top')

        sure_btn = tk.Button(pw, text='Sure', command=lambda: self.pe_sure(player_spinbox, points_entry))
        sure_btn.pack(side='top')

        pw.mainloop()

    def pe_sure(self, ps, pe):
        player_ = ps.get()
        pnts = float(pe.get())
        self.result[player_] = pnts

    def round_end(self):
        assert self.crt_step == 'Result'
        # play result

        player_list = list(self.pl)
        player_list.sort(key=lambda x: self.result[x], reverse=True)
        if self.poe == '赢家通吃':
            self.pts[player_list[0]] += ceil(self.pn / 2)
            self.report[player_list[0]][0] = ceil(self.pn / 2)
        elif self.poe == '正态分布':
            if self.pn % 2:
                add_list = [min(i, self.pn - i - 1) for i in range(self.pn)]
            else:
                add_list = [min(i + 1, self.pn - i) for i in range(self.pn)]
            for i in range(self.pn):
                self.pts[player_list[i]] += add_list[i]
                self.report[player_list[i]][0] = add_list[i]
        else:
            for i in range(int(self.pn / 2) + 1):
                add_point = max(ceil(self.pn / 2) - i, 0)
                self.pts[player_list[i]] += add_point
                self.report[player_list[i]][0] = add_point

        self.poe = None

        # bet point

        if self.bte != '不必犹豫':
            for v in self.bets.values():
                bet_object_name = v[0]
                if bet_object_name != 'None':
                    self.pts[bet_object_name] -= 1
                    self.report[bet_object_name][1] -= 1

        # Temp point
        highest_point = -float('inf')
        temp_winner = []
        for s in self.pl:
            self.report[s][2] = self.pts[s]
            if self.pts[s] > highest_point:
                highest_point = self.pts[s]
                temp_winner = [s]
            elif self.pts[s] == highest_point:
                temp_winner.append(s)

        # bet result

        if self.bte == '福利时间':
            for k, v in self.bets.items():
                if v[0] in temp_winner:
                    self.report[k][3] += (2 * v[1])
                    self.pts[k] += (2 * v[1])
                elif v[0] != 'None':
                    self.report[k][3] -= (2 * v[1])
                    self.pts[k] -= (2 * v[1])
        elif self.bte == '风险规避':
            for k, v in self.bets.items():
                if v[0] in temp_winner:
                    self.report[k][3] += v[1]
                    self.pts[k] += v[1]
        else:
            for k, v in self.bets.items():
                if v[0] in temp_winner:
                    self.report[k][3] += v[1]
                    self.pts[k] += v[1]
                elif v[0] != 'None':
                    self.report[k][3] -= v[1]
                    self.pts[k] -= v[1]

        self.bte = None

        # Event point

        for v in self.bets.values():
            if v[0] != 'None':
                self.betted_count[v[0]] += 1

        if self.ree == '交通事故':
            for s in self.pl:
                if self.bets[s][0] != 'None':
                    if self.betted_count[self.bets[s][0]] >= 1:
                        self.pts[s] -= (self.betted_count[self.bets[s][0]] - 1)
                        self.report[s][4] -= (self.betted_count[self.bets[s][0]] - 1)

        if self.ree == '人气选手':
            max_player = []
            max_bet = 0
            for s in self.pl:
                if self.betted_count[s] > max_bet:
                    max_player = [s]
                    max_bet = self.betted_count[s]
                elif self.betted_count == max_bet:
                    max_player.append(s)

            for s in max_player:
                self.report[s][4] += (2 * max_bet)
                self.pts[s] += (2 * max_bet)

        if self.ree == '你先别急':
            print(self.pts)
            min_player = []
            min_pts = float('inf')
            for s in self.pl:
                if self.pts[s] < min_pts:
                    min_player = [s]
                    min_pts = self.pts[s]
                elif self.pts[s] == min_pts:
                    min_player.append(s)
            for s in min_player:
                self.report[s][4] += self.pn
                self.pts[s] += self.pn

        self.ree = None

        self.crt_step = 'Event'

        # show point difference

        for s in self.pl:
            self.report[s][5] = self.pts[s]

        ps = tk.Tk()
        ps.title('Points Show')

        text_hint_1 = tk.Label(ps, text=f'Betting Situation: {self.bets}')
        text_hint_1.grid_configure(row=1, column=1, columnspan=7)
        text_hint_2 = tk.Label(ps, text=f'Play Result: {self.result}')
        text_hint_2.grid_configure(row=2, column=1, columnspan=7)

        title = ['Player\nName', 'Play\nResult', 'Betted\nPoint', 'Temp\nPoint', 'Bet\nResult', 'Event\nPoint', 'Total\nPoint']
        for t in range(7):
            sheet = tk.Label(ps, text=title[t])
            sheet.grid_configure(row=3, column=(t + 1))
        for i in range(self.pn):
            name = tk.Label(ps, text=self.pl[i])
            name.grid_configure(row=(i + 4), column=1)
            assert len(self.report[self.pl[0]]) == 6
            for j in range(6):
                sheet = tk.Label(ps, text=self.report[self.pl[i]][j])
                sheet.grid_configure(row=(i + 4), column=(j + 2))

        sure_button = tk.Button(ps, text='Sure', command=ps.destroy)
        sure_button.grid_configure(row=(4 + self.pn), column=4)

        ps.mainloop()

    def game_end(self):
        self.show_pts()


if __name__ == '__main__':
    Start()
