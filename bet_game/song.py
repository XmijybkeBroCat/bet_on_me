from .parser import get_arcaea_info, set_arcaea_quest
from .parser import get_phigros_info, set_phigros_quest
from .utils import GameplayError
import copy

class SongPackageManager:
    def __init__(self):
        self._songs = None
        self._packages = None
        self._difficulties = None

        self._packages_enabled = set()
        self._difficulties_enabled = set()

        self._songs_cache = None
        self._levels_cache = None
        self.set_quest_list = None

    @property
    def available_packages(self):
        return self._packages_enabled

    @property
    def available_difficulties(self):
        return self._difficulties_enabled

    def enable_all_packages(self):
        self._packages_enabled = copy.deepcopy(self._packages)
        self._levels_cache = None
        self._songs_cache = None

    def disable_all_packages(self):
        self._packages_enabled = set()
        self._levels_cache = None
        self._songs_cache = None

    def enable_all_difficulties(self):
        self._difficulties_enabled = copy.deepcopy(self._difficulties)
        self._levels_cache = None
        self._songs_cache = None

    def disable_all_difficulties(self):
        self._difficulties_enabled = set()
        self._levels_cache = None
        self._songs_cache = None

    def enable(self, s:str):
        if s.lower() in self._packages:
            self._packages_enabled.add(s.lower())
        elif s.lower() in self._difficulties:
            self._difficulties_enabled.add(s.lower())
        else:
            raise GameplayError(f'Invalid package or difficulty name {s} to enable')
        self._levels_cache = None
        self._songs_cache = None

    def disable(self, s:str):
        if s.lower() in self._packages:
            self._packages_enabled.remove(s.lower())
        if s.lower() in self._difficulties:
            self._difficulties_enabled.remove(s.lower())
        else:
            raise GameplayError(f'Invalid package or difficulty name {s} to disable')
        self._levels_cache = None
        self._songs_cache = None

    def add_quest_list(self, args:list):
        if not self._levels_cache is None:
            # song cache and level cache are synchronous
            songs = self._songs_cache
            levels = self._levels_cache
        else:
            songs = []
            levels = {}
            for song in self._songs:
                if song['package'] in self._packages_enabled and song['difficulty'] in self._difficulties_enabled:
                    songs.append(song)
                    if song['level'] not in levels.keys():
                        levels[song['level']] = 1.0
            self._levels_cache = levels
            self._songs_cache = songs
        return self.set_quest_list(levels, songs, args)


class ArcaeaSongPackageManager(SongPackageManager):
    def __init__(self):
        super().__init__()
        # package names and difficulty names should be lower
        self._songs, self._packages, self._difficulties = get_arcaea_info()
        self.set_quest_list = set_arcaea_quest


class PhigrosSongPackageManager(SongPackageManager):
    def __init__(self):
        super().__init__()
        # package names and difficulty names should be lower
        self._songs, self._packages, self._difficulties = get_phigros_info()
        self.set_quest_list = set_phigros_quest

    def add_quest_list(self, args:list):
        if not self._levels_cache is None:
            # song cache and level cache are synchronous
            songs = self._songs_cache
            levels = self._levels_cache
        else:
            songs = []
            levels = {}
            for song in self._songs:
                if song['package'] in self._packages_enabled and song['difficulty'] in self._difficulties_enabled:
                    songs.append(song)
                    if int(song['level']) not in levels.keys():
                        levels[int(song['level'])] = 1.0
            self._levels_cache = levels
            self._songs_cache = songs
        return self.set_quest_list(levels, songs, args)