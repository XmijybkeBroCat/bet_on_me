from .utils import GameplayError
import numpy as _np

class QuestInfo:
    def __init__(
        self,
        weight : float = 1.0,
        description : str = ''
    ):
        self.weight = weight
        self.description = description

    def __str__(self):
        return self.description

    def __eq__(self, other):
        return self.description == other.description


class ArcaeaQuestInfo(QuestInfo):
    def __init__ (
        self,
        weight: float,
        song: dict,
    ):
        level = song['level']
        level_name = str(int(level))
        if level - int(level) > 0:
            level_name += '+'
        difficulty_full = {'pst':'Past', 'pre':'Present', 'ftr':'Future', 'byd':'Beyond'}
        difficulty_name = difficulty_full[song['difficulty']]

        song_name = song['name']
        artist_name = song['artist']

        self.weight = weight
        self.description = f'{song_name} ({artist_name}) [{difficulty_name} {level_name}]'


class PhigrosQuestInfo(QuestInfo):
    def __init__ (
        self,
        weight: float,
        song: dict,
    ):
        level = song['level']
        level_name = str(int(level))

        difficulty_name = song['difficulty'].upper()

        song_name = song['name']
        artist_name = song['artist']
        self.weight = weight
        self.description = f'{song_name} ({artist_name}) [{difficulty_name} {level_name}]'


class QuestPool:
    def __init__(self, quest_list=None):
        if (quest_list):
            self.__quest_list = quest_list
        else:
            self.__quest_list = []
        self.__p_cache = None

    def set_quest_list(self, quest_list):
        self.__quest_list = quest_list

    def add_quest(self, quest:QuestInfo):
        self.__quest_list.append(quest)
        self.__p_cache = None

    def remove_quest(self, quest:QuestInfo):
        self.__quest_list.remove(quest)
        self.__p_cache = None

    def draw_quest(self):
        if not self.__p_cache is None:
            p = self.__p_cache
        else:
            weights = _np.array([q.weight for q in self.__quest_list])
            total_pool_size = len(self.__quest_list)
            if (total_pool_size == 0):
                raise GameplayError("No Quest In The Quest Pool!")
            total_weights = weights.sum()
            p = weights / total_weights
            self.__p_cache = p
        indexes = _np.arange(0, len(p), dtype=_np.int_)
        rolled = _np.random.choice(indexes, 1, replace=False, p=p).item()
        current_quest = self.__quest_list[rolled]
        return current_quest
