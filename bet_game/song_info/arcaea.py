import os as _os
import json as _json
import re as _re

from .. import utils as _utils 
from ..quest import ArcaeaQuestInfo as _ArcaeaQuestInfo

def get_arcaea_info():
    _song_package_file = _os.path.dirname(_os.path.abspath(__file__)) + _os.path.sep + 'arcaea_songlist'
    with open(_song_package_file, 'r', encoding='utf8') as f:
        _song_package_raw = _json.load(f)
        _song_package = {}
        for _song in _song_package_raw['songs']:
            _package = _song['set']
            _package_list = _song_package.setdefault(_package, {})
            _base_info = {
                'id': _song['id'],
                'name': _song['title_localized']['en'],
                'artist': _song['artist'],
                'package': _package,
            }
            for _dif in _song['difficulties']:
                _difficulty = _dif['ratingClass']
                _level = _dif['rating'] + (0.7 if _dif.get('ratingPlus', False) else 0.0)
                _diff_list = _package_list.setdefault(_level, [])
                _dif_info = {
                    **_base_info,
                    'level': _level,
                    'difficulty': _difficulty
                }
                if 'title_localized' in _dif:
                    _dif_info['name'] = _dif['title_localized']['en']
                _diff_list.append(_dif_info)
    return _song_package
    

def arcaea_level(value : str):
    if _re.match(r'^[0-9]+(?:\.[0-9]+)?$', value):
        level = float(value)
    elif _re.match(r'^[0-9]+\+$', value):
        level = float(value[:-1]) + 0.7
    else:
        level = None
    return level


def set_arcaea_quest(levels, args:list):
    level_weights = {k : 1.0 for k in levels.keys()}
    difficulty_enabled = [True, True, True, True]
    ban_song_id = set()
    for i in range(0, len(args), 2):
        arg1, arg2 = args[i], args[i + 1]
        mode = 0
        if isinstance(arg1, int) or isinstance(arg1, float):
            mode = 1
            arg1 = float(arg1)
        elif isinstance(arg1, str):
            _level = arcaea_level(arg1)
            if _level:
                arg1 = _level
                mode = 1
            else:
                difficulties = {'pst': 0, 'prs': 1, 'ftr': 2, 'byd': 3}
                _arg1 = arg1.lower()
                if _arg1 in difficulties:
                    mode = 2
                    arg1 = _arg1
                elif _arg1 == 'ban':
                    mode = 3

        if mode == 1:
            level, weight = arg1, arg2
            if not isinstance(weight, int) and not isinstance(weight, float):
                raise _utils.SettingsError(f'Invalid weight: {weight}')
            weight = max(weight, 0)
            level_weights[level] = weight
        elif mode == 2:
            difficulties = {'pst': 0, 'prs': 1, 'ftr': 2, 'byd': 3}
            difficulty_enabled[difficulties[arg1]] = bool(arg2)
        elif mode == 3:
            ban_song_id.add(arg2)
        quests = []
        for level, songs in levels.items():
            songs = list(filter(lambda x: difficulty_enabled[x['difficulty']] and not x['id'] in ban_song_id, songs))
            for song in songs:
                quest = _ArcaeaQuestInfo(song, weight=level_weights[level] / len(songs))
                quests.append(quest)
        return quests
