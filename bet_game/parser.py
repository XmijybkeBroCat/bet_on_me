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
        _difficulty_list = ['pst', 'prs', 'ftr', 'byd']
        for _song in _song_info_raw['songs']:
            _base_info = {
                'id': _song['id'],
                'name': _song['title_localized']['en'],
                'artist': _song['artist'],
                'package': _song['set'].lower(),
            }
            for _dif in _song['difficulties']:
                _level = _dif['rating'] + (0.7 if _dif.get('ratingPlus', False) else 0.0)
                _dif_info = {
                    **_base_info,
                    'level': _level,
                    'difficulty': _difficulty_list[_dif['ratingClass']]
                }
                if 'title_localized' in _dif:
                    _dif_info['name'] = _dif['title_localized']['en']
                _song_info.append(_dif_info)
            _package_info.add(_song['set'].lower())
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


def set_arcaea_quest(level_weights:dict, songs:list, args:list):
    ban_song_id = set()
    for i in range(0, len(args), 2):
        _arg1, _arg2 = args[i], args[i+1]
        if isinstance(_arg2, float) or isinstance(_arg2, int):
            # set weight
            level_weights[arcaea_level(_arg1)] = max(float(_arg2), 0)
            if level_weights[arcaea_level(_arg1)] == 0.0:
                del(level_weights[arcaea_level(_arg1)])
        elif isinstance(_arg2, str):
            # ban song
            if _arg1 != "ban":
                raise ParseError(f'Invalid args: {_arg1}, {_arg2}')
            ban_song_id.add(_arg2)
        else:
            raise ParseError(f'Invalid args: {_arg1}, {_arg2}')

    quests = []
    for song in songs:
        if song['id'] not in ban_song_id and song['level'] in level_weights.keys():
            quests.append(ArcaeaQuestInfo(song=song, weight=level_weights[song['level']]))
    return quests

# phigros
def get_phigros_info():
    _song_info_file = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + '/song_info/phigros_songlist'
    with open(_song_info_file, 'r', encoding='utf8') as f:
        _song_info_raw = json.load(f)
        _song_info = []
        _package_info = set()
        diffname_list = ['EZ', 'HD', 'IN', 'AT']
        for _song in _song_info_raw:
            _base_info = {
                'id': "",
                'name': _song['Title'],
                'artist': _song['Artist'],
                'package': _song['Pack'].lower(),
            }
            for diff_num in range(4):
                _level = phigros_diff_split(_song[diffname_list[diff_num]])
                if _level:
                    _dif_info = {
                        **_base_info,
                        'difficulty': diffname_list[diff_num].lower(),
                        'level': float(_level)
                    }
                    _song_info.append(_dif_info)
            _package_info.add(_song['Pack'].lower())
        return _song_info, _package_info, set(('ez', 'hd', 'in', 'at'))


def phigros_diff_split(diff_str):
    if re.search(r'[0-9]+\s*\([0-9]+\.[0-9]+\)', diff_str):
        _, detailed = re.findall(r'(?P<rough>[0-9]+)\s*\((?P<detailed>[0-9]+\.[0-9]+)\)', diff_str)[0]
        return float(detailed)
    else:
        return None


def set_phigros_quest(level_weights:dict, songs:list, args:list):
    ban_song_id = set()
    for i in range(0, len(args), 2):
        _arg1, _arg2 = args[i], args[i+1]
        if isinstance(_arg2, float) or isinstance(_arg2, int):
            # set weight (only support integer level)
            try:
                level_weights[int(float(_arg1))] = max(float(_arg2), 0)
                if level_weights[int(float(_arg1))] == 0.0:
                    del(level_weights[int(float(_arg1))])
            except ValueError:
                print(f'{_arg1} is not a valid level!')
        elif isinstance(_arg2, str):
            # ban song
            if _arg1 != "ban":
                raise ParseError(f'Invalid args: {_arg1}, {_arg2}')
            ban_song_id.add(_arg2)
        else:
            raise ParseError(f'Invalid args: {_arg1}, {_arg2}')

    quests = []
    for song in songs:
        if song['id'] not in ban_song_id and int(song['level']) in level_weights.keys():
            quests.append(PhigrosQuestInfo(song=song, weight=level_weights[int(song['level'])]))
    return quests
