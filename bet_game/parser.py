import os
import json
import re

from .utils import ParseError
from .quest import ArcaeaQuestInfo, PhigrosQuestInfo

def get_arcaea_info():
    _song_info_file = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + '/song_info/arcaea_songlist'
    with open(_song_info_file, 'r', encoding='utf8') as f:
        _song_info_raw = json.load(f)
        _song_info = []
        _package_info = set()
        _difficulty_dict = {0:'pst', 1:'prs', 2:'ftr', 3:'byd'}
        for _song in _song_info_raw['songs']:
            _package = _song['set']
            _base_info = {
                'id': _song['id'],
                'name': _song['title_localized']['en'],
                'artist': _song['artist'],
                'package': _package,
            }
            for _dif in _song['difficulties']:
                _difficulty = _difficulty_dict[_dif['ratingClass']]
                _level = _dif['rating'] + (0.7 if _dif.get('ratingPlus', False) else 0.0)
                _dif_info = {
                    **_base_info,
                    'level': _level,
                    'difficulty': _difficulty
                }
                if 'title_localized' in _dif:
                    _dif_info['name'] = _dif['title_localized']['en']
                _song_info.append(_dif_info)

            _package_info.add(_package)
            
    return _song_info, _package_info, set(('pst', 'prs', 'ftr', 'byd'))
    

def arcaea_level(value):
    if isinstance(value, float):
        return value
    elif isinstance(value, int):
        return float(value)
    elif isinstance(value, str):
        if re.match(r'^[0-9]+(?:\.[0-9]+)?$', value):
            level = float(value)
        elif re.match(r'^[0-9]+\+$', value):
            level = float(value[:-1]) + 0.7
        else:
            level = None
        return level
    else:
        raise ParseError(f'Invalid arcaea level: {value}')


def set_arcaea_quest(level_weights:dict, songs:dict, args:list):
    ban_song_id = set()
    
    for i in range(0, len(args), 2):
        _arg1, _arg2 = args[i], args[i+1]
        if isinstance(_arg2, float):
            # set weight
            level_weights[arcaea_level(_arg1)] = max(_arg2, 0)
        elif isinstance(_arg2, str):
            # ban song
            if _arg1 != "ban":
                raise ParseError(f'Invalid args: {_arg1}, {_arg2}')
            ban_song_id.add(_arg2)
        else:
            raise ParseError(f'Invalid args: {_arg1}, {_arg2}')

    quests = []
    for song in songs:
        if song['id'] not in ban_song_id:
            quests.append(ArcaeaQuestInfo(song=song, weight=level_weights[song['level']]))
    return quests

# phigros
def get_phigros_info():
    _song_info_file = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + '/song_info/phigros_songlist'
    with open(_song_info_file, 'r', encoding='utf8') as f:
        _song_info_raw = json.load(f)
        _song_info = {}
        diffname_list = ['EZ', 'HD', 'IN', 'AT']
        for _song in _song_info_raw:
            _package = _song['Pack']
            _package_list = _song_info.setdefault(_package, {})
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
    if re.search(r'[0-9]+\s*\([0-9]+\.[0-9]+\)', diff_str):
        rough, detailed = re.findall(r'(?P<rough>[0-9]+)\s*\((?P<detailed>[0-9]+\.[0-9]+)\)', diff_str)[0]
        return int(rough), float(detailed)
    else:
        return 0, 0


def phigros_level(value : str):
    if re.match(r'^[0-9]+(?:\.[0-9]+)?$', value):
        level = float(value)
        detailed = 1
    elif re.match(r'^[0-9]+$', value):
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
            _level, _ = phigros_level(arg1)
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
                raise ParseError(f'Invalid weight: {weight}')
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
            quest = PhigrosQuestInfo(song, weight=level_weights[level] / len(songs))
            quests.append(quest)
    return quests
