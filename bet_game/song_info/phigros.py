import os as _os
import json as _json
import re as _re

from .. import utils as _utils
from ..quest import PhigrosQuestInfo as _PhigrosQuestInfo

def get_phigros_info():
    _song_package_file = _os.path.dirname(_os.path.abspath(__file__)) + _os.path.sep + 'phigros_songlist'
    with open(_song_package_file, 'r', encoding='utf8') as f:
        _song_package_raw = _json.load(f)
        _song_package = {}
        diffname_list = ['EZ', 'HD', 'IN', 'AT']
        for _song in _song_package_raw:
            _package = _song['Pack']
            _package_list = _song_package.setdefault(_package, {})
            _base_info = {
                'id': "",
                'name': _song['Title'],
                'artist': _song['Artist'],
                'package': _package,
            }
            for diff_num in range(4):
                _level, _level_detailed = phigros_diff_split(_song[diffname_list[diff_num]])
                _diff_list = _package_list.setdefault(_level, [])
                if _level:
                    _dif_info = {
                        **_base_info,
                        'difficulty': diff_num,
                        'level': _level_detailed
                    }
                    _diff_list.append(_dif_info)


def phigros_diff_split(diff_str):
    if _re.search(r'[0-9]+\s*\([0-9]+\.[0-9]+\)', diff_str):
        rough, detailed = _re.findall(r'(?P<rough>[0-9]+)\s*\((?P<detailed>[0-9]+\.[0-9]+)\)', diff_str)[0]
        return int(rough), float(detailed)
    else:
        return 0, 0


def phigros_level(value : str):
    if _re.match(r'^[0-9]+(?:\.[0-9]+)?$', value):
        level = float(value)
        detailed = 1
    elif _re.match(r'^[0-9]+$', value):
        level = float(value)
        detailed = 0
    else:
        level = None
        detailed = None
    return level, detailed


def set_phigros_quest(levels, args:list):
    level_weights = {k : 0.0 for k in levels.keys()}
    difficulty_enabled = [True, True, True, True]
    ban_song_id = set()
    for i in range(0, len(args), 2):
        arg1, arg2 = args[i], args[i + 1]
        mode = 0
        if isinstance(arg1, int) or isinstance(arg1, float):
            mode = 1
            arg1 = float(arg1)
        elif isinstance(arg1, str):
            _level, _detailed = phigros_level(arg1)
            if _level:
                arg1 = _level
                mode = 1
            else:
                difficulties = {'EZ': 0, 'HD': 1, 'IN': 2, 'AT': 3}
                _arg1 = arg1.upper()
                if _arg1 in difficulties:
                    mode = 2
                    arg1 = _arg1
                elif _arg1 == 'BAN':
                    mode = 3

        if mode == 1:
            level, weight = arg1, arg2
            if not isinstance(weight, int) and not isinstance(weight, float):
                raise _utils.SettingsError(f'Invalid weight: {weight}')
            weight = max(weight, 0)
            level_weights[level] = weight
        elif mode == 2:
            difficulties = {'EZ': 0, 'HD': 1, 'IN': 2, 'AT': 3}
            difficulty_enabled[difficulties[arg1]] = bool(arg2)
        elif mode == 3:
            ban_song_id.add(arg2)
    quests = []
    for level, songs in levels.items():
        songs = list(filter(lambda x: difficulty_enabled[x['difficulty']] and not x['id'] in ban_song_id, songs))
        for song in songs:
            quest = _PhigrosQuestInfo(song, weight=level_weights[level] / len(songs))
            quests.append(quest)
    return quests
