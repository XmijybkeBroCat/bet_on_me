from .parser import get_arcaea_info, set_arcaea_quest
from .parser import get_phigros_info, set_phigros_quest
from .utils import GameplayError
import copy

class SongPackageManager:
    def __init__(self):
        self._songs = None
        self._packages = None
        self._difficulties = None

        self.__songs_available = []
        self.__packages_enabled = set()
        self.__difficulties_enabled = set()

        self.__songs_cache = None
        self.__levels_cache = None
        self.set_quest_list = None

    @property
    def available_packages(self):
        return self.__packages_enabled

    @property
    def available_difficulties(self):
        return self.__difficulties_enabled

    def enable_all_packages(self):
        self.__packages_enabled = copy.deepcopy(self._packages)
        self.__levels_cache = None
        self.__songs_cache = None

    def disable_all_packages(self):
        self.__packages_enabled = set()
        self.__levels_cache = None
        self.__songs_cache = None

    def enable_all_difficulties(self):
        self.__difficulties_enabled = copy.deepcopy(self._difficulties)
        self.__levels_cache = None
        self.__songs_cache = None

    def disable_all_difficulties(self):
        self.__difficulties_enabled = set()
        self.__levels_cache = None
        self.__songs_cache = None

    def enable(self, s:str):
        if s in self._packages:
            self.__packages_enabled.add(s)
        elif s in self._difficulties:
            self.__difficulties_enabled.add(s)
        else:
            raise GameplayError(f'Invalid package or difficulty name {s} to enable')
        self.__levels_cache = None
        self.__songs_cache = None

    def disable(self, s:str):
        if s in self._packages:
            self.__packages_enabled.remove(s)
        elif s in self._difficulties:
            self.__difficulties_enabled.remove(s)
        else:
            raise GameplayError(f'Invalid package or difficulty name {s} to disable')
        self.__levels_cache = None
        self.__songs_cache = None

    def add_quest_list(self, args:list):
        if not self.__levels_cache is None:
            # song cache and level cache are synchronous
            songs = self.__songs_cache
            levels = self.__levels_cache
        else:
            songs = []
            levels = {}
            for song in self._songs:
                if song['package'] in self.__packages_enabled and song['difficulty'] in self.__difficulties_enabled:
                    songs.append(song)
                    if song['level'] not in levels.keys():
                        levels[song['level']] = 1.0
            self.__levels_cache = levels
            self.__songs_cache = songs
        return self.set_quest_list(levels, songs, args)


class ArcaeaSongPackageManager(SongPackageManager):
    def __init__(self):
        super().__init__()
        self._songs, self._packages, self._difficulties = get_arcaea_info()
        self.set_quest_list = set_arcaea_quest


class PhigrosSongPackageManager(SongPackageManager):
    def __init__(self):
        super().__init__()
        self._songs, self._packages, self._difficulties = get_phigros_info()
        self.set_quest_list = set_phigros_quest